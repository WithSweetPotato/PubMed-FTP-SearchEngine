import json
import xml.etree.ElementTree as ET
import os

# 결과를 기록할 변수 초기화
success_count = 0
failed_files = []

# "unzip_xmls" 폴더 내의 모든 XML 파일에 대해 반복
for xml_file in os.listdir("./unzip_xmls"):
    if xml_file.endswith(".xml"):
        try:
            # XML 파일 경로 설정
            xml_file_path = os.path.join(".", "unzip_xmls", xml_file)

            # "parsed_xmls" 폴더가 없으면 생성
            if not os.path.exists("./parsed_xmls"):
                os.makedirs("./parsed_xmls")

            # 결과를 저장할 JSON 파일 경로 설정 ("parsed_xmls" 폴더 내)
            output_json_file = f"parsed_{xml_file[:-4]}.json"
            output_file_path = os.path.join(".", "parsed_xmls", output_json_file)

            # 해당 JSON 파일이 이미 존재하는지 확인
            if os.path.exists(output_file_path):
                print(f'"{output_json_file}" already exists. Skipping parsing.')
                continue

            # XML 파일 파싱
            tree = ET.parse(xml_file_path)
            root = tree.getroot()

            # 추출한 데이터를 저장할 리스트
            articles_data = []

            # XML에서 정보 추출
            for article in root.findall('.//PubmedArticle'):
                # (데이터 추출 과정)
                # 추출한 정보 저장
                articles_data.append({
                    # (데이터 구조)
                })

            # JSON 파일로 데이터 저장
            with open(output_file_path, 'w', encoding='utf-8') as f:
                json.dump(articles_data, f, ensure_ascii=False, indent=4)

            success_count += 1

        except Exception as e:
            failed_files.append(xml_file)
            print(f'Error parsing "{xml_file}": {e}')

# 결과를 HTML 파일에 기록
html_output_path = './index.html'
with open(html_output_path, 'w', encoding='utf-8') as f:
    # HTML 시작
    f.write('<html><head><title>Parsing Results</title><style>')
    f.write('body { font-family: Arial, sans-serif; margin: 20px; }')
    f.write('.success { color: green; }')
    f.write('.failure { color: red; }')
    f.write('.summary { font-size: 16px; }')
    f.write('</style></head><body>')
    
    # 요약 정보
    if success_count == 0:
        f.write('<div class="summary failure">성공한 파일이 하나도 없습니다.</div>')
    elif len(failed_files) == 0:
        f.write('<div class="summary success">모두 성공했습니다.</div>')
    else:
        f.write(f'<div class="summary success">{success_count} 파일이 성공적으로 파싱되었습니다.</div>')
        f.write(f'<div class="summary failure">실패한 파일: {", ".join(failed_files)}</div>')

    # HTML 끝
    f.write('</body></html>')

print("All XML files in 'unzip_xmls' have been processed. Check the 'index.html' for results.")
