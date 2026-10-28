import pytest
from pwcheck import check_password, has_repeated_run, has_sequence, load_common_passwords, main

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

def test_common_word_with_digits_and_symbols_is_capped():
    score, reasons = check_password("Password1!", COMMON)
    assert score <= 2
    assert "common word with digits/symbols added" in reasons


def test_summer2024_is_capped_with_real_list():
    score, _ = check_password("Summer2024!!")
    assert score <= 2

def test_keyboard_sequence_is_capped():
    score, reasons = check_password("Qwerty!Xk92mPz", COMMON)
    assert score <= 2
    assert "keyboard or alphabet sequence (like qwer or 1234)" in reasons


def test_number_sequence_is_capped():
    score, _ = check_password("Zx!81234Kp#Lm", COMMON)
    assert score <= 2


def test_has_sequence_detects_sequences():
    assert has_sequence("xx1234xx")
    assert has_sequence("9876")
    assert has_sequence("ABCD")
    assert not has_sequence("a1b2c3d4")
    assert not has_sequence("")


def test_qwerty123456_is_capped_with_real_list():
    score, _ = check_password("qwerty123456")
    assert score <= 2

def test_main_prints_score_and_reasons(monkeypatch, capsys):
    monkeypatch.setattr("getpass.getpass", lambda prompt: "password")
    main()
    out = capsys.readouterr().out
    assert "Score: 0/4" in out
    assert "found in common list" in out


def test_main_prints_perfect_score(monkeypatch, capsys):
    monkeypatch.setattr("getpass.getpass", lambda prompt: "Tr0ub4dor&3xyz!")
    main()
    assert "Score: 4/4 (very strong)" in capsys.readouterr().out