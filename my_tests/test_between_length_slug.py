import pytest
import validators


# ------------------------------ between ------------------------------
@pytest.mark.boundary
@pytest.mark.parametrize("value, expected", [
    (0, False),      # just below min
    (1, True),       # == min  (inclusive)
    (5, True),       # inside
    (10, True),      # == max  (inclusive)
    (11, False),     # just above max
    (-3, False),
])
def test_between_integers(value, expected, boundary_ints):
    got = validators.between(value, min_val=boundary_ints["min"], max_val=boundary_ints["max"])
    assert bool(got) is expected


def test_between_floats_and_open_ended():
    assert validators.between(2.5, min_val=2.0, max_val=3.0) is True
    assert validators.between(5, min_val=1) is True        # no upper limit
    assert validators.between(5, max_val=10) is True       # no lower limit


# ------------------------------ length -------------------------------
@pytest.mark.boundary
@pytest.mark.parametrize("text, lo, hi, expected", [
    ("", 1, None, False),        # empty but at least 1 needed
    ("a", 1, 3, True),           # == min
    ("abc", 1, 3, True),         # == max
    ("abcd", 1, 3, False),       # one over max
    ("abc", None, None, True),   # no limits
])
def test_length(text, lo, hi, expected):
    assert bool(validators.length(text, min_val=lo, max_val=hi)) is expected


# ------------------------------- slug --------------------------------
@pytest.mark.parametrize("text", ["my-post", "a", "post-123", "hello-world-2026"])
def test_valid_slugs(text):
    assert validators.slug(text) is True


@pytest.mark.parametrize("text", ["Hello", "my_post", "a--b", "-a", "a-", "", "x y"])
def test_invalid_slugs(text):
    assert not validators.slug(text)
