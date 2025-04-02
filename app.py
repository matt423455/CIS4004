from flask import Flask, request, session, redirect, url_for, jsonify, render_template
from flask_cors import CORS
import mysql.connector
from werkzeug.security import generate_password_hash
import msal
import random
import time

app = Flask(__name__)
app.secret_key = '17344d5039b0c598f2bdc9f866a500a0'  # Replace with a secure secret key
CORS(app)

# --- Database configuration ---
db_config = {
    'host': 'localhost',
    'user': 'HOLDER',        # Replace with your MySQL username
    'password': 'Cookie123', # Replace with your MySQL password
    'database': 'QuizGame'
}

# --- MSAL configuration ---
client_id     = '4252cb8e-b486-475c-9163-5e0b679e47ea'
client_secret = '~d38Q~SpLtT-Tl4IBhfLR_HqNpqdkym6FUjZlcK.'
tenant_id     = '5ba7dd49-7ac9-4955-b136-4f6f3b6d4709'
authority     = f'https://login.microsoftonline.com/{tenant_id}'
redirect_uri  = 'https://www.triviaparadise.online/getAToken'
scope         = ['User.Read']

msal_app = msal.ConfidentialClientApplication(
    client_id,
    authority=authority,
    client_credential=client_secret
)

# -----------------------------
#      EXISTING MSAL ROUTES
# -----------------------------
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login')
def login():
    return redirect(url_for('getAToken'))

@app.route('/getAToken')
def getAToken():
    code = request.args.get('code')
    if not code:
        # No code: redirect to Microsoft login
        auth_url = msal_app.get_authorization_request_url(scope, redirect_uri=redirect_uri)
        return redirect(auth_url)
    
    # Once redirected back with code:
    result = msal_app.acquire_token_by_authorization_code(code, scopes=scope, redirect_uri=redirect_uri)
    if 'access_token' in result:
        id_token_claims = result.get('id_token_claims', {})
        email = id_token_claims.get('preferred_username') or id_token_claims.get('email')
        username = id_token_claims.get('name') or email
        
        if not email:
            return "Error: No email found in token claims", 400
        
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            # Check if user exists:
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            row = cursor.fetchone()
            if row:
                user_id = row[0]
            else:
                # Insert new user
                default_password = generate_password_hash("defaultpassword")
                insert_query = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
                cursor.execute(insert_query, (username, email, default_password))
                conn.commit()
                user_id = cursor.lastrowid
            
            # Store user in session
            session['user_id'] = user_id
            
        except mysql.connector.Error as err:
            return f"Database error: {str(err)}", 400
        finally:
            cursor.close()
            conn.close()
        
        return redirect(url_for('select_quiz'))
    else:
        return f"Token acquisition failedd: {result.get('error_description', '')}", 400

# -----------------------------------
#    QUIZ-RELATED ROUTES START HERE
# -----------------------------------

@app.route('/select_quiz')
def select_quiz():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Ideally we'd gather unique categories and difficulties from the DB:
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Get distinct categories
        cursor.execute("SELECT DISTINCT category FROM questions")
        categories = [row[0] for row in cursor.fetchall()]
        
        # Get distinct difficulties
        cursor.execute("SELECT DISTINCT difficulty FROM questions")
        difficulties = [row[0] for row in cursor.fetchall()]
        
    except mysql.connector.Error as err:
        return f"Database error: {str(err)}", 400
    finally:
        cursor.close()
        conn.close()
    
    # This example returns JSON, but you could also use a template
    return render_template(
        'select_quiz.html',
        categories=categories,
        difficulties=difficulties
    )

@app.route('/start_quiz', methods=['POST'])
def start_quiz():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.content_type == 'application/json':
        # Parse JSON
        data = request.json
        category   = data.get('category')
        difficulty = data.get('difficulty')
    else:
        # Assume it's an HTML form
        category   = request.form.get('category')
        difficulty = request.form.get('difficulty')
    
    # For example, fetch 10 random questions from the DB
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)  # dictionary=True for easier reading of columns
        
        query = """
            SELECT id, question, correct_answer 
            FROM questions
            WHERE category = %s
              AND difficulty = %s
            ORDER BY RAND()
            LIMIT 20
        """
        cursor.execute(query, (category, difficulty))
        questions_db = cursor.fetchall()
        
    except mysql.connector.Error as err:
        return jsonify({'error': f"Database error: {str(err)}"}), 400
    finally:
        cursor.close()
        conn.close()
    
    # For security, we don't want to send correct answers back in the same request.
    # We'll store them in the user session to compare later.
    # Concurrent quizzes will be stored differently.
    questions_for_client = []
    for q in questions_db:
        questions_for_client.append({
            'id': q['id'],
            'question': q['question'],
            'correct_answer': q['correct_answer']
        })

    return jsonify({
        'message': f"Quiz started for category: {category}, difficulty: {difficulty}",
        'questions': questions_for_client
    })

@app.route('/submit_answers', methods=['POST'])
def submit_answers():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user_answers = request.json.get('answers', [])  # e.g. list of { 'question_id': 123, 'answer': 'True' }
    
    # Retrieve the correct answers
    correct_answers_map = session.get('correct_answers', {})
    
    score = 0
    for ans in user_answers:
        qid = ans['question_id']
        user_answer = ans['answer']
        # Compare
        if str(correct_answers_map.get(qid, '')).lower() == str(user_answer).lower():
            score += 1
    
    # Clear out correct answers from session once used
    session.pop('correct_answers', None)
    
    # Now we check if this score is higher than user's current highscore
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Get current highscore
        cursor.execute("SELECT highscore FROM users WHERE id = %s", (user_id,))
        row = cursor.fetchone()
        current_highscore = row[0] if row else 0
        
        if score > current_highscore:
            # Update new highscore
            cursor.execute("UPDATE users SET highscore = %s WHERE id = %s", (score, user_id))
            conn.commit()
        
    except mysql.connector.Error as err:
        return jsonify({'error': f"Database error: {str(err)}"}), 400
    finally:
        cursor.close()
        conn.close()
    
    return jsonify({
        'score': score,
        'message': "Quiz complete!",
    })

# Just a simple route to see the user’s highscore or handle a next step:
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    highscore = 0
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT highscore FROM users WHERE id = %s", (user_id,))
        row = cursor.fetchone()
        if row:
            highscore = row[0]
    except mysql.connector.Error as err:
        return f"Database error: {str(err)}", 400
    finally:
        cursor.close()
        conn.close()
    
    return f"Your current high score is: {highscore}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
