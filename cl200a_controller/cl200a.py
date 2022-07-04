from datetime import datetime
from pathlib import Path
from typing import Tuple

from serial import PARITY_EVEN, SEVENBITS, SerialException

from cl200a_controller.cl200a_utils import CL200Utils
from cl200a_controller.logger import Logger
from cl200a_controller.serial_utils import SerialUtils


class CL200A:
    """
    Konica Minolta (CL-200A)
    All documentation can be found:
    http://www.konicaminolta.com.cn/instruments/download/software/pdf/CL-200A_communication_specifications.pdf
    this code is developed based on:
    https://github.com/maslyankov/luxmeters-py
    """

    def __init__(
        self,
        log_file_path: Path = Path("./cl200a_controller.log"),
        debug: bool = False,
    ) -> None:
        """__init__

        Args:
            log_file_path: (Union[Path, None], optional): log file path. Defaults to None.
            skip_check (bool, optional):
            Check whether the response from the CL-200A is correct. Defaults to True.
            debug (bool, optional): _description_. Defaults to False.

        Raises:
            exc: SerialException when the CL-200A is not found.
            err: SerialException when the CL-200A is not found.
        """
        self.log_file_path = log_file_path

        self.logger = Logger.logger(show_debug_message=debug, log_file_path=log_file_path)

        self.cmd_dict = CL200Utils.cl200a_cmd_dict

        try:
            self.port = SerialUtils.find_all_luxmeters("FTDI")[0]
        except SerialException as exc:
            self.logger.error("Error: Serial port not found")
            raise exc

        try:
            self.ser = CL200Utils.connect_serial_port(
                self.port, parity=PARITY_EVEN, bytesize=SEVENBITS
            )
        except SerialException as exc:
            self.logger.error("Error: Could not connect to Lux Meter")
            raise exc

        self.is_connected: bool = False
        self._connection()
        self._hold_mode()
        self._ext_mode()

    def _connection(self) -> None:
        """__connection
        Switch the CL-200A to PC connection mode. (Command "54").
        In order to perform communication with a PC,
        this command must be used to set the CL-200A to PC connection mode.

        Raises:
            SerialException: when the CL-200A has an error.
        """

        self.logger.info("Setting CL-200A to PC connection mode")
        try:
            CL200Utils.connect_luxmeter(ser=self.ser)
            self.is_connected = True

        except SerialException as exc:
            raise exc

    def _hold_mode(self) -> None:
        """__hold_mode (internal use)
        Sets the CL-200A to Hold status. (command 55)
        """

        cmd = CL200Utils.cmd_formatter(self.cmd_dict["command_55"])
        # Hold status
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        try:
            CL200Utils.write_serial_port(ser=self.ser, cmd=cmd, sleep_time=0.5)
        except SerialException as exc:
            raise exc

    def _ext_mode(self) -> None:
        """__ext_mode (internal use)
        Set the Lux meter into EXT mode. (command 40)
        Sets the CL-200A to the mode for controlling measurements from the PC,
        and takes measurements.

        EXT mode can not be performed unless the CL-200A set to Hold mode.

        Raises:
            ConnectionError: _description_
        """
        cmd = CL200Utils.cmd_formatter(self.cmd_dict["command_40"])
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()

        for _ in range(2):
            # set CL-200A to EXT mode
            try:
                CL200Utils.write_serial_port(ser=self.ser, cmd=cmd, sleep_time=0.125)
            except SerialException as exc:
                raise exc
            ext_mode_err = self.ser.readline().decode("ascii")
            # If an error occurred when setting EXT mode (ERR byte = "4"),
            # hold_mode was not completed
            # correctly. Repeat hold_mode and then set EXT mode again.
            if ext_mode_err[6:7] == "4":
                self._hold_mode()
                continue

            if ext_mode_err[6:7] in ["1", "2", "3"]:
                self.logger.error("Set hold mode error")
                err = "Switch off the CL-200A and then switch it back on"
                self.logger.info(err)
                raise ConnectionError(err)

            break

    def _perform_measurement(self, read_cmd: str) -> Tuple[str, datetime]:
        """_perform_measurement (internal use)

        Args:
            read_cmd (str): command to send to the CL-200A

        Raises:
            SerialException: when no data received from CL-200A
            ConnectionAbortedError: when the connection to Luxmeter was lost.

        Returns:
            str: result from the CL-200A
            datetime: time of measurement
        """

        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()

        # Perform measurement
        cmd_ext = CL200Utils.cmd_formatter(self.cmd_dict["command_40r"])
        cmd_read = CL200Utils.cmd_formatter(read_cmd)
        CL200Utils.write_serial_port(ser=self.ser, cmd=cmd_ext, sleep_time=0.5)
        # read data
        CL200Utils.write_serial_port(ser=self.ser, cmd=cmd_read, sleep_time=0)
        measured_time = datetime.now()
        try:
            serial_ret = self.ser.readline()
            if len(serial_ret) == 0:
                raise SerialException("No data received from CL-200A")

            result = serial_ret.decode("ascii")
        except SerialException as exc:
            raise ConnectionAbortedError("Connection to Luxmeter was lost.") from exc

        CL200Utils.check_measurement(result)

        self.logger.debug(f"Got raw data: {result.rstrip()}")

        return result, measured_time

    # pylint: disable=invalid-name
    # the names ev, y, z are used in the documentation
    def get_ev_x_y(self) -> Tuple[float, float, float, datetime]:
        """get_ev_x_y
        read the most recent measurement data from the CL-200A to the PC in terms of Ev, x, y
        (command 02)

        Raises:
            ValueError: returned value from luxmeter is not valid

        Returns:
            float: measured value
        """

        result, measured_time = self._perform_measurement(self.cmd_dict["command_02"])
        # Convert Measurement
        ev, x, y = CL200Utils.extract_ev_x_y(result)

        self.logger.debug(f"Returning {ev} luxes, x: {x}, y: {y}")

        return ev, x, y, measured_time

    # pylint: disable=invalid-name
    # the names x, y, z are used in the documentation
    def get_x_y_z(self) -> Tuple[float, float, float, datetime]:
        """get_x_y_z
        read the most recent measurement data from the CL-200A to the PC in terms of X, Y, Z.
        (command 01)

        Raises:
            ValueError: returned value from luxmeter is not valid

        Returns:
            float: measured value
        """
        result, measured_time = self._perform_measurement(self.cmd_dict["command_01"])
        x, y, z = CL200Utils.extract_x_y_z(result)

        self.logger.debug(f"X: {x}, Y: {y}, Z: {z}")

        return x, y, z, measured_time

    # pylint: disable=invalid-name
    # the names ev, u, v are used in the documentation
    def get_ev_u_v(self) -> Tuple[float, float, float, datetime]:
        """get_ev_tcp_delta_uv
        To read the most recent measurement data from the CL-200A to the PC in terms of Ev, u', v'.
        (command 03)

        Raises:
            ValueError: returned value from luxmeter is not valid

        Returns:
            float: measured value
        """
        result, measured_time = self._perform_measurement(self.cmd_dict["command_03"])
        ev, u, v = CL200Utils.extract_ev_u_v(result)

        self.logger.debug(f"Illuminance: {ev} lux, u: {u}, v: {v}")

        return ev, u, v, measured_time

    # pylint: disable=invalid-name
    # the names ev, tcp, delta_uv are used in the documentation
    def get_ev_tcp_delta_uv(self) -> Tuple[float, float, float, datetime]:
        """get_ev_tcp_delta_uv
        To read the most recent measurement data
        from the CL-200A to the PC in terms of EV, TCP, Δuv.
        (command 08)

        Raises:
            ValueError: returned value from luxmeter is not valid

        Returns:
            float: measured value
        """
        result, measured_time = self._perform_measurement(self.cmd_dict["command_08"])
        ev, tcp, delta_uv = CL200Utils.extract_ev_tcp_delta_uv(result)

        self.logger.debug(f"Illuminance: {ev} lux, TCP: {tcp}, DeltaUV: {delta_uv}")

        return ev, tcp, delta_uv, measured_time
