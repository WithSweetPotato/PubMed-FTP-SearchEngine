def parse_xml_files():
    unzip_folder = 'unzip_xmls'
    parsed_folder = 'parsed_xmls'


    if not os.path.exists(parsed_folder):
        os.makedirs(parsed_folder)

    for xml_file in os.listdir(unzip_folder):
        if xml_file.endswith(".xml"):
            xml_file_path = os.path.join(unzip_folder, xml_file)
            output_file_path = os.path.join(parsed_folder, f"parsed_{xml_file[:-4]}.json")

            # 파일이 비어 있는지 확인하고, 비어 있으면 건너뜁니다.
            if os.path.getsize(xml_file_path) == 0:
                print(f'"{xml_file}" 파일은 비어 있습니다.')
                continue

            try:
                tree = ET.parse(xml_file_path)
                root = tree.getroot()
                articles_data = []

                # XML 파일 파싱 로직...
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

            except ET.ParseError as e:
                print(f'"{xml_file}" 파일 파싱 중 오류 발생: {e}')
