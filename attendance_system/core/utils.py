# utils.py not on django package

import qrcode
import json
import base64
from io import BytesIO
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes
import hashlib

# Generate RSA key pair for the application
def generate_key_pair():
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return private_key, public_key

# These would normally be stored securely and loaded from environment variables
# For demonstration purposes, we're generating them at runtime
private_key, public_key = generate_key_pair()

def encrypt_data(data):
    """Encrypt data using RSA"""
    key = RSA.import_key(public_key)
    cipher = PKCS1_OAEP.new(key)
    
    # Convert data to JSON string
    json_data = json.dumps(data)
    
    # For data that might be too large for RSA, we use a hybrid approach
    # Generate a random AES key
    aes_key = get_random_bytes(16)
    
    # Encrypt the data with AES key
    from Crypto.Cipher import AES
    cipher_aes = AES.new(aes_key, AES.MODE_GCM)
    ciphertext, tag = cipher_aes.encrypt_and_digest(json_data.encode('utf-8'))
    
    # Encrypt the AES key with RSA
    encrypted_aes_key = cipher.encrypt(aes_key)
    
    # Combine all components
    encrypted_data = {
        'encrypted_aes_key': base64.b64encode(encrypted_aes_key).decode('utf-8'),
        'nonce': base64.b64encode(cipher_aes.nonce).decode('utf-8'),
        'tag': base64.b64encode(tag).decode('utf-8'),
        'ciphertext': base64.b64encode(ciphertext).decode('utf-8')
    }
    
    return encrypted_data

def decrypt_data(encrypted_data):
    """Decrypt data using RSA"""
    key = RSA.import_key(private_key)
    cipher = PKCS1_OAEP.new(key)
    
    # Decode base64 components
    encrypted_aes_key = base64.b64decode(encrypted_data['encrypted_aes_key'])
    nonce = base64.b64decode(encrypted_data['nonce'])
    tag = base64.b64decode(encrypted_data['tag'])
    ciphertext = base64.b64decode(encrypted_data['ciphertext'])
    
    # Decrypt the AES key with RSA
    aes_key = cipher.decrypt(encrypted_aes_key)
    
    # Decrypt the data with AES key
    from Crypto.Cipher import AES
    cipher_aes = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
    data = cipher_aes.decrypt_and_verify(ciphertext, tag)
    
    # Convert JSON string back to dictionary
    return json.loads(data.decode('utf-8'))

def generate_qr_code(member):
    """Generate a QR code for the member"""
    # Data to encode in QR code
    data = {
        'id': member.student_id,
        'name': member.full_name,
        'section': member.section
    }
    
    # Encrypt the data
    encrypted_data = encrypt_data(data)
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    # Add data to QR code
    qr.add_data(json.dumps(encrypted_data))
    qr.make(fit=True)
    
    # Create an image from the QR Code
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 for displaying in HTML
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qr_code_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return qr_code_image