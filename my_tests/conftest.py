import pytest
from validators.domain import _IanaTLD

@pytest.fixture
def valid_email():
    return "student@example.com"

@pytest.fixture
def setup_teardown_data():
    data = {"url": "https://example.com", "ip": "192.168.0.10"}
    yield data
    data.clear()

@pytest.fixture
def mock_tld_file(monkeypatch):
    def fake_retrieve():
        return ["com", "org", "net"]
    monkeypatch.setattr(_IanaTLD, "_retrieve", fake_retrieve)

# --- MAKE SURE THIS IS AT THE BOTTOM OF conftest.py ---
@pytest.fixture
def boundary_ints():
    return {"min": 1, "max": 10}