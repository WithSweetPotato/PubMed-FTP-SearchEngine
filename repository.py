def parse_xml_files():
    # 데이터베이스 연결 설정
    db_config = {
        'host': '127.0.0.1',
        'user': 'root',
        'password': '20092021',
        'database': 'mydatabase'
    }

    # 데이터베이스 연결 및 쿼리 실행
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # 파싱에 성공한 파일 이름 조회
        cursor.execute("SELECT filename FROM parsing_filename WHERE status = 'success'")
        success_files = cursor.fetchall()  # 조회 결과를 모두 가져옵니다.
        
        # 파싱에 성공한 파일 이름 출력
        print("파싱에 성공한 파일들:")
        for (filename,) in success_files:
            print(filename)
        
        # 파싱할 파일 목록 준비
        parsed_files = {filename for (filename,) in success_files}  # 성공한 파일 목록을 집합으로 변환
        all_xml_files = [f for f in os.listdir('unzip_xmls') if f.endswith(".xml")]  # unzip_xmls 폴더 내 모든 XML 파일 목록을 가져옵니다.

        if not all_xml_files:
            print("파싱할 파일이 없습니다.")
            return

        start_time = datetime.now()  # 파싱 시작 시간 기록

        success_count = 0
        fail_count = 0

        with ThreadPoolExecutor() as executor:
            futures = []
            for xml_file in all_xml_files:
                if xml_file in parsed_files:
                    continue  # 이미 파싱된 파일은 건너뜁니다.

                # 아직 파싱되지 않은 파일에 대해 파싱 작업을 예약합니다.
                futures.append(executor.submit(process_xml_file, xml_file, parsed_files))

            for future in as_completed(futures):
                success, fail = future.result()
                success_count += success
                fail_count += fail

        end_time = datetime.now()  # 파싱 종료 시간 기록
        # 파싱 결과 요약 등 추가적인 로직...

    except mysql.connector.Error as e:
        print(f"데이터베이스 에러: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
