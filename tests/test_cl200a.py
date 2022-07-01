from datetime import datetime
import logging
from pathlib import Path

import pytest
from testfixtures import LogCapture

from cl200a_controller import CL200A
from cl200a_controller.logger import Logger


@pytest.fixture(scope="session")
def cl200a(log_file_path):
    return CL200A(log_file_path=log_file_path)


@pytest.fixture(scope="function")
def mock_logger():
    with LogCapture() as log:
        yield log


# pylint: disable=redefined-outer-name
# to use the fixture, outer name must be used
# pylint: disable=invalid-name
# the names ev, x, y, z, u, v, tcp, delta_uv
# are used in the documentation
class TestCL200A:
    def test_init(self, cl200a):
        assert cl200a.__class__.__name__ == "CL200A"
        assert isinstance(cl200a.log_file_path, Path)

    def test_get_ev_x_y(self, cl200a):
        ev, x, y, measured_time = cl200a.get_ev_x_y()
        assert isinstance(ev, float)
        assert isinstance(x, float)
        assert isinstance(y, float)
        assert isinstance(measured_time, datetime)

    def test_get_x_y_z(self, cl200a):
        x, y, z, measured_time = cl200a.get_x_y_z()
        assert isinstance(x, float)
        assert isinstance(y, float)
        assert isinstance(z, float)
        assert isinstance(measured_time, datetime)

    def test_get_ev_u_v(self, cl200a):
        ev, u, v, measured_time = cl200a.get_ev_u_v()
        assert isinstance(ev, float)
        assert isinstance(u, float)
        assert isinstance(v, float)
        assert isinstance(measured_time, datetime)

    def test_get_ev_tcp_delta_uv(self, cl200a):
        ev, tcp, delta_uv, measured_time = cl200a.get_ev_tcp_delta_uv()
        assert isinstance(ev, float)
        assert isinstance(tcp, float)
        assert isinstance(delta_uv, float)
        assert isinstance(measured_time, datetime)

    def test_debug_mode(self, log_file_path, mock_logger):
        Logger.reset_logger()
        cl200a = CL200A(log_file_path=log_file_path, debug=True)
        assert cl200a.logger.level == logging.DEBUG
        mock_logger.clear()

        _ = cl200a.get_ev_x_y()
        assert mock_logger.records[0].levelname == "DEBUG"
        mock_logger.clear()

        _ = cl200a.get_x_y_z()
        assert mock_logger.records[0].levelname == "DEBUG"
        mock_logger.clear()

        _ = cl200a.get_ev_u_v()
        assert mock_logger.records[0].levelname == "DEBUG"
        mock_logger.clear()

        _ = cl200a.get_ev_tcp_delta_uv()
        assert mock_logger.records[0].levelname == "DEBUG"
        mock_logger.clear()
