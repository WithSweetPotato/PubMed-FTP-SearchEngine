import mysql.connector
import gzip
import os
import json
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

# MariaDB에 결과 저장
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
        # 일괄 삽입을 위해 executemany 메서드를 사용
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
            conn.close()

def decompress_gz_files():
    source_folder = 'save_files'
    target_folder = 'unzip_xmls'
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    for file in os.listdir(source_folder):
        if file.endswith('.gz'):
            gz_file_path = os.path.join(source_folder, file)
            decompressed_file_path = os.path.join(target_folder, file[:-3])

            try:
                with gzip.open(gz_file_path, 'rb') as gz_file:
                    with open(decompressed_file_path, 'wb') as decompressed_file:
                        decompressed_file.write(gz_file.read())
                print(f'"{file[:-3]}"이(가) 압축해제되어 "{target_folder}" 폴더에 저장되었습니다.')
            except gzip.BadGzipFile:
                print(f'오류: "{file}"은(는) 유효한 GZIP 파일이 아닙니다.')

def process_xml_file(xml_file):
    xml_file_path = os.path.join('unzip_xmls', xml_file)

    if not os.path.exists(xml_file_path):
        print(f'"{xml_file}" 파일을 찾을 수 없습니다.')
        return 0, 1  # 성공 카운트 0, 실패 카운트 1 반환

    if os.path.getsize(xml_file_path) == 0:
        print(f'"{xml_file}" 파일은 비어 있습니다.')
        return 0, 1  # 성공 카운트 0, 실패 카운트 1 반환

    match = re.search(r'\d+', xml_file)
    if match is None:
        print(f'"{xml_file}" 파일 이름에서 숫자를 찾을 수 없습니다.')
        return 0, 1

    number = int(match.group())
    try:
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        success_count = 0
        fail_count = 0

        articles_data = []  # 기사 데이터를 모을 리스트 생성

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

        # articles_data를 데이터베이스에 일괄 삽입
        save_articles_to_db(articles_data)

        print(f'"{xml_file}" 파일 파싱 완료. 성공 {success_count}, 실패 {fail_count}')
        return success_count, fail_count

    except ET.ParseError as e:
        logging.error(f'파싱 실패: {xml_file}, 오류: {e}')
        print(f'"{xml_file}" 파일 파싱 중 오류 발생: {e}')
        return 0, 1  # 성공 카운트 0, 실패 카운트 1 반환

def parse_xml_files():
    unzip_folder = 'unzip_xmls'
    xml_files = [xml_file for xml_file in os.listdir(unzip_folder) if xml_file.endswith(".xml")]
    xml_files.sort(key=lambda x: int(re.search(r'\d+', x).group() if re.search(r'\d+', x) else 0))
    
    start_time = datetime.now()
    success_count = 0
    fail_count = 0

    # 테이블 내용 초기화
    clear_table()

    with ThreadPoolExecutor() as executor:
        # 각 XML 파일에 대한 처리 작업을 스케줄링합니다.
        futures = {executor.submit(process_xml_file, xml_file): xml_file for xml_file in xml_files}

        # as_completed를 사용하여 각 작업의 완료를 기다립니다.
        for future in as_completed(futures):
            success, fail = future.result()  # 작업의 결과를 가져옵니다. 튜플로부터 직접 값을 언패킹합니다.
            xml_file = futures[future]  # 처리된 XML 파일 이름을 가져옵니다.
            #print(f'"{xml_file}" 파일 파싱 완료. 성공 {success}, 실패 {fail}')
            success_count += success
            fail_count += fail

    # end_time = datetime.now()
    # duration = (end_time - start_time).total_seconds()
    # print(f"파싱 완료: 성공 {success_count}, 실패 {fail_count}")
    # print(f"총 소요 시간: {duration}초")
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    hours, remainder = divmod(duration, 3600)
    minutes, seconds = divmod(remainder, 60)

    print(f"파싱 완료: 성공 {success_count}, 실패 {fail_count}")
    print(f"총 소요 시간: {int(hours)}시간 {int(minutes)}분 {int(seconds)}초")
    # 결과를 데이터베이스에 저장합니다.
    save_results_to_db(start_time, end_time, duration, success_count, fail_count)

1q2w3e567
def clear_table():
    """parsed_data 테이블의 모든 데이터를 삭제합니다."""
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM parsed_data")
        conn.commit()
        print("테이블 내용이 초기화되었습니다.")
    except mysql.connector.Error as e:
        print(f"테이블 초기화 중 오류 발생: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def main():
    decompress_gz_files()
    print("압축 해제가 끝났습니다. Parsing을 시작합니다.")
    parse_xml_files()
    print("'unzip_xmls' 폴더의 모든 XML 파일들이 성공적으로 파싱되었습니다.")

if __name__ == "__main__":
    main()
