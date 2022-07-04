import pytest
from cl200a_controller.cl200a_utils import (
    CL200Utils,
    MeasurementValueOverError,
    LowBatteryError,
    LowLuminanceError,
    ValueOutOfRangeError,
)
from serial import SerialException


@pytest.fixture()
def mock_connect_serial_port(mocker):
    ser = mocker.Mock()
    ser.reset_input_buffer = mocker.Mock(return_value=None)
    ser.reset_output_buffer = mocker.Mock(return_value=None)
    ser.readline = mocker.Mock(
        return_value="xxxxxx5x".encode(),
    )
    ser.write = mocker.Mock(return_value=None)
    ser.close = mocker.Mock(return_value=None)
    return ser


# pylint: disable=redefined-outer-name
# to use the fixture, outer name must be used
# pylint: disable=invalid-name
# the names ev, x, y, z, u, v, tcp, delta_uv
# are used in the documentation
# pylint: disable=protected-access
class TestCL200Utils:
    def test_connect_luxmeter(self, mock_connect_serial_port):
        is_connected = CL200Utils.connect_luxmeter(ser=mock_connect_serial_port)
        assert is_connected is True

    def test_connect_luxmeter_read_fail(self, mock_connect_serial_port, mocker):
        mock_connect_serial_port.readline = mocker.Mock(
            side_effect=SerialException(),
        )
        is_connected = CL200Utils.connect_luxmeter(ser=mock_connect_serial_port)
        assert is_connected is False

    def test_connect_luxmeter_usb_fail(self, mock_connect_serial_port, mocker):
        mock_connect_serial_port.reset_input_buffer = mocker.Mock(
            side_effect=SerialException(),
        )
        with pytest.raises(SerialException):
            CL200Utils.connect_luxmeter(ser=mock_connect_serial_port)

    def test_connect_serial_port(self, mock_connect_serial_port, mocker):
        mocker.patch(
            "cl200a_controller.cl200a_utils.Serial", return_value=mock_connect_serial_port
        )
        ser = CL200Utils.connect_serial_port(port="COM1")
        assert isinstance(ser, mocker.Mock)

    def test_write_serial_port(self, mock_connect_serial_port):
        CL200Utils.write_serial_port(ser=mock_connect_serial_port, cmd="cmd", sleep_time=0)
        mock_connect_serial_port.write.assert_called_once_with("cmd".encode())

    def test_write_serial_port_fail(self, mock_connect_serial_port, mocker):
        mock_connect_serial_port.write = mocker.Mock(
            side_effect=SerialException(),
        )
        with pytest.raises(SerialException):
            CL200Utils.write_serial_port(ser=mock_connect_serial_port, cmd="cmd", sleep_time=0)

    def test_check_measurement_123(self):
        result = "xxxxxx1xxxxxx"
        with pytest.raises(ConnectionResetError):
            CL200Utils.check_measurement(result)
        result = "xxxxxx2xxxxxx"
        with pytest.raises(ConnectionResetError):
            CL200Utils.check_measurement(result)
        result = "xxxxxx3xxxxxx"
        with pytest.raises(ConnectionResetError):
            CL200Utils.check_measurement(result)

    def test_check_measurement_4(self):
        result = "xxxxxx4xxxxxx"
        assert CL200Utils.check_measurement(result) is None

    def test_check_measurement_5(self):
        result = "xxxxxx5xxxxxx"
        with pytest.raises(MeasurementValueOverError):
            CL200Utils.check_measurement(result)

    def test_check_measurement_6(self):
        result = "xxxxxx6xxxxxx"
        with pytest.raises(LowLuminanceError):
            CL200Utils.check_measurement(result)

    def test_check_measurement_7(self):
        result = "xxxxxx7xxxxxx"
        with pytest.raises(ValueOutOfRangeError):
            CL200Utils.check_measurement(result)

    def test_check_measurement_8(self):
        result = "xxxxxxxx1xxxx"
        with pytest.raises(LowBatteryError):
            CL200Utils.check_measurement(result)

    def test_extract_one_data_from_result_plus(self):
        result = "\x0200021 10+ 2733+45450+44990\x031F\r\n"
        value = CL200Utils._extract_one_data_from_result(result=result, start_index=9)
        assert value == 27.3

        result = "\x0200021 10- 2733+45450+44990\x031F\r\n"
        value = CL200Utils._extract_one_data_from_result(result=result, start_index=9)
        assert value == -27.3

    def test__extract_three_data_from_result(self):
        result = "\x0200021 10+ 2733+45450+44990\x031F\r\n"
        values = CL200Utils._extract_three_data_from_result(result=result)
        assert values[0] == 27.3
        assert values[1] == 0.455
        assert values[2] == 0.45

    def test_check_command_num(self):
        result = "\x0200021 10+ 2733+45450+44990\x031F\r\n"
        assert CL200Utils._check_command_num(result=result, command_num="02") is None

        result = "\x0200031 10+ 2733+45450+44990\x031F\r\n"
        with pytest.raises(ValueError):
            CL200Utils._check_command_num(result=result, command_num="02")

        with pytest.raises(ValueError):
            CL200Utils._check_command_num(result=result, command_num=["02, 04"])

    def test_clean_obj_port(self, mock_connect_serial_port):
        assert CL200Utils._clean_obj_port(obj_port=mock_connect_serial_port) is None

    def test_clean_obj_port_fail(self, mock_connect_serial_port, mocker):
        mock_connect_serial_port.isOpen = mocker.Mock(return_value=False)

        CL200Utils._clean_obj_port(obj_port=mock_connect_serial_port)
        assert mock_connect_serial_port.open.called is True
