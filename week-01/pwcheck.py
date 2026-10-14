"""Password strength checker."""

def character_classes(password):
    """Say which type of character the password contains."""
    return {
       "lowercase letters": any(c.islower() for c in password),
        "uppercase letters": any(c.isupper() for c in password),
        "digits": any(c.isdigit() for c in password),
        "symbols": any(not c.isalnum() for c in password), 
    }
    