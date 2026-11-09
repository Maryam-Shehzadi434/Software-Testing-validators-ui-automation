# Pytest suite for the `validators` library

Run from inside this folder (see commands in the chat / project guide):

    pytest                                   # all tests
    pytest -m boundary                       # only boundary tests
    pytest test_email.py -k "valid"          # one file, name filter
    pytest --cov --cov-config=.coveragerc --cov-report=term-missing
    $env:RUN_STRESS=1; pytest -m slow        # PowerShell: enables the stress test

Files
- conftest.py                shared fixtures (setup/teardown, session scope, factory, autouse)
- test_email.py              email validation
- test_url.py                URL validation (+ xfail)
- test_ip.py                 IPv4 / IPv6 (+ skip)
- test_between_length_slug.py  boundary-value tests
- test_advanced.py           pytest.raises, monkeypatch, mock, tmp_path, capsys, skipif
- pytest.ini / .coveragerc   configuration
