import csv
import mysql.connector

db_config = {
    'host': 'localhost',
    'user': 'HOLDER',
    'password': 'Cookie123',
    'database': 'QuizGame'
}

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

with open('quiz_questions.csv', mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        category       = row['category']
        difficulty     = row['difficulty']
        question       = row['question']
        correct_answer = row['correct_answer']
        
        # Insert each row into your questions table
        insert_query = """
            INSERT INTO questions (category, difficulty, question, correct_answer)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (category, difficulty, question, correct_answer))

conn.commit()
cursor.close()
conn.close()
