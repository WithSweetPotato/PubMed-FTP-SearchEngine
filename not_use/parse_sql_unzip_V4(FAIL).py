import mysql.connector
import gzip
import os
import xml.etree.ElementTree as ET
from datetime import datetime
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

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
    
    
    
def fetch_success_filenames():
    try:
        # db_config를 사용하여 데이터베이스에 연결
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # 파싱에 성공한 파일 이름 조회
        cursor.execute("SELECT filename FROM parsing_filename WHERE status = 'success'")
        success_files = cursor.fetchall()

        # 파싱에 성공한 파일 이름 출력
        print("파싱에 성공한 파일들:")
        for (filename,) in success_files:
            print(filename)

        return {filename[0] for filename in success_files}

    except mysql.connector.Error as e:
        print(f"데이터베이스 에러: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()



def parse_xml_files():
    parsed_files = check_parsed_files()
    xml_files = [f for f in os.listdir('unzip_xmls') if f.endswith(".xml") and f not in parsed_files]


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
    print(f"총 소요 시간: {int(hours)}시간 {int(minutes)}분 {int(seconds)}초") # 파싱에 걸린 시간을 출력합니다.
    print(f"파싱 시작 시간: {start_time.strftime('%Y-%m-%d %H:%M:%S')}") # 파싱 시작 시간을 출력합니다.
    print(f"파싱 종료 시간: {end_time.strftime('%Y-%m-%d %H:%M:%S')}") # 파싱 종료 시간을 출력합니다.
    # 결과를 데이터베이스에 저장합니다.
    save_results_to_db(start_time, end_time, duration, success_count, fail_count)


def main():
    decompress_gz_files()
    parse_xml_files()
    print("파싱 작업이 완료되었습니다.")

if __name__ == "__main__":
    main()
