"""Password strength checker."""
import getpass
from pathlib import Path

COMMON_FILE = Path(__file__).parent / "common_passwords.txt"


def character_classes(password):
    """Say which type of character the password contains."""
    return {
        "lowercase letters": any(c.islower() for c in password),
        "uppercase letters": any(c.isupper() for c in password),
        "digits": any(c.isdigit() for c in password),
        "symbols": any(not c.isalnum() for c in password),
    }


def load_common_passwords(path=COMMON_FILE):
    """Return the common passwords as a lowercase set."""
    with open(path, encoding="utf-8") as f:
        return {line.strip().lower() for line in f if line.strip()}


def check_password(password, common=None):
    """Return (score, reasons). Score is 0 to 4."""
    if not password:
        return 0, ["empty password"]

    if common is None:
        common = load_common_passwords()

    score = 0
    reasons = []

    if len(password) < 8:
        reasons.append("too short (under 8 characters)")
    else:
        score += 1
        if len(password) >= 12:
            score += 1
        else:
            reasons.append("under 12 characters; longer is stronger")

    classes = character_classes(password)
    for name, present in classes.items():
        if not present:
            reasons.append(f"no {name}")
    if sum(classes.values()) >= 3:
        score += 1

    if password.lower() in common:
        reasons.append("found in common list")
        score = 0
    else:
        score += 1

    return score, reasons


LABELS = ["very weak", "weak", "fair", "strong", "very strong"]


def main():
    """Ask for a password (hidden) and print the result."""
    password = getpass.getpass("Enter password (hidden): ")
    score, reasons = check_password(password)
    print(f"Score: {score}/4 ({LABELS[score]})")
    for reason in reasons:
        print(f"  - {reason}")


if __name__ == "__main__":
    main()