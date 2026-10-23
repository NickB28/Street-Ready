import pytest

from pwcheck import check_password, has_repeated_run, load_common_passwords

COMMON = {"password", "123456", "qwerty"}


def test_empty_password_scores_zero():
    score, reasons = check_password("", COMMON)
    assert score == 0
    assert "empty password" in reasons


def test_common_password_scores_zero():
    score, reasons = check_password("password", COMMON)
    assert score == 0
    assert "found in common list" in reasons


def test_common_check_ignores_case():
    score, _ = check_password("PassWord", COMMON)
    assert score == 0


def test_short_password_is_flagged():
    _, reasons = check_password("aB3$", COMMON)
    assert "too short (under 8 characters)" in reasons


def test_strong_password_scores_four():
    score, reasons = check_password("Tr0ub4dor&3xyz!", COMMON)
    assert score == 4
    assert reasons == []


def test_missing_symbols_reported():
    _, reasons = check_password("Abcdefgh1234", COMMON)
    assert "no symbols" in reasons


def test_lowercase_only_reports_all_missing_types():
    _, reasons = check_password("abcdefghijkl", COMMON)
    assert "no uppercase letters" in reasons
    assert "no digits" in reasons
    assert "no symbols" in reasons


def test_very_long_password_does_not_break():
    score, _ = check_password("aB3$" * 2500, COMMON)
    assert score == 4


def test_unicode_password_scores_four():
    score, _ = check_password("Ünïcödé-Pässwörd9", COMMON)
    assert score == 4


@pytest.mark.parametrize("pw", ["", " ", "日本語日本語日本語日本語", "a" * 5000, "😀" * 20])
def test_score_always_between_zero_and_four(pw):
    score, _ = check_password(pw, COMMON)
    assert 0 <= score <= 4


def test_real_common_list_loads():
    common = load_common_passwords()
    assert len(common) >= 100
    assert "123456" in common

def test_repeated_characters_are_capped():
    score, reasons = check_password("zzzzzzzzzzzz", COMMON)
    assert score <= 2
    assert "repeated characters (like aaaa)" in reasons


def test_repeated_run_with_symbol_is_capped():
    score, _ = check_password("aaaaaaaaaaaaaaa!", COMMON)
    assert score <= 2


def test_has_repeated_run_detects_runs():
    assert has_repeated_run("abbbbc")
    assert not has_repeated_run("abababab")
    assert not has_repeated_run("")