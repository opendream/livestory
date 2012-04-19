import base64, hashlib

def generate_username(email):
    return generate_md5_base64(email)

def generate_md5_base64(str):
    m = hashlib.md5()
    m.update(str)
    hash = base64.urlsafe_b64encode(m.digest())
    hash = hash.replace('=', '')
    hash = hash.replace('+', '-')
    hash = hash.replace('/', '_')

    return hash