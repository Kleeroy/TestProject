## Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/attendance-system.git
cd attendance-system
```

2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run migrations
```bash
python manage.py makemigrations core
python manage.py migrate
```

5. Create a superuser (admin)
```bash
python manage.py createsuperuser
```

6. Run the development server
```bash
python manage.py runserver
```

7. Access the application at http://127.0.0.1:8000/

## Setup Admin Access

After creating a regular user account:

1. Access the Django admin panel at http://127.0.0.1:8000/admin/
2. Login with your superuser credentials
3. Navigate to the "Members" section
4. Find your user and check the "is_admin" checkbox
5. Save changes

## Usage

### For Admins

1. Login with admin credentials
2. Create events with necessary details
3. Use the QR scanner to mark attendance for members
4. Generate and view reports

### For Members

1. Register for an account or login
2. View your generated QR code
3. Present your QR code for scanning at events
4. View your attendance statistics

## Security

Member details in QR codes are encrypted using RSA encryption, ensuring that:

- Data cannot be forged
- QR codes cannot be duplicated without access to the encryption keys
- Each QR code is uniquely tied to a specific member

## Development

This project uses:

- Django 4.2.5 for the web framework
- pycryptodome for RSA encryption
- qrcode and Pillow for QR code generation
- Bootstrap 5 for the frontend
- jsQR for QR code scanning
