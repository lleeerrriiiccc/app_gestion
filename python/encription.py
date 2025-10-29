import bcrypt


def encrypt_password(password):
    # accept str or bytes; ensure UTF-8 bytes for bcrypt
    if isinstance(password, str):
        password_bytes = password.encode('utf-8')
    else:
        password_bytes = password

    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed

def check_password(password, hashed):
    if isinstance(password, str):
        password_bytes = password.encode('utf-8')
    else:
        password_bytes = password
    if isinstance(hashed, str):
        hashed_bytes = hashed.encode('utf-8')
    else:
        hashed_bytes = hashed
    if bcrypt.checkpw(password_bytes, hashed_bytes):
        return True
    else:
        return False


