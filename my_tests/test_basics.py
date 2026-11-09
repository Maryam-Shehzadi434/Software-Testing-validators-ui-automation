import pytest
from validators.slug import slug
from validators.length import length
from validators.hashes import md5
from validators.utils import ValidationError


@pytest.mark.parametrize("value", [
    "my-first-post",
    "a",
    "post-123"
])
def test_valid_slug(value):
    assert slug(value) is True


@pytest.mark.parametrize("value", [
    "Bad Slug",
    "my.slug",
    "",
    "-leading-hyphen"
])
def test_invalid_slug(value):
    assert not slug(value)


@pytest.mark.parametrize("text, min_val, max_val, expected", [
    ("abc", 2, 5, True),
    ("a", 2, 5, False),
    ("abcdef", 2, 5, False),
    ("", None, None, True)
])
def test_length_boundaries(text, min_val, max_val, expected):
    assert bool(length(text, min_val=min_val, max_val=max_val)) is expected


def test_invalid_length_returns_error_object():
    result = length("test", min_val=-5)
    assert isinstance(result, ValidationError)


@pytest.mark.parametrize("hash_str, expected", [
    ("d41d8cd98f00b204e9800998ecf8427e", True),
    ("D41D8CD98F00B204E9800998ECF8427E", True),
    ("900zz11", False),
    ("", False)
])
def test_md5_hash(hash_str, expected):
    assert bool(md5(hash_str)) is expected