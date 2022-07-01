from typing import List, Union

import serial.tools.list_ports as serial_list_ports
from serial import SerialException


class SerialUtils:
    @classmethod
    def list_ports(cls) -> Union[List, List[dict]]:
        """list_ports

        Raises:
            SerialException: raise when no serial port is found.

        Returns:
            Union[List, List[dict]]: list of serial ports.
        """
        ports = serial_list_ports.comports()
        serial_port_list: list = []

        for port in sorted(ports):
            port_dict = {}
            for port_item in vars(port):
                port_dict[f"{port_item}"] = getattr(port, port_item)

            serial_port_list.append(port_dict)

        if len(serial_port_list) == 0:
            raise SerialException("No port found")

        return serial_port_list

    @classmethod
    def find_all_luxmeters(cls, keyword: str, target: str = "manufacturer") -> List[str]:
        """find_all_luxmeters

        Args:
            keyword (str): search keyword. e.g. "FTDI"
            target (str, optional): target key in the serial port dictionary.
            Defaults to "manufacturer".

        Raises:
            SerialException: raises when no luxmeter is found.

        Returns:
            List[str]: list of serial ports that match the keyword.
        """
        try:
            found_ports = cls.list_ports()
        except SerialException as exc:
            raise exc

        if len(found_ports) > 0:
            result = []
            for port in found_ports:
                if target in port and port[target]:
                    if keyword in port[target]:
                        result.append(port["device"])
            if len(result) == 0:
                raise SerialException("luxmeter not found")

            return result

        raise SerialException("No port found")
