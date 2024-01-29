from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import subprocess

app = Flask(__name__)

def get_db_connection():
    conn = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='20092021',
        database='mydatabase'
    )
    return conn

@app.route('/search_history')
def search_history():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 'search_logs' 테이블에서 모든 검색 기록 가져오기
    cursor.execute('SELECT * FROM search_logs ORDER BY search_time DESC')
    logs = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # 검색 기록을 'search_history.html' 템플릿에 전달
    return render_template('search_history.html', logs=logs)

@app.route('/parsing_management')
def parsing_management():
    results, filenames = get_parsing_info()  # 파싱 정보를 가져오는 기존 함수 사용

    # 'parsing_management.html' 템플릿 렌더링, 결과와 파일명을 템플릿에 전달
    return render_template('parsing_management.html', results=results, filenames=filenames)


@app.route('/delete_log/<int:log_id>')
def delete_log(log_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 특정 검색 기록 삭제
    cursor.execute('DELETE FROM search_logs WHERE id = %s', (log_id,))
    conn.commit()
    
    cursor.close()
    conn.close()
    
    # 삭제 후 검색 기록 페이지로 리다이렉트
    return redirect(url_for('search_history'))
def get_parsing_info():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # parsing_results 테이블에서 파싱 결과 가져오기
    cursor.execute('SELECT * FROM parsing_results')
    results = cursor.fetchall()

    # parsing_filename 테이블에서 파일별 파싱 상태 가져오기
    cursor.execute('SELECT * FROM parsing_filename')
    filenames = cursor.fetchall()

    cursor.close()
    conn.close()
    return results, filenames

@app.route('/')
def index():
    return render_template('main_page.html')


@app.route('/paper_details/<pmid>')
def paper_details(pmid):
    conn = get_db_connection()
    # 커서 생성 시 buffered=True 옵션 추가
    cursor = conn.cursor(dictionary=True, buffered=True)

    cursor.execute('SELECT * FROM parsed_data WHERE PMID = %s', (pmid,))
    paper = cursor.fetchone()

    cursor.close()
    conn.close()

    if paper is not None:
        return render_template('paper_details.html', paper=paper)
    else:
        return "Paper not found", 404




@app.route('/start_parsing', methods=['POST'])
def start_parsing():
    try:
        # subprocess의 출력을 캡처
        result1 = subprocess.run(['python', 'down_updatefiles_V3.py'], text=True, capture_output=True)
        result2 = subprocess.run(['python', 'parse_sql_unzip_V3.py'], text=True, capture_output=True)
        console_output = result1.stdout + "\n" + result2.stdout
        message = "성공적으로 파싱되었습니다."
    except subprocess.CalledProcessError as e:
        console_output = e.stdout + "\n" + e.stderr
        message = "파싱 중 오류가 발생했습니다."

    # 파싱 결과와 파일 상태 정보 가져오기
    results, filenames = get_parsing_info()

    # 콘솔 출력, 메시지, 파싱 결과, 파일 상태를 템플릿에 전달
    return render_template('parsing_management.html', message=message, console_output=console_output, results=results, filenames=filenames)




# 상세 정보, 검색 히스토리 등 나머지 라우트는 추가 구현 필요

@app.route('/search_papers', methods=['GET', 'POST'])
def search_papers():
    search_results = []
    search_query = ''  # search_query를 빈 문자열로 초기화하여 항상 정의되도록 함
    if request.method == 'POST':
        search_query = request.form['search_query']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 'search_logs' 테이블이 없는 경우 생성
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                search_query VARCHAR(255),
                search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 검색 쿼리를 사용하여 'parsed_data' 테이블에서 논문 정보 조회
        search_sql = "SELECT * FROM parsed_data WHERE ArticleTitle LIKE %s OR JournalTitle LIKE %s"
        cursor.execute(search_sql, ('%' + search_query + '%', '%' + search_query + '%'))
        search_results = cursor.fetchall()

        # 검색 기록을 'search_logs' 테이블에 저장
        insert_log_sql = "INSERT INTO search_logs (search_query) VALUES (%s)"
        cursor.execute(insert_log_sql, (search_query,))
        conn.commit()

        cursor.close()
        conn.close()

    # search_query 변수도 함께 전달
    return render_template('search_papers.html', search_results=search_results, search_query=search_query)


if __name__ == '__main__':
    app.run(debug=True)


