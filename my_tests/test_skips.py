import pytest
import sys


@pytest.mark.skip(reason="This test is skipped because the feature is not ready yet")
def test_future_feature():
    assert 1 + 1 == 3   # This would fail, but it never runs


@pytest.mark.skipif(sys.platform != "linux", reason="Only runs on Linux operating system")
def test_linux_only():
    assert sys.platform == "linux"


def test_always_runs():
    assert 1 + 1 == 2