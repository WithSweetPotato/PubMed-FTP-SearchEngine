def process_xml_file(xml_file):
    xml_file_path = os.path.join('unzip_xmls', xml_file)

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
        # 기사 데이터 추출 및 articles_data 리스트에 추가하는 코드...
        
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
        update_parsing_status(xml_file, 'fail')  # 예외 발생 시 실패 처리
        return 0, 1
