from offlineforge import __version__
import pytest
def test_version():
    assert isinstance(__version__, str)
