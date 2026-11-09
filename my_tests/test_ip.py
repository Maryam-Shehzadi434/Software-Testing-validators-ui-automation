import pytest
from validators.ip_address import ipv4, ipv6
from validators.domain import domain
from validators.url import url


@pytest.mark.parametrize("ip, expected", [
    ("192.168.1.1", True),
    ("255.255.255.255", True),
    ("256.1.1.1", False),
    ("192.168.1", False),
    ("abc", False),
    ("", False)
])
def test_ipv4_boundaries(ip, expected):
    assert bool(ipv4(ip)) is expected


@pytest.mark.parametrize("ip, expected", [
    ("10.0.0.1", True),
    ("172.16.0.1", True),
    ("8.8.8.8", False)
])
def test_ipv4_private_flag(ip, expected):
    assert bool(ipv4(ip, private=True)) is expected


def test_valid_ipv6():
    assert ipv6("::1") is True
    assert ipv6("2001:db8::1") is True


def test_domain_using_monkeypatch(mock_tld_file):
    assert domain("example.com", consider_tld=True) is True
    assert not domain("example.xyz", consider_tld=True)


@pytest.mark.parametrize("link", [
    "https://example.com",
    "ftp://files.example.com"
])
def test_valid_urls(link):
    assert url(link) is True


def test_localhost_url():
    assert url("http://localhost:8080", simple_host=True) is True


@pytest.mark.parametrize("link", [
    "",
    "example.com",
    "http://",
    "htp://example.com"
])
def test_invalid_urls(link):
    assert not url(link)