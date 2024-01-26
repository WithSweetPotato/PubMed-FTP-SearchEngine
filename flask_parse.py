from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import datetime

app = Flask(__name__)

# MariaDB 연결 설정을 통합한 버전
db_config = {
    'host': 'localhost',
    'user': 'root',  # 데이터베이스 사용자 이름
    'passwd': '20092021',  # 데이터베이스 비밀번호
    'database': 'mydatabase'  # 데이터베이스 이름
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_parsing', methods=['POST'])
def start_parsing():
    # 파싱 작업 시작 로직 (parse_auto_unzip.py 스크립트 호출 등)
    # 예: start_parsing_script() 함수를 여기에 구현하거나 호출

    # 데이터베이스에 파싱 작업 시작 기록
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    start_time = datetime.datetime.now()
    cursor.execute("INSERT INTO parsing_jobs (start_time, status) VALUES (%s, %s)", (start_time, 'Running'))
    connection.commit()
    job_id = cursor.lastrowid  # 생성된 작업 ID 가져오기
    cursor.close()
    connection.close()

    return redirect(url_for('parsing_status', job_id=job_id))

@app.route('/parsing_status/<int:job_id>')
def parsing_status(job_id):
    # 파싱 작업 상태 조회 로직
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM parsing_jobs WHERE id = %s", (job_id,))
    job = cursor.fetchone()
    cursor.close()
    connection.close()

    return render_template('parsing_status.html', job=job)

if __name__ == '__main__':
    app.run(debug=True)
