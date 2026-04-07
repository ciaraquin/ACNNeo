from cryptography.fernet import Fernet
import rsa
import datetime
import json
import base64
import time
import os

def createCA():
    ca_public, ca_private = rsa.newkeys(2048)
    return ca_public, ca_private


def issueCert(username, ca_private_key):
    user_public, user_private = rsa.newkeys(2048)

    pub_pem = user_public.save_pkcs1().decode()

    cert_data = {
        "username":   username,
        "public_key": pub_pem,
        "issued_at":  time.time(),
        "expires_at": time.time() + 365 * 86400
    }

    data_bytes = json.dumps(cert_data, sort_keys=True).encode()
    signature  = rsa.sign(data_bytes, ca_private_key, "SHA-256")
    cert_data["signature"] = base64.b64encode(signature).decode()

    return user_private, cert_data

def verifyCert(cert_data, ca_public):
    try:
        sig = base64.b64decode(cert_data["signature"])
        payload = {k: v for k, v in cert_data.items() if k != "signature"}
        data_bytes = json.dumps(payload, sort_keys=True).encode()
        rsa.verify(data_bytes, sig,ca_public)
        if time.time() > cert_data["expires_at"]:
            return False
        return True
    except rsa.VerificationError:
        return False


def getPublicKeyFromCert(cert_data, ca_public_key):
    if not verifyCert(cert_data, ca_public_key):
        raise ValueError("Invalid or expired certificate")
    return rsa.PublicKey.load_pkcs1(cert_data["public_key"].encode())

def userRSAKeyPair():
    publicKey, privateKey = rsa.newkeys(2048)
    return publicKey, privateKey


def groupAESKey():
    key = Fernet.generate_key()
    return key


def encryptGroupKey(group_key, user_public_key):
    groupKey = rsa.encrypt(group_key, user_public_key)
    return groupKey


def encrypt_message(aes_key, plaintext):
    fernet = Fernet(aes_key)
    message = fernet.encrypt(plaintext.encode())
    return message

def decrypt_message(ciphertext, aes_key):
    fernet = Fernet(aes_key)
    decMessage = fernet.decrypt(ciphertext).decode()
    return decMessage