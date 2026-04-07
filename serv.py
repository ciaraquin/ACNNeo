import datetime
from cryp import groupAESKey, encrypt_message, decrypt_message, createCA, issueCert, verifyCert, getPublicKeyFromCert

CA_PUBLIC_KEY, CA_PRIVATE_KEY = createCA()
USER_CERTS    = {}
USER_PRIV_KEYS = {}
usersAndPasswords = {
    
}


def create_account(username, password):
    if username in usersAndPasswords:
        return "Username already exists."
    usersAndPasswords[username] = password
    # create cert for user
    priv, cert = issueCert(username, CA_PRIVATE_KEY)
    USER_CERTS[username]     = cert
    USER_PRIV_KEYS[username] = priv
    return "Account created successfully."

def check_login(username, password):
    if username not in usersAndPasswords:
        return None, "Username does not exist."
    if usersAndPasswords[username] != password:
        return None, "Incorrect password."
    if not verifyCert(USER_CERTS[username], CA_PUBLIC_KEY):
        return None, "Certificate invalid or expired."
    return username, "Login successful."

POSTS = []
GROUPS = {}  # { group_id: { 'members': {username: True}, 'key': AES_key } }

def create_group(group_id):
    if group_id in GROUPS:
        return "Group already exists."
    GROUPS[group_id] = {'members': {}, 'key': groupAESKey()}
    return "Group created."

def add_to_group(username, group_id):
    if username not in usersAndPasswords:
        return "User does not exist."
    if group_id not in GROUPS:
        return "Group does not exist."
    GROUPS[group_id]['members'][username] = True
    return f"User added to {group_id}."

def rm_from_group(username, group_id):
    if group_id not in GROUPS:
        return "Group does not exist."
    if username not in GROUPS[group_id]['members']:
        return "User is not in the group."
    del GROUPS[group_id]['members'][username]
    return f"User removed from {group_id}."

def make_post(author, body, group_id):
    if group_id not in GROUPS:
        return "Group does not exist."
    key = GROUPS[group_id]['key']
    encrypted_body = encrypt_message(key, body)
    POSTS.append({
        'author': author,
        'created_at': datetime.datetime.now(),
        'body': encrypted_body,
        'group_id': group_id,
    })
    return "Post created."

def get_user_groups(username):
    return [gid for gid, g in GROUPS.items() if username in g['members']]

def return_feed_for_user(username):
    user_groups = set(get_user_groups(username))
    posts = sorted(POSTS, key=lambda x: x['created_at'], reverse=True)
    result = []
    for p in posts:
        gid = p['group_id']
        if gid in user_groups:
            key = GROUPS[gid]['key']
            body = decrypt_message(p['body'], key)
            result.append({**p, 'body': body, 'encrypted': False})
        else:
            result.append({**p, 'encrypted': True})
    return result
