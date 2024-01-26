import mysql.connector
import gzip
import os
import json
import xml.etree.ElementTree as ET
#import logging
from datetime import datetime

# logging.basicConfig(filename='parsing_errors.log', level=logging.ERROR)
# MariaDB 연결 설정
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '20092021',
    'database': 'mydatabase'
}

# MariaDB에 결과 저장
def save_results_to_db(start_time, end_time, duration, success_count, fail_count, success_files, fail_files):
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO parsing_results_V2 (start_time, end_time, duration, success_count, fail_count, success_files, fail_files)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (start_time, end_time, duration, success_count, fail_count, ','.join(success_files), ','.join(fail_files)))
        conn.commit()
    except mysql.connector.Error as e:
        print(f"MariaDB에 데이터 저장 중 오류 발생: {e}")
    finally:
        if conn.is_connected():
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
            decompressed_file_path = os.path.join(target_folder, file[:-3])

            try:
                with gzip.open(gz_file_path, 'rb') as gz_file:
                    with open(decompressed_file_path, 'wb') as decompressed_file:
                        decompressed_file.write(gz_file.read())
                print(f'"{file[:-3]}"이(가) 압축해제되어 "{target_folder}" 폴더에 저장되었습니다.')
            except gzip.BadGzipFile:
                print(f'오류: "{file}"은(는) 유효한 GZIP 파일이 아닙니다.')

# 
def parse_xml_files():
    unzip_folder = 'unzip_xmls'
    parsed_folder = 'parsed_xmls'
    
    if not os.path.exists(parsed_folder):
        os.makedirs(parsed_folder)

    start_time = datetime.now()
    success_count = 0
    fail_count = 0
    success_files = []  # 성공한 파일 이름을 저장할 리스트
    fail_files = []  # 실패한 파일 이름을 저장할 리스트

    for xml_file in os.listdir(unzip_folder):
        if xml_file.endswith(".xml"):
            xml_file_path = os.path.join(unzip_folder, xml_file)
            output_file_path = os.path.join(parsed_folder, f"parsed_{xml_file[:-4]}.json")

            if os.path.getsize(xml_file_path) == 0:
                print(f'"{xml_file}" 파일은 비어 있습니다.')
                continue

            articles_data = []
            try:
                tree = ET.parse(xml_file_path)
                root = tree.getroot()

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
                    authors = []
                    for author in article.findall('.//Author'):
                        last_name = author.find('LastName').text if author.find('LastName') is not None else 'N/A'
                        fore_name = author.find('ForeName').text if author.find('ForeName') is not None else 'N/A'
                        authors.append(f"{fore_name} {last_name}")
                        
                    articles_data.append({
                        'PMID': pmid,
                        'ArticleTitle': article_title,
                        'Language': language,
                        'JournalTitle': journal_title,
                        'ISSN': issn,
                        'PubDate': pub_date,
                        'DateRevised': date_revised,
                        'Authors': authors
                    })
                with open(output_file_path, 'w', encoding='utf-8') as f:
                    json.dump(articles_data, f, ensure_ascii=False, indent=4)

                print(f'"{xml_file}" 파일 파싱 완료.')

            except ET.ParseError as e:
                #logging.error(f'파싱 실패: {xml_file}, 오류: {e}')
                print(f'"{xml_file}" 파일 파싱 중 오류 발생: {e}')
            try:
                # XML 파일 파싱 시도
                # 파싱 성공 시 success_count 증가
                success_count += 1
            except ET.ParseError as e:
                # 파싱 실패 시 fail_count 증가
                fail_count += 1

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    hours, remainder = divmod(duration, 3600)
    minutes, seconds = divmod(remainder, 60)

    print(f"파싱 완료: 성공 {success_count}, 실패 {fail_count}")
    print(f"총 소요 시간: {int(hours)}시간 {int(minutes)}분 {int(seconds)}초")

    # print(f"파싱 완료: 성공 {success_count}, 실패 {fail_count}")
    # print(f"총 소요 시간: {duration}초")

    # MariaDB에 결과 저장
    save_results_to_db(start_time.strftime('%Y-%m-%d %H:%M:%S'), end_time.strftime('%Y-%m-%d %H:%M:%S'), duration, success_count, fail_count, success_files, fail_files)

def main():
    decompress_gz_files()
    print("압축 해제가 끝났습니다. Parsing을 시작합니다.")
    parse_xml_files()
    print("'unzip_xmls' 폴더의 모든 XML 파일들이 성공적으로 파싱되었습니다.")

main()
