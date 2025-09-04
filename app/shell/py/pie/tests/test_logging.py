import pytest

from pie.logging import (
    logger,
    configure_logging,
    add_file_logger,
    disable_logging,
)


@pytest.fixture(autouse=True)
def reset_logging():
    """Reset logger configuration before and after each test."""
    configure_logging(False, None)
    yield
    configure_logging(False, None)


def test_configure_logging_verbose_sets_debug():
    configure_logging(True, None)
    assert logger._core.min_level == logger.level("DEBUG").no


def test_configure_logging_non_verbose_sets_info():
    configure_logging(False, None)
    assert logger._core.min_level == logger.level("INFO").no


def test_add_file_logger_writes_messages(tmp_path):
    log_file = tmp_path / "test.log"
    disable_logging()
    add_file_logger(str(log_file))
    message = "logged to file"
    logger.debug(message)
    assert message in log_file.read_text(encoding="utf-8")
