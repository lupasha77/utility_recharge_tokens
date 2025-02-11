def format_token(raw_token):
    """Format the token to include hyphens (XXXX-XXXX-XXXX-XXXX)."""
    cleaned_token = ''.join(filter(str.isdigit, raw_token))
    if len(cleaned_token) != 16:
        return None
    return '-'.join([cleaned_token[i:i+4] for i in range(0, 16, 4)])