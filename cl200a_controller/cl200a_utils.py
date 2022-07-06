"""
       Command type                              Command
 Read measurement data (X, Y, Z)                   01
 Read measurement data (EV, x, y)                  02
 Read measurement data (EV, u', v')                03
 Read measurement data (EV, TCP, Δuv)              08
 Read measurement data (EV, DW, P)                 15
 Set EXT mode; Take measurements                   40
 Read measurement data (X2, Y, Z) *                45
 Read coefficients for user calibration *          47
 Set coefficients for user calibration *           48
 Set PC connection mode                            54
 Set Hold status                                   55
"""

from time import sleep
from typing import List, Tuple, Union

from serial import EIGHTBITS, PARITY_NONE, STOPBITS_ONE, Serial, SerialException


class MeasurementValueOverError(BaseException):
    pass


class LowLuminanceError(BaseException):
    pass


class LowBatteryError(BaseException):
    pass


class ValueOutOfRangeError(BaseException):
    pass


class CL200Utils:
    skip_connection_check = False

    cl200a_cmd_dict = {
        "command_01": "00011200",
        "command_02": "00021200",
        "command_03": "00031200",
        "command_08": "00081200",
        "command_15": "00151200",
        "command_40": "004010  ",
        "command_40r": "994021  ",
        "command_45": "00451000",
        "command_47a": "004711",
        "command_47b": "004721",
        "command_47c": "004731",
        "command_48a": "004811  ",
        "command_48b": "004821  ",
        "command_48c": "004831  ",
        "command_54": "00541   ",
        "command_54r": "0054    ",
        "command_55": "99551  0",
    }

    @classmethod
    def connect_luxmeter(cls, ser: Serial) -> bool:
        """connect_luxmeter
        Switch the CL-200A to PC connection mode. (Command "54").
        In order to perform communication with a PC,
        this command must be used to set the CL-200A to PC connection mode.

        Args:
            ser (Serial): serial object

        Raises:
            SerialException: when the CL-200A has an error.

        Returns:
            bool: True if success, False if fail.
        """
        cmd_request: str = chr(2) + "00541   " + chr(3) + "13\r\n"
        is_connected: bool = True

        for _ in range(2):
            cls.write_serial_port(ser=ser, cmd=cmd_request, sleep_time=0.5)
            try:
                _ = ser.readline().decode("ascii")
            except SerialException:
                is_connected = False

                return is_connected

            ser.flushInput()
            ser.flushOutput()

            if is_connected:
                break

        return is_connected

    @classmethod
    def connect_serial_port(
        cls,
        port: str,
        baudrate: int = 9600,
        parity: str = PARITY_NONE,
        stopbits: float = STOPBITS_ONE,
        bytesize: int = EIGHTBITS,
        timeout: float = 3,
    ) -> Serial:
        """connect_serial_port
        Perform serial connection

        Args:
            port (str): containing the COM port.
            baudrate (int, optional): Baudrate. Defaults to 9600.
            parity (str, optional): Parity bit. Defaults to PARITY_NONE.
            stopbits (float, optional): Stop Bit. Defaults to STOPBITS_ONE.
            bytesize (int, optional): Byte size. Defaults to EIGHTBITS.
            timeout (float, optional): Timeout to perform the connection.. Defaults to 3.

        Returns:
            Serial: connected serial port
        """
        ser = Serial(
            port=port,
            baudrate=baudrate,
            parity=parity,
            stopbits=stopbits,
            bytesize=bytesize,
            timeout=timeout,
        )
        cls._clean_obj_port(obj_port=ser)
        return ser

    @classmethod
    def cmd_formatter(cls, cmd: str) -> str:
        """cmd_formatter
        Given a command, verify XOR ( Or Exclusive) byte per byte.

        Args:
            cmd (str): String with a serial command.

        Returns:
            str: Ascii with the entire command converted.
        """
        j = 0x0
        stx = chr(2)
        etx = chr(3)
        delimiter = "\r\n"
        to_hex = [hex(ord(c)) for c in cmd + etx]
        for i in to_hex:
            j ^= int(i, base=16)
        bcc = str(j).zfill(2)
        return stx + cmd + etx + bcc + delimiter

    @classmethod
    def write_serial_port(cls, ser: Serial, cmd: str, sleep_time: float) -> None:
        """write_serial_port
        Writes into the serial port.

        Args:
            ser (Serial): Serial object
            cmd (str): String containing the command
            sleep_time (float): sleep time after write command.
        """
        try:
            ser.write(cmd.encode())
        except SerialException as exc:
            raise exc

        sleep(sleep_time)
        ser.reset_input_buffer()

    @classmethod
    def check_measurement(cls, result: str) -> None:
        """check_measurement _summary_

        Args:
            result (str): returned str data from the Luxmeter

        Raises:
            ConnectionResetError: raise if the CL200A must be reset.
            LowBatteryError: raise when the battery is low.
            LowLuminanceError: raise when the luminance is low.
        """
        if result[6] in ["1", "2", "3"]:
            err = "Switch off the CL-200A and then switch it back on"
            raise ConnectionResetError(err)

        if result[6] == "5":
            err = (
                "Measurement value over error. "
                + "The measurement exceed the CL-200A measurement range."
            )
            raise MeasurementValueOverError(err)
        if result[6] == "6":
            err = (
                "Low luminance error. Luminance is low, resulting in reduced calculation accuracy "
                "for determining chromaticity"
            )
            raise LowLuminanceError(err)
        if result[6] == "7":
            err = "The TCP, Δuv measured values are out of range"
            raise ValueOutOfRangeError(err)

        # if result[7] == '6':
        #     err= 'Switch off the CL-200A and then switch it back on'
        #     raise Exception(err)
        if result[8] == "1":
            err = (
                "Low battery\n"
                + "The battery should be changed immediately or the AC adapter should be used. "
                + "Also, if this error occurs, "
                + "the measurement values should not be used "
                + "as the values for the most recent measurement"
            )
            raise LowBatteryError(err)

    @classmethod
    def _extract_one_data_from_result(cls, result: str, start_index: int) -> float:
        """extract_one_data_from_result
        extract one data from the result string based on the data format.

        Args:
            result (str): returned str data from the Luxmeter
            start_index (int): index when to start extracting the data.

        Returns:
            float: extracted value
        """
        if result[start_index] == "+":
            signal = 1
        else:
            signal = -1
        value_num = float(result[start_index + 1 : start_index + 1 + 4])
        value_exp = float(result[start_index + 1 + 4]) - 4

        value = round(float(signal * value_num * (10**value_exp)), 3)
        return value

    @classmethod
    def _extract_three_data_from_result(cls, result: str) -> Tuple[float, float, float]:
        """extract_three_data_from_result
        extract all of the data from the result string based on the data format.

        Args:
            result (str): returned str data from the Luxmeter

        Returns:
            Tuple[float, float, float]: extracted values
        """
        value1 = cls._extract_one_data_from_result(result, start_index=9)
        value2 = cls._extract_one_data_from_result(result, start_index=15)
        value3 = cls._extract_one_data_from_result(result, start_index=21)
        return value1, value2, value3

    # pylint: disable=invalid-name
    # the names ev, x, y are used in the documentation
    @classmethod
    def extract_ev_x_y(cls, result: str) -> Tuple[float, float, float]:
        """extract_ev_x_y _summary_

        Args:
            result (str): returned str data from the Luxmeter
            cmd_name (str): command name to check
            if the command is correct for the extraction sequence.

        Raises:
            ValueError: raise if the command is not correct for the extraction sequence.

        Returns:
            Tuple[float, float, float]: _description_
        """
        cls._check_command_num(result=result, command_num="02")
        ev, x, y = cls._extract_three_data_from_result(result)
        return ev, x, y

    # pylint: disable=invalid-name
    # the names x, y, z are used in the documentation
    @classmethod
    def extract_x_y_z(cls, result: str) -> Tuple[float, float, float]:
        """extract_xyz _summary_

        Args:
            result (str): returned str data from the Luxmeter
            cmd_name (str): command name to check
            if the command is correct for the extraction sequence.

        Raises:
            ValueError: raise if the command is not correct for the extraction sequence.

        Returns:
            Tuple[float, float, float]: _description_
        """
        cls._check_command_num(result=result, command_num="01")
        x, y, z = cls._extract_three_data_from_result(result)
        return x, y, z

    # pylint: disable=invalid-name
    # the names ev, u, v are used in the documentation
    @classmethod
    def extract_ev_u_v(cls, result: str) -> Tuple[float, float, float]:
        """extract_ev_u_v _summary_

        Args:
            result (str): returned str data from the Luxmeter
            cmd_name (str): command name to check
            if the command is correct for the extraction sequence.

        Raises:
            ValueError: raise if the command is not correct for the extraction sequence.

        Returns:
            Tuple[float, float, float]: _description_
        """
        cls._check_command_num(result=result, command_num="03")
        ev, u, v = cls._extract_three_data_from_result(result)
        return ev, u, v

    # pylint: disable=invalid-name
    # the names ev, tcp, delta_uv are used in the documentation
    @classmethod
    def extract_ev_tcp_delta_uv(cls, result: str) -> Tuple[float, float, float]:
        """extract_ev_tcp_delta_uv

        Args:
            result (str): returned str data from the Luxmeter
            if the command is correct for the extraction sequence.

        Raises:
            ValueError: raise if the command is not correct for the extraction sequence.

        Returns:
            Tuple[float, float, float]: _description_
        """
        cls._check_command_num(result=result, command_num="08")
        ev, tcp, delta_uv = cls._extract_three_data_from_result(result)
        return ev, tcp, delta_uv

    @classmethod
    def _check_command_num(cls, result: str, command_num: Union[str, List[str]]):
        """_check_command_num
        check the command num in the result is correct.

        Args:
            result (str): returned str data from the Luxmeter
            command_num (Union[str, List[str]]): command num to check

        Raises:
            ValueError: raise if the command num is not correct.
        """
        result_num = str(result[3:5])
        if isinstance(command_num, list):
            if result_num not in command_num:
                raise ValueError("Invalid command number")
        else:
            if result_num != command_num:
                raise ValueError("Invalid command number")

    @classmethod
    def _clean_obj_port(cls, obj_port: Serial) -> None:
        """_clean_obj_port
        Perform object buffer cleaning

        Args:
            obj_port (Serial): target serial port object
        """

        obj_port.close()
        if not obj_port.isOpen():
            obj_port.open()
