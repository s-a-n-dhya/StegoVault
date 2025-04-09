from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

def generate_keys():
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return private_key, public_key

def encrypt_rsa(data, public_key_bytes):
    pub_key = RSA.import_key(public_key_bytes)
    cipher = PKCS1_OAEP.new(pub_key)
    return cipher.encrypt(data)

def decrypt_rsa(encrypted_data, private_key_bytes):
    priv_key = RSA.import_key(private_key_bytes)
    cipher = PKCS1_OAEP.new(priv_key)
    return cipher.decrypt(encrypted_data)
