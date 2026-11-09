import pytest
from validators.utils import validator, ValidationError
from validators.email import email


@validator
def is_even(value):
    return value % 2 == 0


def test_custom_validator():
    assert is_even(4) is True
    
    result = is_even(5)
    assert isinstance(result, ValidationError)
    assert result.value == 5


def test_env_variable_raises_error(monkeypatch):
    monkeypatch.setenv("RAISE_VALIDATION_ERROR", "True")
    
    with pytest.raises(ValidationError):
        is_even(3)


def test_capsys_prints_result(capsys):
    result = email("test@example.com")
    print(f"Validation result: {result}")
    
    captured = capsys.readouterr()
    assert captured.out == "Validation result: True\n"