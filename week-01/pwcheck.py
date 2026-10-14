"""Password strength checker."""

def character_classes(password):
    """Say which type of character the password contains."""
    return {
       "lowercase letters": any(c.islower() for c in password),
        "uppercase letters": any(c.isupper() for c in password),
        "digits": any(c.isdigit() for c in password),
        "symbols": any(not c.isalnum() for c in password), 
    }


def check_password(password):
    """Return (score, reasons). Score is 0 to 4."""
    if not password:
        return 0, ["empty password"]

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

    return score, reasons