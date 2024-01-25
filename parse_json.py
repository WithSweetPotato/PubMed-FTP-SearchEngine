import json
import xml.etree.ElementTree as ET
import os

# XML 파일 경로 설정
xml_file_path = os.path.join(".", "unzip_xmls", "pubmed24n1220.xml")

# 결과를 저장할 JSON 파일 경로 설정
output_file_path = os.path.join(".", "parsed_articles.json")

# XML 파일 파싱
tree = ET.parse(xml_file_path)
root = tree.getroot()

# 추출한 데이터를 저장할 리스트
articles_data = []

# XML에서 정보 추출
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

    # 추출한 정보 저장
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

# JSON 파일로 데이터 저장
with open(output_file_path, 'w', encoding='utf-8') as f:
    json.dump(articles_data, f, ensure_ascii=False, indent=4)
