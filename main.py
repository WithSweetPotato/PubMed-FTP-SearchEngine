import subprocess

def run_script(script_name):
    try:
        subprocess.run(["python", script_name], check=True)
        print(f"{script_name} 실행 완료.")
    except subprocess.CalledProcessError as e:
        print(f"{script_name} 실행 중 오류 발생: {e}")

def main():
    # down_updatefiles_V3.py 스크립트 실행
    run_script("make_test_file.py")
    run_script("down_updatefiles_V3.py")

    # parse_auto_unzip.py 스크립트 실행
    run_script("parse_auto_unzip.py")

if __name__ == "__main__":
    main()
