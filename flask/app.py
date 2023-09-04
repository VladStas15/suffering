from flask import Flask, render_template, request, jsonify, g, send_file
from transliterate import translit, get_available_language_codes
from translit_word import TranslitForm
import pandas as pd
import sqlite3
import os

# Конфигурация БД
DATABASE = '/tmp/test.db'

app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path,'test.db')))

#функция для соединения с БД
def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

#функция для создания таблиц

def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    #если не установлено соединение с БД, то устанавливаем
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db

#разрыв соединения с БД, если установлено
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()

@app.route('/')
def index():
    db = get_db()
    form = TranslitForm()
    return render_template("index.html", form=form)

@app.route('/', methods=['POST'])
def index_post():
    form = TranslitForm()
    text = form.vvod.data
    processed_text = translit(text, 'ru', reversed=True)
    lower_processed_text = processed_text.lower()
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO test (vvod_text, Translit_text) VALUES (?, ?)', (text, lower_processed_text))
    db.commit()
    db.close()
    return jsonify({'result': lower_processed_text})

@app.route('/get_latest_records', methods=['GET'])
def get_latest_records():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT vvod_text, Translit_text  FROM test ORDER BY id DESC LIMIT 10")
    latest_records = cursor.fetchall()
    db.close()
    return render_template('latest_records.html', records=latest_records)


@app.route('/export', methods=['GET'])
def export():
    db = get_db()
    query = 'SELECT * FROM test'
    df = pd.read_sql_query(query, db)
    output_file = 'exported_data.xlsx'
    df.to_excel(output_file, index=False)
    db.close()
    return send_file(output_file, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)

