from flask import Flask, render_template
import hashlib
from ftplib import FTP
import os
import mysql.connector
import gzip
import xml.etree.ElementTree as ET
from datetime import datetime
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

app = Flask(__name__)

## 테스트 파일 생성 함수 ##################################################
def test():
    # 테스트 파일 1: example.xml.gz
    file_content_1 = b"This is the content of example.xml.gz"
    file_path_1 = "save_files/example.xml.gz"
    md5_hash_1 = hashlib.md5(file_content_1).hexdigest()

    # 테스트 파일 2: example1.xml.gz
    file_content_2 = b"This is the content of example1.xml.gz"
    file_path_2 = "save_files/example1.xml.gz"
    md5_hash_2 = hashlib.md5(file_content_2).hexdigest()

    # MD5 파일 생성
    with open("save_files/example.xml.gz.md5", "w") as md5_file_1:
        md5_file_1.write(md5_hash_1)

    with open("save_files/example1.xml.gz.md5", "w") as md5_file_2:
        md5_file_2.write(md5_hash_2)

    # 실제 파일 생성
    with open(file_path_1, "wb") as file_1:
        file_1.write(file_content_1)

    with open(file_path_2, "wb") as file_2:
        file_2.write(file_content_2)

## 다운 함수 ######################################################
def down():
    # FTP에서 XML 파일 다운로드
    xml_file_names = ftp_download()
    
    # 테스트용 성공 데이터 추가
    xml_file_names.append("example.xml.gz")
    xml_file_names.append("example1.xml.gz")

    # MD5 검증 수행
    success_xml_files, fail_xml_files = init_call_md5(xml_file_names)
    print(f"성공한 XML 파일들 : {success_xml_files}")
    print(f"실패한 XML 파일들 : {fail_xml_files}")
    # 결과를 텍스트 파일에 저장
    success_file_path = os.path.join(".", "save_result", "success_xml_list.txt")
    fail_file_path = os.path.join(".", "save_result", "fail_xml_list.txt")

    write_list_to_file(success_xml_files, success_file_path)
    write_list_to_file(fail_xml_files, fail_file_path)
    
    if fail_xml_files:
        print("무결성 검증에 실패한 파일 다운로드를 재시도합니다.")
        re_download_and_verify(fail_xml_files)    
    
# 파일에 대한 MD5 해시 계산
def calculate_md5(file_path):
    with open(file_path, "rb") as file:
        data = file.read()  # 파일 전체를 한 번에 읽음
    return hashlib.md5(data).hexdigest()  # 파일의 내용으로 MD5 계산

# 파일의 MD5 해시가 기대한 MD5 값과 일치하는지 확인
def verify_md5(file_path, md5_file_path):
    # Calculate the actual file's MD5 hash
    actual_md5 = calculate_md5(file_path).strip()

    # Read the expected MD5 hash from the file
    with open(md5_file_path, "r") as md5_file:
        expected_md5_line = md5_file.read().strip()
        # Extract only the MD5 hash value
        expected_md5 = expected_md5_line.split('=')[-1].strip()

    # Compare the MD5 hashes
    is_match = actual_md5 == expected_md5
    if is_match:
        print(f"MD5 verification successful for {file_path}. MD5: {actual_md5}")
    else:
        print(f"MD5 verification failed for {file_path}. Calculated MD5: {actual_md5}, Expected MD5: {expected_md5}")
    
    return is_match

def init_call_md5(xml_file_names):
    # 파일 경로 설정
    folder_path = "save_files"
    success_xml_files = []
    fail_xml_files = []

    for xml_file_name in xml_file_names:
        file_path = os.path.join(folder_path, xml_file_name)
        md5_file_path = os.path.join(folder_path, f"{xml_file_name}.md5")

        # MD5 검증 수행
        if verify_md5(file_path, md5_file_path):
            success_xml_files.append(xml_file_name)
        else:
            fail_xml_files.append(xml_file_name)
    return success_xml_files, fail_xml_files

# FTP에서 파일 다운로드
def ftp_download():
    # FTP 서버 설정
    ftp_url = "ftp.ncbi.nlm.nih.gov"
    ftp_directory = "/pubmed/updatefiles/"

    # FTP 서버에 연결
    ftp = FTP(ftp_url)
    ftp.login()

    # 디렉토리 변경
    ftp.cwd(ftp_directory)

    # 파일 목록 가져오기
    file_list = ftp.nlst()

    # 로컬 디렉토리 설정
    local_directory = "save_files"
    os.makedirs(local_directory, exist_ok=True)

    # XML 파일 목록 초기화
    xml_file_names = []

    # 파일 다운로드
    for file_name in file_list:
        local_file_path = os.path.join(local_directory, file_name)

        # "xml.gz"로 끝나는 파일 저장
        if file_name.endswith("xml.gz"):
            xml_file_names.append(file_name)

        # 파일이 이미 존재하는지 확인
        if os.path.exists(local_file_path):
            continue

        # 파일 다운로드
        with open(local_file_path, 'wb') as local_file:
            ftp.retrbinary('RETR ' + file_name, local_file.write)

    ftp.quit()
    print(xml_file_names)
    print("파일 다운로드 완료.")
    return xml_file_names

def write_list_to_file(file_list, file_path):
    with open(file_path, 'w') as file:
        for item in file_list:
            file.write(item + '\n')
            

def re_download_and_verify(file_names):
    for file_name in file_names:
        print(f"{file_name} 재다운로드 중...")
        ftp_re_download(file_name)
        file_path = os.path.join("save_files", file_name)
        md5_file_path = os.path.join("save_files", f"{file_name}.md5")
        if verify_md5(file_path, md5_file_path):
            print(f"재검증 성공: {file_name}")
        else:
            print(f"재검증 실패: {file_name}")

def ftp_re_download(file_name):
    # FTP 서버 설정
    ftp_url = "ftp.ncbi.nlm.nih.gov"
    ftp_directory = "/pubmed/updatefiles/"

    # 로컬 저장 경로 설정
    local_directory = "save_files"

    # FTP 서버에 연결
    ftp = FTP(ftp_url)
    ftp.login()

    # 디렉토리 변경
    ftp.cwd(ftp_directory)

    # 로컬 파일 경로 설정
    local_file_path = os.path.join(local_directory, file_name)

    # 파일 다운로드
    with open(local_file_path, 'wb') as local_file:
        ftp.retrbinary('RETR ' + file_name, local_file.write)

    ftp.quit()
    print(f"{file_name} 재다운로드 완료.")




## 파싱 및 unzie 함수 ##################################################
# MariaDB 연결 설정
logging.basicConfig(filename='parsing_errors.log', level=logging.ERROR)
db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '20092021',
    'database': 'mydatabase'
}

def save_results_to_db(start_time, end_time, duration, success_count, fail_count):
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO parsing_results (start_time, end_time, duration, success_count, fail_count)
            VALUES (%s, %s, %s, %s, %s)
        """, (start_time, end_time, duration, success_count, fail_count))
        conn.commit()
    except mysql.connector.Error as e:
        print(f"MariaDB에 데이터 저장 중 오류 발생: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def save_articles_to_db(articles_data):
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.executemany("""
            INSERT INTO parsed_data (PMID, ArticleTitle, Language, JournalTitle, ISSN, PubDate, DateRevised, Authors)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, articles_data)
        conn.commit()
    except mysql.connector.Error as e:
        print(f"MariaDB에 데이터 저장 중 오류 발생: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def decompress_gz_files():
    source_folder = 'save_files'
    target_folder = 'unzip_xmls'
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    for file in os.listdir(source_folder):
        if file.endswith('.gz'):
            gz_file_path = os.path.join(source_folder, file)
            xml_file_name = file[:-3]  # .gz 확장자를 제거하여 xml 파일 이름을 얻습니다.
            decompressed_file_path = os.path.join(target_folder, xml_file_name)

            # 이미 압축 해제된 파일은 건너뜁니다.
            if os.path.exists(decompressed_file_path):
                print(f'"{xml_file_name}" 파일은 이미 압축 해제되었습니다.')
                continue

            # Try-except block to handle potential gzip errors
            try:
                with gzip.open(gz_file_path, 'rb') as gz_file:
                    with open(decompressed_file_path, 'wb') as decompressed_file:
                        decompressed_file.write(gz_file.read())
                    print(f'"{xml_file_name}"이(가) 압축 해제되어 "{target_folder}" 폴더에 저장되었습니다.')
            except gzip.BadGzipFile:
                print(f'오류: "{file}"은(는) 유효한 GZIP 파일이 아닙니다.')


def check_parsed_files():
    parsed_files = set()
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS parsing_filename (filename VARCHAR(255), status VARCHAR(10), PRIMARY KEY(filename))")
        cursor.execute("SELECT filename FROM parsing_filename WHERE status = 'success'")
        parsed_files = {row[0] for row in cursor.fetchall()}
    except mysql.connector.Error as e:
        print(f"파싱 파일 확인 중 오류 발생: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()
    return parsed_files

def update_parsing_status(filename, status):
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO parsing_filename (filename, status) VALUES (%s, %s) ON DUPLICATE KEY UPDATE status = %s", (filename, status, status))
        conn.commit()
    except mysql.connector.Error as e:
        print(f"파싱 상태 업데이트 중 오류 발생: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

def process_xml_file(xml_file, parsed_files):
    
    xml_file_path = os.path.join('unzip_xmls', xml_file)
    success_count = 0  # 성공 카운트 변수 초기화
    if xml_file in parsed_files:  # 이미 처리된 파일 건너뛰기
        return 0, 0
    if not os.path.exists(xml_file_path):
        print(f'"{xml_file}" 파일을 찾을 수 없습니다.')
        update_parsing_status(xml_file, 'fail')  # 상태 업데이트 추가
        return 0, 1

    if os.path.getsize(xml_file_path) == 0:
        print(f'"{xml_file}" 파일은 비어 있습니다.')
        update_parsing_status(xml_file, 'fail')  # 상태 업데이트 추가
        return 0, 1

    try:
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        articles_data = []

        for article in root.findall('.//PubmedArticle'):
            pmid = article.find('.//PMID').text
            article_title = article.find('.//ArticleTitle').text
            language = article.find('.//Language').text if article.find('.//Language') is not None else 'Unknown'
            journal_title = article.find('.//Journal/Title').text
            issn = article.find('.//ISSN').text if article.find('.//ISSN') is not None else 'Unknown'
            pub_date = article.find('.//PubDate/Year').text if article.find('.//PubDate/Year') is not None else 'Unknown'
            date_revised = article.find('.//DateRevised')
            if date_revised is not None:
                date_revised = f"{date_revised.find('Year').text}-{date_revised.find('Month').text.zfill(2)}-{date_revised.find('Day').text.zfill(2)}"
            else:
                date_revised = 'Unknown'
            authors = [f"{author.find('ForeName').text if author.find('ForeName') is not None else 'N/A'} {author.find('LastName').text if author.find('LastName') is not None else 'N/A'}" for author in article.findall('.//Author')]

            # 기사 데이터를 articles_data 리스트에 추가
            articles_data.append((
                pmid,
                article_title,
                language,
                journal_title,
                issn,
                pub_date,
                date_revised,
                ', '.join(authors)
            ))
            success_count += 1  # 성공 카운트 증가

        if articles_data:
            save_articles_to_db(articles_data)
            update_parsing_status(xml_file, 'success')  # 성공 시 상태 업데이트
            print(f'"{xml_file}" 파일 파싱 완료. 성공 {len(articles_data)}')
            return len(articles_data), 0
        else:
            update_parsing_status(xml_file, 'fail')  # 데이터 없음에 대한 실패 처리
            return 0, 1

    except ET.ParseError as e:
        logging.error(f'파싱 실패: {xml_file}, 오류: {e}')
        print(f'"{xml_file}" 파일 파싱 중 오류 발생: {e}')
        return 0, 1  # 성공 카운트 0, 실패 카운트 1 반환

def parse_xml_files():
    parsed_files = check_parsed_files()
    xml_files = [f for f in os.listdir('unzip_xmls') if f.endswith(".xml") and f not in parsed_files]
    
    # 디버깅을 위해 파싱 대상 파일 목록 출력
    print(f"새롭게 추가되거나 오류가 생겨, 파싱할 파일 목록: {xml_files}")

    if not xml_files:
        print("파싱할 파일이 없습니다.")
        return
    
    start_time = datetime.now()  # 파싱 시작 시간 기록
    success_count = 0
    fail_count = 0


    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_xml_file, xml_file, parsed_files) for xml_file in xml_files]
        for future in as_completed(futures):
            success, fail = future.result()
            success_count += success
            fail_count += fail


    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    hours, remainder = divmod(duration, 3600)
    minutes, seconds = divmod(remainder, 60)

    print(f"파싱 완료: 성공 {success_count}, 실패 {fail_count}") # 파싱에 성공한 파일과 실패한 파일의 갯수를 출력줍니다.
    print(f"파싱 총 소요 시간: {int(hours)}시간 {int(minutes)}분 {int(seconds)}초") # 파싱에 걸린 시간을 출력합니다.
    print(f"파싱 시작 시간: {start_time.strftime('%Y-%m-%d %H:%M:%S')}") # 파싱 시작 시간을 출력합니다.
    print(f"파싱 종료 시간: {end_time.strftime('%Y-%m-%d %H:%M:%S')}") # 파싱 종료 시간을 출력합니다.
    # 결과를 데이터베이스에 저장합니다.
    save_results_to_db(start_time, end_time, duration, success_count, fail_count)


def unzip_main():
    decompress_gz_files()
    parse_xml_files()
    print("파싱 작업이 완료되었습니다.")


## SQL 데이터 받아오는 함수 #######################################



## Flask ##########################################################

resultSql = "1000"

# 기본 화면
@app.route("/")
def main():
    return render_template("index.html", resultSql=resultSql)

# 앞에서 작성한 경로를 여기안에 넣기
@app.route("/hola1")
def hola1():
    test()
    print("완료")
    return "완료했습니다"


# 2 route안에 주소 넣기
@app.route("/hola2")
# 3 def 옆에 주소 넣기
def hola2():
    down()
    data = 10
    # 5 결과물 return하기
    return f"{data}"


# 2 route안에 주소 넣기
@app.route("/hola3")
# 3 def 옆에 주소 넣기
def hola3():
    unzip_main()
    
    # db search

    return f"for(<div><a href='논문검색주소/{본문번호}'>논문제목</a></div>)"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5500, debug=False)