import pytest


@pytest.fixture(scope="session")
def log_file_path(tmp_path_factory):
    return tmp_path_factory.mktemp("test") / "test.log"
