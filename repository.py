# process_xml_file 함수의 예시 반환
def process_xml_file(xml_file):
    # 처리 로직...
    # 예시 반환 값
    return success_count, fail_count

# parse_xml_files 함수 내에서 결과 처리
def parse_xml_files():
    # 기존 코드...
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_xml_file, xml_file): xml_file for xml_file in xml_files}

        for future in as_completed(futures):
            success, fail = future.result()  # 튜플의 인덱스를 사용하여 값을 추출
            xml_file = futures[future]
            print(f'"{xml_file}" 파일 파싱 완료. 성공 {success}, 실패 {fail}')
            success_count += success
            fail_count += fail
    # 기존 코드...
