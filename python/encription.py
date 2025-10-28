import bcrypt


def encrypt_password(password):
    # accept str or bytes; ensure UTF-8 bytes for bcrypt
    if isinstance(password, bytes):
        password_bytes = password
    else:
        password_bytes = password.encode('utf-8')

    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed


encrypt_password(b"micontrasenasegura")
