from ftplib import FTP
import os
import hashlib

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

# MD5 검증 및 재다운로드 필요 파일 목록 반환
def verify_and_redownload(xml_file_names):
    success_xml_files = []
    need_redownload_files = []

    for xml_file_name in xml_file_names:
        file_path = os.path.join("save_files", xml_file_name)
        md5_file_path = os.path.join("save_files", f"{xml_file_name}.md5")

        # MD5 검증
        if verify_md5(file_path, md5_file_path):
            success_xml_files.append(xml_file_name)
        else:
            need_redownload_files.append(xml_file_name)
    
    return success_xml_files, need_redownload_files

# 재다운로드 및 최종 검증
def final_verification(need_redownload_files):
    updated_success_files = []
    updated_fail_files = []

    for file_name in need_redownload_files:
        print(f"{file_name} 재다운로드 중...")
        ftp_re_download(file_name)
        file_path = os.path.join("save_files", file_name)
        md5_file_path = os.path.join("save_files", f"{file_name}.md5")

        if verify_md5(file_path, md5_file_path):
            updated_success_files.append(file_name)
        else:
            updated_fail_files.append(file_name)
    
    return updated_success_files, updated_fail_files

# FTP에서 파일 재다운로드
def ftp_re_download(file_name):
    # FTP 서버 설정
    ftp_url = "ftp.ncbi.nlm.nih.gov"
    ftp_directory = "/pubmed/updatefiles/"

    # 로컬 저장 경로 설정
    local_directory = "save_files"

    # FTP 서버에 연결
    ftp = FTP(ftp_url)
    ftp.login()

    # 디렉토리 변경
    ftp.cwd(ftp_directory)

    # 로컬 파일 경로 설정
    local_file_path = os.path.join(local_directory, file_name)

    # 파일 다운로드
    with open(local_file_path, 'wb') as local_file:
        ftp.retrbinary('RETR ' + file_name, local_file.write)

    ftp.quit()
    print(f"{file_name} 재다운로드 완료.")

def main():
    # 테스트용 XML 파일 목록
    xml_file_names = ["example.xml.gz", "example1.xml.gz"]

    # 초기 MD5 검증 및 재다운로드 필요 파일 목록 반환
    success_xml_files, need_redownload_files = verify_and_redownload(xml_file_names)

    # 재다운로드 및 최종 검증
    updated_success_files, updated_fail_files = final_verification(need_redownload_files)

    # 최종 결과 출력
    if updated_success_files:
        print(f"성공한 XML 파일들: {updated_success_files}")
    else:
        print("성공한 XML 파일이 하나도 없습니다.")
    
    if updated_fail_files:
        print(f"실패한 XML 파일들: {updated_fail_files}")
    else:
        print("모두 성공했습니다.")

main()
