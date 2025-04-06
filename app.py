from flask import Flask, request, session, redirect, url_for, jsonify, render_template
from flask_cors import CORS
import mysql.connector
from werkzeug.security import generate_password_hash
import msal
import random
import time

app = Flask(__name__)
app.secret_key = 'YOUR-SECRET-KEY'
CORS(app, supports_credentials=True)

# --- Database configuration ---
db_config = {
    'host': 'localhost',
    'user': 'HOLDER',         # Replace with your MySQL username
    'password': 'Cookie123',  # Replace with your MySQL password
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

@app.route('/')
def index():
    """
    If logged in, show start_quiz.html
    If not, redirect to /login
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('start_quiz.html')

@app.route('/login')
def login():
    """
    Kicks off the MSAL login process
    """
    return redirect(url_for('getAToken'))

@app.route('/getAToken')
def getAToken():
    code = request.args.get('code')
    if not code:
        # Step 1: No code => redirect to Microsoft login
        auth_url = msal_app.get_authorization_request_url(
            scope,
            redirect_uri=redirect_uri
        )
        return redirect(auth_url)

    # Step 2: We got the code => exchange for token
    result = msal_app.acquire_token_by_authorization_code(
        code,
        scopes=scope,
        redirect_uri=redirect_uri
    )
    if 'access_token' in result:
        id_token_claims = result.get('id_token_claims', {})
        email = id_token_claims.get('preferred_username') or id_token_claims.get('email')

        # 'name' from Microsoft SSO claims:
        real_name = id_token_claims.get('name') or email

        if not email:
            return "Error: No email found in token claims", 400

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            # Check if user exists:
            cursor.execute("SELECT id, username FROM users WHERE email = %s", (email,))
            row = cursor.fetchone()

            if row:
                user_id = row[0]
                existing_username = row[1]
            else:
                # Insert new user with name from SSO, username is blank initially
                default_password = generate_password_hash("defaultpassword")
                insert_query = """
                    INSERT INTO users (name, email, password, username)
                    VALUES (%s, %s, %s, %s)
                """
                # name=real_name, email, password=default, username='' for now
                cursor.execute(insert_query, (real_name, email, default_password, ''))
                conn.commit()
                user_id = cursor.lastrowid
                existing_username = ''

            # Store user_id in session
            session['user_id'] = user_id
            # Also store the user's current "username" in session for convenience
            session['username'] = existing_username

        except mysql.connector.Error as err:
            return f"Database error: {str(err)}", 400
        finally:
            cursor.close()
            conn.close()

        # After successful login, redirect...
        #   If they don't have a username yet, prompt them.
        if not existing_username:
            return redirect(url_for('prompt_username'))
        else:
            return redirect(url_for('index'))
    else:
        return f"Token acquisition failed: {result.get('error_description', '')}", 400

# ============================
#   Single-Question-At-A-Time
# ============================

@app.route('/start_quiz', methods=['POST'])
def start_quiz():
    """
    1) Fetch 20 total questions:
       3 Hard, 7 Medium, 10 Easy (from all categories)
    2) Shuffle them
    3) Save them in session
    4) Return JSON with success
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # -- Get 3 random Hard --
        cursor.execute("""
            SELECT id, question, correct_answer, difficulty
            FROM questions
            WHERE difficulty = 'hard'
            ORDER BY RAND()
            LIMIT 3
        """)
        hard_questions = cursor.fetchall()

        # -- Get 7 random Medium --
        cursor.execute("""
            SELECT id, question, correct_answer, difficulty
            FROM questions
            WHERE difficulty = 'medium'
            ORDER BY RAND()
            LIMIT 7
        """)
        medium_questions = cursor.fetchall()

        # -- Get 10 random Easy --
        cursor.execute("""
            SELECT id, question, correct_answer, difficulty
            FROM questions
            WHERE difficulty = 'easy'
            ORDER BY RAND()
            LIMIT 10
        """)
        easy_questions = cursor.fetchall()

        # combine them
        questions_db = hard_questions + medium_questions + easy_questions
        random.shuffle(questions_db)

    except mysql.connector.Error as err:
        return jsonify({'error': f"Database error: {str(err)}"}), 400
    finally:
        cursor.close()
        conn.close()

    # Store them in session for single-question flow
    session['quiz_questions'] = questions_db
    session['current_question_index'] = 0
    session['user_answers'] = {}  # e.g. { question_id: "True"/"False" }

    return jsonify({
        'message': "Quiz started! (3 Hard, 7 Medium, 10 Easy)",
        'total_questions': len(questions_db)
    })

@app.route('/get_question', methods=['GET'])
def get_question():
    """
    Returns the "current question" from session.
    If out of questions, returns done=true
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))

    quiz_questions = session.get('quiz_questions', [])
    index = session.get('current_question_index', 0)

    if index >= len(quiz_questions):
        return jsonify({
            'done': True,
            'message': 'No more questions'
        })

    q = quiz_questions[index]
    return jsonify({
        'done': False,
        'question_id': q['id'],
        'question': q['question'],
        'difficulty': q['difficulty']
    })

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    if 'user_id' not in session:
        # or return a JSON error if you prefer
        return redirect(url_for('login'))

    data = request.json
    question_id = data.get('question_id')
    user_answer = data.get('answer')

    # get the existing dictionary from session or empty if none
    user_answers = session.get('user_answers', {})

    # store the answer under the string key
    user_answers[str(question_id)] = user_answer

    # update session
    session['user_answers'] = user_answers
    session['current_question_index'] += 1

    print(f"submit_answer() => question_id={question_id}, user_answer={user_answer}")
    return jsonify({'message': 'Answer recorded'})

@app.route('/prompt_username')
def prompt_username():
    """
    Simple route to render an HTML form so user can pick a username
    if they don't already have one.
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('choose_username.html')

@app.route('/set_username', methods=['POST'])
def set_username():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    chosen_username = request.form.get('username', '').strip()

    if not chosen_username:
        return "Username cannot be blank", 400

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        # Update the existing user record:
        cursor.execute("""
            UPDATE users
            SET username = %s
            WHERE id = %s
        """, (chosen_username, user_id))
        conn.commit()
    except mysql.connector.Error as err:
        return f"Database error: {str(err)}", 400
    finally:
        cursor.close()
        conn.close()

    # Store in session for convenience
    session['username'] = chosen_username

    # Now redirect to main page
    return redirect(url_for('index'))

@app.route('/get_stats', methods=['GET'])
def get_stats():
    """
    Return the current user's stats (high score, total games played, average score, etc.)
    and also the global leaderboard (top 5 or top 10).
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    stats = {}
    leaderboard = []

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # 1) Fetch the current user's stats
        cursor.execute("""
            SELECT high_score
            FROM users
            WHERE id = %s
        """, (user_id,))
        row = cursor.fetchone()

        user_high_score = row['high_score'] if row else 0

        # total games played
        cursor.execute("""
            SELECT COUNT(*) as total_games, AVG(score) as avg_score
            FROM game_history
            WHERE user_id = %s
        """, (user_id,))
        row = cursor.fetchone()
        total_games = row['total_games'] if row['total_games'] else 0
        avg_score = row['avg_score'] if row['avg_score'] else 0

        stats['high_score'] = user_high_score
        stats['total_games'] = total_games
        stats['avg_score'] = round(avg_score, 2)

        # 2) Leaderboard - top 5
        cursor.execute("""
            SELECT username, high_score
            FROM users
            WHERE username <> ''
            ORDER BY high_score DESC
            LIMIT 5
        """)
        leaderboard_rows = cursor.fetchall()
        leaderboard = leaderboard_rows

    except mysql.connector.Error as err:
        return jsonify({'error': f"Database error: {str(err)}"}), 400
    finally:
        cursor.close()
        conn.close()

    return jsonify({
        'user_stats': stats,
        'leaderboard': leaderboard
    })

@app.route('/finish_quiz', methods=['POST'])
def finish_quiz():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    quiz_questions = session.get('quiz_questions', [])
    user_answers = session.get('user_answers', {})

    print("=== finish_quiz DEBUG ===")
    print(f"quiz_questions length = {len(quiz_questions)}")
    print(f"user_answers = {user_answers}")

    correct_count = 0
    wrong_count = 0
    score = 0

    for q in quiz_questions:
        qid_str = str(q['id'])
        user_ans = user_answers.get(qid_str, '').strip().lower()
        correct_ans = q['correct_answer'].strip().lower()
        difficulty = q['difficulty'].strip().lower()

        print(f"QID={qid_str}, correct_ans={correct_ans}, user_ans={user_ans}, diff={difficulty}")

        if difficulty == 'easy':
            weight = 100
        elif difficulty == 'medium':
            weight = 200
        elif difficulty == 'hard':
            weight = 300
        else:
            weight = 100

        if user_ans in ['true', 'false']:
            if user_ans == correct_ans:
                correct_count += 1
                score += weight
            else:
                wrong_count += 1
                score -= weight
        else:
            print(" -> user_ans not valid (not 'true'/'false'?), skipping")

    print(f"Finished loop: correct={correct_count}, wrong={wrong_count}, score={score}")

    # Clear session quiz data
    session.pop('quiz_questions', None)
    session.pop('current_question_index', None)
    session.pop('user_answers', None)

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO game_history (user_id, category, difficulty, score, timestamp)
            VALUES (%s, %s, %s, %s, NOW())
        """, (user_id, "mixed", "mixed", score))

        # Update high score if needed
        cursor.execute("SELECT high_score FROM users WHERE id = %s", (user_id,))
        row = cursor.fetchone()
        current_highscore = row[0] if row else 0

        if score > current_highscore:
            cursor.execute("""
                UPDATE users
                SET high_score = %s
                WHERE id = %s
            """, (score, user_id))

        conn.commit()
    except mysql.connector.Error as err:
        return jsonify({'error': f"Database error: {str(err)}"}), 400
    finally:
        cursor.close()
        conn.close()

    return jsonify({
        'message': "Quiz finished",
        'score': score,
        'correct_count': correct_count,
        'wrong_count': wrong_count
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
