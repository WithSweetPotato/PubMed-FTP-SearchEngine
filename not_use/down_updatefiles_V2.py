from ftplib import FTP
import os
import hashlib


def main():
    # FTP에서 XML 파일 다운로드
    xml_file_names = ftp_download()
    
    # 테스트용 성공 데이터 추가
    xml_file_names.append("example.xml.gz")
    xml_file_names.append("example1.xml.gz")

    # MD5 검증 수행
    success_xml_files, fail_xml_files = init_call_md5(xml_file_names)
    print(f"성공한 XML 파일들 : {success_xml_files}")
    print(f"실패한 XML 파일들 : {fail_xml_files}")
    # 결과를 텍스트 파일에 저장
    success_file_path = os.path.join(".", "save_result", "success_xml_list.txt")
    fail_file_path = os.path.join(".", "save_result", "fail_xml_list.txt")

    write_list_to_file(success_xml_files, success_file_path)
    write_list_to_file(fail_xml_files, fail_file_path)

    

# 파일에 대한 MD5 해시 계산
def calculate_md5(file_path):
    with open(file_path, "rb") as file:
        data = file.read()  # 파일 전체를 한 번에 읽음
    return hashlib.md5(data).hexdigest()  # 파일의 내용으로 MD5 계산

# 파일의 MD5 해시가 기대한 MD5 값과 일치하는지 확인
def verify_md5(file_path, md5_file_path):
    # Calculate the actual file's MD5 hash
    actual_md5 = calculate_md5(file_path).strip()

    # Read the expected MD5 hash from the file
    with open(md5_file_path, "r") as md5_file:
        expected_md5_line = md5_file.read().strip()
        # Extract only the MD5 hash value
        expected_md5 = expected_md5_line.split('=')[-1].strip()

    # Compare the MD5 hashes
    is_match = actual_md5 == expected_md5
    if is_match:
        print(f"MD5 verification successful for {file_path}. MD5: {actual_md5}")
    else:
        print(f"MD5 verification failed for {file_path}. Calculated MD5: {actual_md5}, Expected MD5: {expected_md5}")
    
    return is_match

def init_call_md5(xml_file_names):
    # 파일 경로 설정
    folder_path = "save_files"
    success_xml_files = []
    fail_xml_files = []

    for xml_file_name in xml_file_names:
        file_path = os.path.join(folder_path, xml_file_name)
        md5_file_path = os.path.join(folder_path, f"{xml_file_name}.md5")

        # MD5 검증 수행
        if verify_md5(file_path, md5_file_path):
            success_xml_files.append(xml_file_name)
        else:
            fail_xml_files.append(xml_file_name)
    return success_xml_files, fail_xml_files

# FTP에서 파일 다운로드
def ftp_download():
    # FTP 서버 설정
    ftp_url = "ftp.ncbi.nlm.nih.gov"
    ftp_directory = "/pubmed/updatefiles/"

    # FTP 서버에 연결
    ftp = FTP(ftp_url)
    ftp.login()

    # 디렉토리 변경
    ftp.cwd(ftp_directory)

    # 파일 목록 가져오기
    file_list = ftp.nlst()

    # 로컬 디렉토리 설정
    local_directory = "save_files"
    os.makedirs(local_directory, exist_ok=True)

    # XML 파일 목록 초기화
    xml_file_names = []

    # 파일 다운로드
    for file_name in file_list:
        local_file_path = os.path.join(local_directory, file_name)

        # "xml.gz"로 끝나는 파일 저장
        if file_name.endswith("xml.gz"):
            xml_file_names.append(file_name)

        # 파일이 이미 존재하는지 확인
        if os.path.exists(local_file_path):
            continue

        # 파일 다운로드
        with open(local_file_path, 'wb') as local_file:
            ftp.retrbinary('RETR ' + file_name, local_file.write)

    ftp.quit()
    print(xml_file_names)
    print("파일 다운로드 완료.")
    return xml_file_names

def write_list_to_file(file_list, file_path):
    with open(file_path, 'w') as file:
        for item in file_list:
            file.write(item + '\n')
main()
