import pytest
import sys
from validators.email import email
from validators.utils import ValidationError
import validators.email as email_module


def test_email_with_fixture(valid_email):
    assert email(valid_email) is True


def test_email_with_setup_teardown(setup_teardown_data):
    # SETUP happens in conftest.py before this runs. 
    # TEARDOWN happens in conftest.py after this finishes.
    assert setup_teardown_data["ip"] == "192.168.0.10"


@pytest.mark.parametrize("address", [
    "plain",
    "@missing.com",
    "a b@x.com",
    ""
])
def test_invalid_email_returns_error_object(address):
    result = email(address)
    assert isinstance(result, ValidationError)
    assert not result


def test_email_raises_when_r_ve_is_true():
    with pytest.raises(ValidationError):
        email("bogus_email", r_ve=True)


# 1. SKIPIF EXAMPLE
@pytest.mark.skipif(sys.platform != "win32", reason="Only runs on Windows")
def test_windows_specific_email():
    assert email("windows@example.com") is True


# 2. MOCKING EXAMPLE (Monkeypatch)
def test_email_with_mock(monkeypatch):
    # We temporarily fake the hostname validator to always say "False"
    monkeypatch.setattr(email_module, "hostname", lambda *a, **k: False)
    
    # Now, even a perfectly good email will be rejected because our mock overrides the hostname check
    result = email("test@example.com")
    assert isinstance(result, ValidationError)