import re
from flask import Flask, request, render_template,jsonify
import psycopg2
from sqlalchemy.testing import db

app = Flask(__name__)

# PostgreSQL-ə qoşulma funksiyası
def get_db_connection():
    conn = psycopg2.connect(
        host='127.0.0.1',
        database='flaskdbb',  # Burada verilənlər bazanızı qeyd edin
        user='postgres',  # PostgreSQL istifadəçi adınızı qeyd edin
        password='aa3203930'  # PostgreSQL şifrənizi qeyd edin
    )
    return conn


# Girişin doğrulanması funksiyası
def validate_input(username, email):
    # Ad yalnız hərflər və boşluq ehtiva edə bilər
    if not re.match(r"^[A-Za-z\s]+$", username):
        return False, "Ad yalnız hərflər və boşluqlardan ibarət ola bilər."

    # Email ümumi formatda olmalıdır
    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
        return False, "Etibarlı bir email formatı daxil edin."

    return True, None

# HTML forması
@app.route('/')
def index():
    return render_template('index.html')


# Formadan daxil edilən məlumatları PostgreSQL cədvəlinə əlavə etmək
@app.route('/submit', methods=['POST'])
def submit():
    username = request.form['username']
    email = request.form['email']

    # Verilənlər bazasına qoşulma
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Birinci emaili yoxlayırıq
        cursor.execute("SELECT COUNT(id) AS user_count FROM users WHERE email = %s", (email,))
        result = cursor.fetchone()

        if result[0] > 0:
            # Əgər email artıq mövcuddursa, xəta mesajı qaytarırıq
            return jsonify({'error': 'Email already exists. Please use a different email.'}), 400

        # Əgər email mövcud deyilsə, istifadəçini əlavə edirik
        cursor.execute('INSERT INTO users (name, email) VALUES (%s, %s)', (username, email))
        conn.commit()  # Dəyişiklikləri təsdiqləyirik

        return jsonify({'message': 'User added successfully!'})

    except Exception as e:
        # Hər hansı bir xəta baş verdikdə xəta mesajı qaytarırıq
        return jsonify({'error': str(e)}), 500

    finally:
        # Bağlantını həmişə bağlayırıq
        cursor.close()
        conn.close()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Verilənlər bazası cədvəllərini yaradın
    app.run(debug=True)

