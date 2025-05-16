# Block-Box

Block-Box is a secure, web-based file storage application that prioritizes user privacy and data integrity. It features a robust authentication system where each registered user is issued a unique secret key, which also functions as a second factor of authentication during file downloads. Files are encrypted locally using symmetric encryption (Fernet) before being uploaded to the InterPlanetary File System (IPFS), leveraging decentralized storage for improved reliability and resistance to tampering. To maintain a verifiable record of all uploads, the platform stores file metadata—such as the IPFS hash and filename—on a custom blockchain, creating an immutable audit trail. Users can later retrieve and decrypt their files securely using their secret key and the associated IPFS hash.

---

## Features

- **User Registration & Login:** Implements a simple in-memory authentication system for managing user access.
- **File Encryption:** Files are encrypted locally using Fernet symmetric encryption before upload, ensuring confidentiality.
- **Decentralized Storage:** Encrypted files are uploaded to IPFS, providing tamper-resistant and distributed storage.
- **Blockchain Metadata:** File metadata (such as IPFS hash and filename) is stored on a custom blockchain for integrity and traceability.
- **Personal Secret Key:** Each user receives a unique secret key, which acts as Two-Factor Authentication (2FA) when attempting to download an uploaded file.
- **File Download:** Users can securely download and decrypt their files using their secret key and the IPFS hash.
- **File Size & Type Restrictions:** Only files up to 25 MB and of allowed types (`.txt`, `.pdf`, `.png`, `.jpg`, `.jpeg`) can be uploaded.

---

## Tech Stack

### Backend
- **Python 3.10+** – Core backend logic
- **Flask** – Web framework for routing and session handling
- **cryptography (Fernet)** – Symmetric encryption for files
- **Custom Blockchain** – Stores file metadata (IPFS hash, filename)
- **IPFS Client** – Uploads/retrieves files via local IPFS node

### Frontend
- **HTML5 + Jinja2** – Dynamic page rendering
- **CSS3** – UI styling (`styles.css`)
- **JavaScript** – Matrix Theme

### Storage
- **IPFS** – Decentralized file storage 
- **Local File System** – Temp storage for uploads/downloads

### Security
- **Fernet Encryption** – Local encryption/decryption
- **Flask Sessions** – Manages authenticated user sessions

---

## Installation (Windows)

### Prerequisites
- Python 3.10+
- pip (Python package manager)
- IPFS (go-ipfs v0.7.0)

### Steps

1. **Download and install IPFS (go-ipfs v0.7.0):**  
   Download the Windows package from: [https://dist.ipfs.tech/go-ipfs/v0.7.0/](https://dist.ipfs.tech/go-ipfs/v0.7.0/)  
   Extract the downloaded ZIP file to a folder of your choice (e.g., `C:\ipfs`).

2. **Add IPFS to your system PATH:**  
   - Open **Start** and search for **Environment Variables** → **Edit the system environment variables**.  
   - Click **Environment Variables**, select **Path** under System variables, and click **Edit**.  
   - Click **New**, add the full path to the folder containing `ipfs.exe` (e.g., `C:\ipfs`), then click **OK** on all dialogs.

3. **Verify IPFS installation:**  
   Open **Command Prompt** and run: ```ipfs version```
   You should see: `ipfs version 0.7.0`.

4. **Initialize IPFS (only once):**  
   ```ipfs init```

5. **Clone the repository and install dependencies:**  
   ```git clone https://github.com/AdityaKarun/Block-Box.git```
   ```cd Block-Box```

6. **Create and activate a Python virtual environment:**
   ```python -m venv venv```
   ```.\venv\Scripts\activate```
   
7. **Install Python dependencies:**
   ```pip install -r requirements.txt```

8. **Start IPFS daemon:**  
   ```ipfs daemon```
   Keep this window open; the daemon must be running whenever you use the app.

9. **Run the Flask application:**
    ```python app.py```

10. **To access the application, open your browser and go to:**
    ```http://localhost:5000```

---

## Usage

### 1. Sign Up
- Go to the signup page.
- Enter a username and password.
- You will receive a unique secret key. **Store this key securely**; it is required for file downloads.

### 2. Log In
- Enter your username and password.

### 3. Upload a File
- Select a file to upload (max 25 MB, allowed types: `.txt`, `.pdf`, `.png`, `.jpg`, `.jpeg`).
- The file is encrypted and uploaded to IPFS.
- You receive the IPFS hash for later retrieval.

### 4. Download a File
- Enter the IPFS hash and your secret key.
- If valid, the file is downloaded from IPFS, decrypted, and served to you.

---

## API Endpoints

- `/` — Home page
- `/login` — Login page
- `/signup` — Signup page
- `/upload_download` — Upload/download dashboard (requires login)
- `/upload` — Upload a file (POST, requires login)
- `/download` — Download a file (POST, requires login)
- `/logout` — Log out

---

## License

MIT License. See [LICENSE](go-ipfs/LICENSE) for details.
