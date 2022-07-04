import pytest
from serial import SerialException

from cl200a_controller.serial_utils import SerialUtils


class TestSerialUtils:
    def test_list_ports(self):
        serial_port_list = SerialUtils.list_ports()
        assert serial_port_list is not None

    def test_list_ports_no_port(self, mocker):
        mocker.patch("serial.tools.list_ports.comports", return_value=[])
        with pytest.raises(SerialException):
            SerialUtils.list_ports()

    def test_find_all_luxmeters(self, mocker):
        mocker.patch(
            "cl200a_controller.serial_utils.SerialUtils.list_ports",
            return_value=[{"device": "test", "target": "test"}],
        )
        result = SerialUtils.find_all_luxmeters(keyword="test", target="target")
        assert result == ["test"]

    def test_find_all_luxmeters_serial_exception(self, mocker):
        mocker.patch(
            "cl200a_controller.serial_utils.SerialUtils.list_ports",
            side_effect=SerialException,
        )
        with pytest.raises(SerialException):
            SerialUtils.find_all_luxmeters(keyword="test", target="target")

    def test_find_all_luxmeters_no_luxmeters(self, mocker):
        mocker.patch(
            "cl200a_controller.serial_utils.SerialUtils.list_ports",
            return_value=[{"device": "test", "target": "fake"}],
        )
        with pytest.raises(SerialException):
            SerialUtils.find_all_luxmeters(keyword="test", target="target")

    def test_find_all_luxmeters_no_port(self, mocker):
        mocker.patch(
            "cl200a_controller.serial_utils.SerialUtils.list_ports",
            return_value=[],
        )
        with pytest.raises(SerialException):
            SerialUtils.find_all_luxmeters(keyword="test", target="target")
