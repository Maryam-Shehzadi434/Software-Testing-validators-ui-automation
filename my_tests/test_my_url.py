import pytest
import validators


@pytest.mark.parametrize("link", [
    "https://example.com",
    "http://example.com/path/page.html",
    "https://example.com:8080/a?b=1&c=2",
    "ftp://files.example.com",
])
def test_valid_urls(link):
    assert validators.url(link) is True


@pytest.mark.parametrize("link", [
    "",                # empty
    "example.com",     # missing scheme
    "htp:/x",          # broken scheme
    "http://",         # no host
])
def test_invalid_urls(link):
    assert not validators.url(link)


def test_private_option_accepts_private_ip_only():
    # private=True means: ONLY private-network addresses are accepted
    assert validators.url("http://192.168.1.1", private=True) is True
    assert not validators.url("http://8.8.8.8", private=True)


def test_localhost_accepted_with_simple_host():
    assert validators.url("http://localhost:8000/path", simple_host=True) is True
