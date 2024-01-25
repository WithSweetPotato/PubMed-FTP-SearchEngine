from ftplib import FTP
import os
import hashlib

def main():
    
    xml_file_names = ftp_download()
    
    # FTP에서 XML 파일 다운로드 및 테스트용 성공 데이터 추가
    xml_file_names.append("example.xml.gz")
    xml_file_names.append("example1.xml.gz")

    # MD5 검증 수행
    success_xml_files, fail_xml_files = init_call_md5(xml_file_names)
    print(f"success_xml_files : {success_xml_files}")
    print(f"fail_xml_files : {fail_xml_files}")
    
    # MD5 검증 수행
    success_xml_files, fail_xml_files = init_call_md5(xml_file_names)

    # 결과를 텍스트 파일에 저장
    success_file_path = os.path.join(".", "save_result", "success_xml_list.txt")
    fail_file_path = os.path.join(".", "save_result", "fail_xml_list.txt")

    write_list_to_file(success_xml_files, success_file_path)
    write_list_to_file(fail_xml_files, fail_file_path)


# 주어진 파일에 대한 MD5 해시 계산
def calculate_md5(file_path):
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as file:
        # 4K 블록 단위로 읽어들이며 해시 업데이트
        for byte_block in iter(lambda: file.read(4096), b""):
            md5_hash.update(byte_block)
    return md5_hash.hexdigest()

# 파일의 MD5 해시가 제공된 MD5 파일의 값과 일치하는지 확인
def verify_md5(file_path, md5_file_path):
    # 실제 파일의 MD5 해시 계산
    actual_md5 = calculate_md5(file_path)

    # MD5 파일에서 MD5 해시 읽기
    with open(md5_file_path, "r") as md5_file:
        expected_md5 = md5_file.read().strip()

    # 계산된 MD5 해시와 예상 값 비교
    return actual_md5 == expected_md5

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
            print(f"MD5 verification successful for {xml_file_name}")
            success_xml_files.append(xml_file_name)
        else:
            print(f"MD5 verification failed for {xml_file_name}")
            fail_xml_files.append(xml_file_name)
    return success_xml_files, fail_xml_files

# FTP에서 파일 다운로드
def ftp_download():
    ftp_url = "ftp.ncbi.nlm.nih.gov"
    ftp_directory = "/pubmed/baseline/"

    # FTP 서버에 연결
    ftp = FTP(ftp_url)
    ftp.login()

    # 디렉토리 변경
    ftp.cwd(ftp_directory)

    # 현재 디렉토리의 파일 목록 얻기
    file_list = ftp.nlst()

    # 다운로드할 로컬 디렉토리 설정
    local_directory = "save_files"
    os.makedirs(local_directory, exist_ok=True)

    # XML 파일명을 저장할 배열 초기화
    xml_file_names = []

    # 각 파일을 다운로드
    for file_name in file_list:
        local_file_path = os.path.join(local_directory, file_name)

        # "xml.gz"로 끝나는 경우 배열에 저장
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
    print("Files downloaded successfully.")
    return xml_file_names



def write_list_to_file(file_list, file_path):
    with open(file_path, 'w') as file:
        for item in file_list:
            file.write(item + '\n')

main()






