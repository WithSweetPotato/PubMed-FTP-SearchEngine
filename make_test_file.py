import hashlib

# 테스트 파일 1: example.xml.gz
file_content_1 = b"This is the content of example.xml.gz"
file_path_1 = "save_files/example.xml.gz"
md5_hash_1 = hashlib.md5(file_content_1).hexdigest()

# 테스트 파일 2: example1.xml.gz
file_content_2 = b"This is the content of example1.xml.gz"
file_path_2 = "save_files/example1.xml.gz"
md5_hash_2 = hashlib.md5(file_content_2).hexdigest()

# MD5 파일 생성
with open("save_files/example.xml.gz.md5", "w") as md5_file_1:
    md5_file_1.write(md5_hash_1)

with open("save_files/example1.xml.gz.md5", "w") as md5_file_2:
    md5_file_2.write(md5_hash_2)

# 실제 파일 생성
with open(file_path_1, "wb") as file_1:
    
    
    
    file_1.write(file_content_1)

with open(file_path_2, "wb") as file_2:
    file_2.write(file_content_2)