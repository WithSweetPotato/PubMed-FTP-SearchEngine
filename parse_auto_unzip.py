import gzip
import os
import json
import xml.etree.ElementTree as ET

def decompress_gz_files():
    source_folder = 'save_files'
    target_folder = 'unzip_xmls'
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    # .gz 확장자를 가진 모든 파일에 대해 반복
    for file in os.listdir(source_folder):
        if file.endswith('.gz'):
            gz_file_path = os.path.join(source_folder, file)
            decompressed_file_path = os.path.join(target_folder, file[:-3])

########################################
            try:
                with gzip.open(gz_file_path, 'rb') as gz_file:
                    with open(decompressed_file_path, 'wb') as decompressed_file:
                        decompressed_file.write(gz_file.read())
                print(f'"{file[:-3]}"이(가) 압축해제되어 "{target_folder}" 폴더에 저장되었습니다.')
            except gzip.BadGzipFile:
                print(f'오류: "{file}"은(는) 유효한 GZIP 파일이 아닙니다.')

#####################################

            # with gzip.open(gz_file_path, 'rb') as gz_file:
            #     with open(decompressed_file_path, 'wb') as decompressed_file:
            #         decompressed_file.write(gz_file.read())

            # # 파일 이름 출력을 위해 .gz 확장자 제거
            # decompressed_file_name = file[:-3]
            # print(f'"{decompressed_file_name}"이(가) 압축해제되어 "{target_folder}" 폴더에 저장되었습니다.')
            # #print(f'압축 해제 완료: {file}')

def parse_xml_files():
    unzip_folder = 'unzip_xmls'
    parsed_folder = 'parsed_xmls'
    
    if not os.path.exists(parsed_folder):
        os.makedirs(parsed_folder)
        
    for xml_file in os.listdir(unzip_folder):
        if xml_file.endswith(".xml"):
            xml_file_path = os.path.join(unzip_folder, xml_file)
            output_file_path = os.path.join(parsed_folder, f"parsed_{xml_file[:-4]}.json")
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
            print(f'"{xml_file}" Parsing completed.')

def main():
    decompress_gz_files()
    parse_xml_files()
    print("All XML files in 'unzip_xmls' have been successfully parsed.")

main()
