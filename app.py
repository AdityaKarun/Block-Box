from flask import Flask, request, render_template, send_file, redirect, url_for, session, flash
import os
import random
import string
import time
from ipfs import IPFSClient
from blockchain import Blockchain
from cryptography.fernet import Fernet

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Define MAX_FILE_SIZE before using it
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE  # Set the maximum file size

ipfs_client = IPFSClient()
blockchain = Blockchain()
UPLOAD_FOLDER = 'uploads'
DOWNLOAD_FOLDER = 'downloads'

# Ensure upload and download directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# In-memory user store (for demonstration purposes)
users = {}

def generate_secret_key():
    """Generate a unique 16-character secret key."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

# Generate a key (do this once and store it securely)
def generate_key():
    key = Fernet.generate_key()
    with open("encryption_key.key", "wb") as key_file:
        key_file.write(key)

# Load the encryption key
def load_key():
    with open("encryption_key.key", "rb") as key_file:
        return key_file.read()

# Ensure the encryption key exists before the app starts
def ensure_encryption_key():
    if not os.path.exists("encryption_key.key"):
        generate_key()

# Encrypt a file
def encrypt_file(file_path):
    key = load_key()
    fernet = Fernet(key)
    
    with open(file_path, "rb") as file:
        file_data = file.read()
    
    encrypted_data = fernet.encrypt(file_data)
    
    with open(file_path, "wb") as file:
        file.write(encrypted_data)

# Decrypt a file
def decrypt_file(file_path):
    key = load_key()
    fernet = Fernet(key)
    
    with open(file_path, "rb") as file:
        encrypted_data = file.read()
    
    decrypted_data = fernet.decrypt(encrypted_data)
    
    with open(file_path, "wb") as file:
        file.write(decrypted_data)

@app.before_request
def limit_file_size():
    # Only apply file size validation to POST requests to the '/upload' route
    if request.endpoint != 'upload_file' or request.method != 'POST':
        return

    # Skip size check if content_length is None (e.g., for GET requests)
    if request.content_length is None:
        return

    # Check if the request content length exceeds the maximum allowed size
    if request.content_length > MAX_FILE_SIZE:
        flash('File size exceeds the maximum limit of 25 MB.', 'error')
        return redirect(url_for('upload_download'))

@app.errorhandler(413)
def request_entity_too_large(error):
    flash('File size exceeds the maximum limit of 25 MB.', 'error')
    return redirect(url_for('upload_download'))

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('upload_download'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    username = request.form['username']
    password = request.form['password']

    if username in users and users[username]['password'] == password:
        session['username'] = username
        return redirect(url_for('upload_download'))

    flash('Invalid username or password.', 'error')
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')

    username = request.form['username']
    password = request.form['password']

    if username in users:
        flash('Username already exists. Please choose a different one.', 'error')
        return redirect(url_for('signup'))

    secret_key = generate_secret_key()
    users[username] = {'password': password, 'secret_key': secret_key}
    flash(f'Your account has been created! Your secret key is "{secret_key}". Please store it securely.', 'success')
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/upload_download')
def upload_download():
    if 'username' not in session:
        flash('Please log in to access this page.', 'error')
        return redirect(url_for('login'))
    return render_template('upload_download.html')

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'username' not in session:
        flash('Please log in to access this feature.', 'error')
        return redirect(url_for('login'))

    file = request.files.get('file')
    if not file or file.filename == '':
        flash('No file selected for upload.', 'error')
        return redirect(url_for('upload_download'))

    if not allowed_file(file.filename):
        flash('Invalid file type. Only .txt, .pdf, .png, .jpg, and .jpeg are allowed.', 'error')
        return redirect(url_for('upload_download'))

    # Generate a unique filename to avoid overwriting
    base_name, ext = os.path.splitext(file.filename)
    unique_suffix = f"_{int(time.time())}"  # Use a timestamp as a unique suffix
    unique_filename = f"{base_name}{unique_suffix}{ext}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)

    # Save the uploaded file
    file.save(file_path)

    # Encrypt the file before uploading to IPFS
    encrypt_file(file_path)

    # Generate a unique name for the encrypted file
    encrypted_file_name = f"encrypted_{unique_filename}"
    encrypted_file_path = os.path.join(UPLOAD_FOLDER, encrypted_file_name)
    os.rename(file_path, encrypted_file_path)

    # Upload to IPFS
    ipfs_hash = ipfs_client.upload_file(encrypted_file_path)

    # Store in blockchain
    blockchain.create_block(len(blockchain.chain), {'file_name': unique_filename, 'ipfs_hash': ipfs_hash})

    # Ensure the hash is displayed on a new line and provide a download link for the encrypted file
    message = (
        f'File uploaded and stored in IPFS!<br>'
        f'Hash: "<code>{ipfs_hash}</code>"<br>'
        f'<a href="{url_for("download_encrypted_file", filename=encrypted_file_name)}" '
        f'class="btn btn-primary">Download Encrypted File</a>'
    )
    return render_template('response.html', message=message)

@app.route('/download_encrypted/<filename>')
def download_encrypted_file(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        flash('Encrypted file not found.', 'error')
        return redirect(url_for('upload_download'))
    return send_file(file_path, as_attachment=True, download_name=filename)

@app.route('/download', methods=['POST'])
def download_file():
    if 'username' not in session:
        flash('Please log in to access this feature.', 'error')
        return redirect(url_for('login'))

    ipfs_hash = request.form['ipfs_hash']
    secret_key = request.form['secret_key']

    # Validate the secret key
    username = session['username']
    if users[username]['secret_key'] != secret_key:
        return render_template('response.html', message='Error: Invalid secret key or IPFS hash not found in the blockchain.')

    # Search for the block with the given IPFS hash to retrieve the original filename
    original_filename = None
    for block in blockchain.chain:
        if block.data.get('ipfs_hash') == ipfs_hash:
            original_filename = block.data.get('file_name')
            break

    if original_filename is None:
        return render_template('response.html', message='Error: IPFS hash not found in the blockchain.')

    # Download the file from IPFS and save it locally
    file_obj = ipfs_client.download_file(ipfs_hash, DOWNLOAD_FOLDER)
    file_path = os.path.join(DOWNLOAD_FOLDER, ipfs_hash)

    if not os.path.exists(file_path):
        return render_template('response.html', message=f'Error: File {ipfs_hash} not found in local storage!')

    # Decrypt the file after downloading
    decrypt_file(file_path)

    # Rename the decrypted file to its original name
    final_file_path = os.path.join(DOWNLOAD_FOLDER, original_filename)

    # Check if the file already exists and avoid overwriting
    if os.path.exists(final_file_path):
        # Append a unique suffix to the filename
        base_name, ext = os.path.splitext(original_filename)
        counter = 1
        while os.path.exists(final_file_path):
            final_file_path = os.path.join(DOWNLOAD_FOLDER, f"{base_name}_{counter}{ext}")
            counter += 1

    os.rename(file_path, final_file_path)

    # Serve the file for download
    return send_file(final_file_path, as_attachment=True, download_name=os.path.basename(final_file_path))

# Call this function during app initialization
ensure_encryption_key()

if __name__ == '__main__':
    app.run(debug=True)
