# ACNNeo
 
A secure social media web application built with Flask. Users can create accounts, form private groups, and share encrypted posts.
 
## How it works
 
Each user is issued an RSA key pair and a signed JSON certificate when they register. Group posts are encrypted with a symmetric AES key (Fernet), and access is controlled by group membership. Users outside a group see only ciphertext.
 
```
User registers → RSA key pair + JSON cert issued
      ↓
Admin creates group → AES group key generated
      ↓
Users added to group → can encrypt/decrypt posts
      ↓
Posts stored as ciphertext → only members can read
```
 
## Project structure
 
```
ACNNeo/
├── app.py          # Flask routes and app entry point
├── serv.py         # User accounts, groups, and post logic
├── cryp.py         # Cryptography: RSA keys, certs, AES encryption
└── templates/      # HTML templates
```
 
## Installation
 
```bash
pip3 install flask flask-wtf rsa cryptography
```
 
## Running
 
```bash
python3 app.py
```
 
Then open `http://127.0.0.1:5000/` in your browser.
 
Default demo accounts: `ciara / password123`, `alice / mypassword789`, `bob / passw0rd321`
