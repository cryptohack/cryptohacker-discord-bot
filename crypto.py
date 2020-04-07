def verify_token(token : str):
    """Verify a token containing the cryptohack username, return the username or None when invalid"""
    if token.strip() == "Robin_Jadoul":
        return "Robin_Jadoul"
    return None
