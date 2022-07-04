import logging
from datetime import datetime

import pytest
from serial import SerialException
from testfixtures import LogCapture

from cl200a_controller import CL200A
from cl200a_controller.logger import Logger


@pytest.fixture(scope="function")
def cl200a_init_mock(log_file_path, mocker):

    mocker.patch(
        "cl200a_controller.serial_utils.SerialUtils.find_all_luxmeters",
        return_value=[None],
    )

    mocker.patch(
        "cl200a_controller.cl200a_utils.CL200Utils.connect_serial_port",
        return_value=None,
    )

    mocker.patch(
        "cl200a_controller.cl200a.CL200A._connection",
        return_value=None,
    )

    mocker.patch(
        "cl200a_controller.cl200a.CL200A._hold_mode",
        return_value=None,
    )

    mocker.patch(
        "cl200a_controller.cl200a.CL200A._ext_mode",
        return_value=None,
    )

    return CL200A(log_file_path=log_file_path)


@pytest.fixture(scope="function")
def cl200a_debug(log_file_path, mocker):

    mocker.patch(
        "cl200a_controller.serial_utils.SerialUtils.find_all_luxmeters",
        return_value=[None],
    )

    mocker.patch(
        "cl200a_controller.cl200a_utils.CL200Utils.connect_serial_port",
        return_value=None,
    )

    mocker.patch(
        "cl200a_controller.cl200a.CL200A._connection",
        return_value=None,
    )

    mocker.patch(
        "cl200a_controller.cl200a.CL200A._hold_mode",
        return_value=None,
    )

    mocker.patch(
        "cl200a_controller.cl200a.CL200A._ext_mode",
        return_value=None,
    )

    return CL200A(log_file_path=log_file_path, debug=True)


@pytest.fixture(scope="function")
def mock_logger():
    with LogCapture() as log:
        yield log


def setup_mocker(arg):
    pass


# pylint: disable=redefined-outer-name
# to use the fixture, outer name must be used
# pylint: disable=invalid-name
# the names ev, x, y, z, u, v, tcp, delta_uv
# are used in the documentation
# pylint: disable=protected-access
class TestCL200A:
    def test_init(self, log_file_path, mocker):

        mocker.patch(
            "cl200a_controller.serial_utils.SerialUtils.find_all_luxmeters",
            return_value=[None],
        )
        mocker.patch(
            "cl200a_controller.cl200a_utils.CL200Utils.connect_serial_port",
            return_value=None,
        )
        mocker.patch(
            "cl200a_controller.cl200a_utils.CL200Utils.connect_luxmeter",
            return_value=None,
        )
        mocker.patch(
            "cl200a_controller.cl200a.CL200A._connection",
            return_value=None,
        )
        mocker.patch(
            "cl200a_controller.cl200a.CL200A._hold_mode",
            return_value=None,
        )
        mocker.patch(
            "cl200a_controller.cl200a.CL200A._ext_mode",
            return_value=None,
        )

        cl200a = CL200A(log_file_path=log_file_path)
        assert isinstance(cl200a, CL200A)

        # test find_all_luxmeters
        mocker.patch(
            "cl200a_controller.serial_utils.SerialUtils.find_all_luxmeters",
            side_effect=SerialException(),
        )
        with pytest.raises(SerialException):
            cl200a = CL200A(log_file_path=log_file_path)
            assert cl200a.is_connected is False
        mocker.patch(
            "cl200a_controller.serial_utils.SerialUtils.find_all_luxmeters",
            return_value=[None],
        )

        # test connect_serial_port exception
        mocker.patch(
            "cl200a_controller.cl200a_utils.CL200Utils.connect_serial_port",
            return_value=None,
            side_effect=SerialException("Could not connect to luxmeter"),
        )
        with pytest.raises(SerialException):
            cl200a = CL200A(log_file_path=log_file_path)
            assert cl200a.is_connected is False
        mocker.patch(
            "cl200a_controller.cl200a_utils.CL200Utils.connect_serial_port",
            return_value=None,
        )

    def test_connect(self, log_file_path, mocker):
        mocker.patch(
            "cl200a_controller.serial_utils.SerialUtils.find_all_luxmeters",
            return_value=[None],
        )
        mocker.patch(
            "cl200a_controller.cl200a_utils.CL200Utils.connect_serial_port",
            return_value=None,
        )
        mocker.patch(
            "cl200a_controller.cl200a_utils.CL200Utils.connect_luxmeter",
            return_value=None,
        )

        # mocker.patch(
        #     "cl200a_controller.cl200a.CL200A._connection",
        #     return_value=None,
        # )

        mocker.patch(
            "cl200a_controller.cl200a.CL200A._hold_mode",
            return_value=None,
        )

        mocker.patch(
            "cl200a_controller.cl200a.CL200A._ext_mode",
            return_value=None,
        )

        cl200a = CL200A(log_file_path=log_file_path)
        assert cl200a.is_connected is True

        mocker.patch(
            "cl200a_controller.cl200a_utils.CL200Utils.connect_luxmeter",
            side_effect=SerialException(),
        )
        with pytest.raises(SerialException):
            cl200a = CL200A(log_file_path=log_file_path)
            assert cl200a.is_connected is False

    def test_hold_mode(self, log_file_path, mocker):

        mocker.patch(
            "cl200a_controller.serial_utils.SerialUtils.find_all_luxmeters",
            return_value=[None],
        )

        mock_connect_serial_port = mocker.Mock()
        mock_connect_serial_port.reset_input_buffer = mocker.Mock(return_value=None)
        mock_connect_serial_port.reset_output_buffer = mocker.Mock(return_value=None)
        mocker.patch(
            "cl200a_controller.cl200a_utils.CL200Utils.connect_serial_port",
            mock_connect_serial_port,
        )

        mocker.patch(
            "cl200a_controller.cl200a_utils.CL200Utils.write_serial_port",
            return_value=None,
        )

        mocker.patch(
            "cl200a_controller.cl200a.CL200A._connection",
            return_value=None,
        )

        mocker.patch(
            "cl200a_controller.cl200a.CL200A._ext_mode",
            return_value=None,
        )

        cl200a = CL200A(log_file_path=log_file_path)
        assert isinstance(cl200a, CL200A)

        mocker.patch(
            "cl200a_controller.cl200a_utils.CL200Utils.write_serial_port",
            side_effect=SerialException(),
        )
        with pytest.raises(SerialException):
            cl200a = CL200A(log_file_path=log_file_path)
            # assert cl200a.is_connected is False

    def test_ext_mode(self, log_file_path, mocker):
        mocker.patch(
            "cl200a_controller.serial_utils.SerialUtils.find_all_luxmeters",
            return_value=[None],
        )
        mocker.patch(
            "cl200a_controller.cl200a_utils.CL200Utils.connect_luxmeter",
            return_value=None,
        )

        mock_connect_serial_port = mocker.Mock()
        mock_connect_serial_port.reset_input_buffer = mocker.Mock(return_value=None)
        mock_connect_serial_port.reset_output_buffer = mocker.Mock(return_value=None)
        mock_connect_serial_port.readline = mocker.Mock(
            return_value="xxxxxx5x".encode(),
        )

        mocker.patch(
            "cl200a_controller.cl200a_utils.CL200Utils.connect_serial_port",
            return_value=mock_connect_serial_port,
        )

        mocker.patch(
            "cl200a_controller.cl200a.CL200A._connection",
            return_value=None,
        )

        mocker.patch(
            "cl200a_controller.cl200a.CL200A._hold_mode",
            return_value=None,
        )

        mocker.patch(
            "cl200a_controller.cl200a_utils.CL200Utils.write_serial_port",
            return_value=None,
        )

        cl200a = CL200A(log_file_path=log_file_path)
        assert isinstance(cl200a, CL200A)

        mocker.patch(
            "cl200a_controller.cl200a_utils.CL200Utils.write_serial_port",
            side_effect=SerialException(),
        )
        with pytest.raises(SerialException):
            cl200a = CL200A(log_file_path=log_file_path)
            assert cl200a.is_connected is False
        mocker.patch(
            "cl200a_controller.cl200a_utils.CL200Utils.write_serial_port",
            return_value=None,
        )

        mock_connect_serial_port.readline = mocker.Mock(
            return_value="xxxxxx4x".encode(),
        )
        cl200a = CL200A(log_file_path=log_file_path)
        assert isinstance(cl200a, CL200A)

        mock_connect_serial_port.readline = mocker.Mock(
            return_value="xxxxxx1x".encode(),
        )
        with pytest.raises(ConnectionError):
            cl200a = CL200A(log_file_path=log_file_path)

    def test_perform_measurement(self, log_file_path, mocker):
        mocker.patch(
            "cl200a_controller.serial_utils.SerialUtils.find_all_luxmeters",
            return_value=[None],
        )

        mock_connect_serial_port = mocker.Mock()
        mock_connect_serial_port.reset_input_buffer = mocker.Mock(return_value=None)
        mock_connect_serial_port.reset_output_buffer = mocker.Mock(return_value=None)
        # mock_connect_serial_port.readline = "xxxxxx4x".encode()
        mock_connect_serial_port.readline = mocker.Mock(
            return_value="\x0200021 10+ 2733+45450+44990\x031F\r\n".encode(),
        )

        mocker.patch(
            "cl200a_controller.cl200a_utils.CL200Utils.connect_serial_port",
            return_value=mock_connect_serial_port,
        )

        mocker.patch(
            "cl200a_controller.cl200a_utils.CL200Utils.write_serial_port",
            return_value=None,
        )

        mocker.patch(
            "cl200a_controller.cl200a.CL200A._connection",
            return_value=None,
        )

        mocker.patch(
            "cl200a_controller.cl200a.CL200A._ext_mode",
            return_value=None,
        )

        cl200a = CL200A(log_file_path=log_file_path)
        cl200a._perform_measurement(read_cmd=cl200a.cmd_dict["command_02"])

        mock_connect_serial_port.readline = mocker.Mock(
            return_value="".encode(),
        )
        with pytest.raises(ConnectionAbortedError):
            cl200a._perform_measurement(read_cmd=cl200a.cmd_dict["command_02"])

    def test_get_ev_x_y(self, cl200a_init_mock, mocker):
        mocker.patch(
            "cl200a_controller.cl200a.CL200A._perform_measurement",
            return_value=("\x0200021 10+ 2733+45450+44990\x031F\r\n", datetime.now()),
        )
        ev, x, y, measured_time = cl200a_init_mock.get_ev_x_y()
        assert isinstance(ev, float)
        assert isinstance(x, float)
        assert isinstance(y, float)
        assert isinstance(measured_time, datetime)

    def test_get_x_y_z(self, cl200a_init_mock, mocker):
        mocker.patch(
            "cl200a_controller.cl200a.CL200A._perform_measurement",
            return_value=("\x0200011 10+ 2693+ 2673+  563\x0307\r\n", datetime.now()),
        )

        x, y, z, measured_time = cl200a_init_mock.get_x_y_z()
        assert isinstance(x, float)
        assert isinstance(y, float)
        assert isinstance(z, float)
        assert isinstance(measured_time, datetime)

    def test_get_ev_u_v(self, cl200a_init_mock, mocker):
        mocker.patch(
            "cl200a_controller.cl200a.CL200A._perform_measurement",
            return_value=("\x0200031 10+ 2723+24270+54070\x031A\r\n", datetime.now()),
        )

        ev, u, v, measured_time = cl200a_init_mock.get_ev_u_v()
        assert isinstance(ev, float)
        assert isinstance(u, float)
        assert isinstance(v, float)
        assert isinstance(measured_time, datetime)

    def test_get_ev_tcp_delta_uv(self, cl200a_init_mock, mocker):
        mocker.patch(
            "cl200a_controller.cl200a.CL200A._perform_measurement",
            return_value=("\x0200081 10+ 2703+30744+01490\x031E\r\n", datetime.now()),
        )

        ev, tcp, delta_uv, measured_time = cl200a_init_mock.get_ev_tcp_delta_uv()
        assert isinstance(ev, float)
        assert isinstance(tcp, float)
        assert isinstance(delta_uv, float)
        assert isinstance(measured_time, datetime)

    def test_debug_mode(self, cl200a_debug, log_file_path, mock_logger, mocker):
        Logger.reset_logger()
        cl200a_debug = CL200A(log_file_path=log_file_path, debug=True)

        assert cl200a_debug.logger.level == logging.DEBUG
        mock_logger.clear()

        mocker.patch(
            "cl200a_controller.cl200a.CL200A._perform_measurement",
            return_value=("\x0200021 10+ 2733+45450+44990\x031F\r\n", datetime.now()),
        )
        _ = cl200a_debug.get_ev_x_y()
        assert mock_logger.records[0].levelname == "DEBUG"
        mock_logger.clear()

        mocker.patch(
            "cl200a_controller.cl200a.CL200A._perform_measurement",
            return_value=("\x0200011 10+ 2693+ 2673+  563\x0307\r\n", datetime.now()),
        )
        _ = cl200a_debug.get_x_y_z()
        assert mock_logger.records[0].levelname == "DEBUG"
        mock_logger.clear()

        mocker.patch(
            "cl200a_controller.cl200a.CL200A._perform_measurement",
            return_value=("\x0200031 10+ 2723+24270+54070\x031A\r\n", datetime.now()),
        )
        _ = cl200a_debug.get_ev_u_v()
        assert mock_logger.records[0].levelname == "DEBUG"
        mock_logger.clear()

        mocker.patch(
            "cl200a_controller.cl200a.CL200A._perform_measurement",
            return_value=("\x0200081 10+ 2703+30744+01490\x031E\r\n", datetime.now()),
        )
        _ = cl200a_debug.get_ev_tcp_delta_uv()
        assert mock_logger.records[0].levelname == "DEBUG"
        mock_logger.clear()
