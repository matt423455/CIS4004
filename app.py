from flask import Flask, request, session, redirect, url_for
from flask_cors import CORS
import mysql.connector
from werkzeug.security import generate_password_hash
import msal  # Microsoft Authentication Library for Python

app = Flask(__name__)
app.secret_key = '17344d5039b0c598f2bdc9f866a500a0'  # Replace with your secure secret key
CORS(app)  # Enable CORS for React (if needed)

# --- Database configuration ---
db_config = {
    'host': 'localhost',
    'user': 'HOLDER',           # Replace with your MySQL username
    'password': 'Cookie123',    # Replace with your MySQL password
    'database': 'QuizGame'
}

# --- Microsoft Entra / MSAL configuration ---
client_id     = '4252cb8e-b486-475c-9163-5e0b679e47ea'  # Application (client) ID from Azure
client_secret = '~d38Q~SpLtT-Tl4IBhfLR_HqNpqdkym6FUjZlcK.'  # Client secret from Azure
tenant_id     = '5ba7dd49-7ac9-4955-b136-4f6f3b6d4709'  # Directory (tenant) ID from Azure
authority     = f'https://login.microsoftonline.com/{tenant_id}'
redirect_uri  = 'https://www.triviaparadise.online/getAToken'  # Must exactly match your Azure app settings
scope         = ['User.Read']  # Adjust scopes as needed

# Initialize the MSAL confidential client
msal_app = msal.ConfidentialClientApplication(
    client_id,
    authority=authority,
    client_credential=client_secret
)

# --- Routes ---

# Root route: automatically sends users to login (MSAL) flow.
@app.route('/')
def index():
    return redirect(url_for('login'))

# /login route: simply redirects to /getAToken to start the MSAL authentication flow.
@app.route('/login')
def login():
    return redirect(url_for('getAToken'))

# /getAToken handles the MSAL auth flow.
@app.route('/getAToken')
def getAToken():
    code = request.args.get('code')
    if not code:
        # No code provided yet; redirect to Microsoft's login page.
        auth_url = msal_app.get_authorization_request_url(scope, redirect_uri=redirect_uri)
        return redirect(auth_url)
    
    # Once redirected back from Microsoft with a code:
    result = msal_app.acquire_token_by_authorization_code(code, scopes=scope, redirect_uri=redirect_uri)
    if 'access_token' in result:
        # Extract user details from the token's claims.
        id_token_claims = result.get('id_token_claims', {})
        email = id_token_claims.get('preferred_username') or id_token_claims.get('email')
        username = id_token_claims.get('name') or email
        if not email:
            return "Error: No email found in token claims", 400

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            # Check if the user already exists by email.
            query = "SELECT id FROM users WHERE email = %s"
            cursor.execute(query, (email,))
            result_db = cursor.fetchone()
            if result_db:
                user_id = result_db[0]
            else:
                # If the user doesn't exist, insert a new record.
                # A default password is set (hashed) but will not be used since MSAL handles auth.
                default_password = generate_password_hash("defaultpassword")
                insert_query = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
                cursor.execute(insert_query, (username, email, default_password))
                conn.commit()
                user_id = cursor.lastrowid
            session['user_id'] = user_id
        except mysql.connector.Error as err:
            return f"Database error: {str(err)}", 400
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('dashboard'))
    else:
        return f"Token acquisition failed: {result.get('error_description', '')}", 400

# /dashboard: A protected route that shows a successful login message.
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return "Successfully logged in!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
