import subprocess

def run_script(script_name):
    try:
        subprocess.run(["python", script_name], check=True)
        print(f"{script_name} 실행 완료.")
    except subprocess.CalledProcessError as e:
        print(f"{script_name} 실행 중 오류 발생: {e}")

def main():
    # down_updatefiles_V3.py 스크립트 실행
    run_script("make_test_file.py") #md5 검증 알고리즘 확인용 파일 생성
    
    run_script("down_updatefiles_V3.py") #FTP 서버에서 파일을 다운로드받고, MD5 검증을 실행함.

    # parse_auto_unzip.py 스크립트 실행
    run_script("parse_sql_autounzip.py") #MD5 검증이 완료된 파일에 한해 압축 해제 및 

if __name__ == "__main__":
    main()
