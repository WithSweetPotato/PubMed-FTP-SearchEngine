# Import hashlib library (md5 method is part of it)
import hashlib

# File to check
file_name = 'pubmed24n1263.xml.gz'

# Correct original md5 goes here
original_md5 = 'fa2125d2a736cb9df74b9bbb364c74f5'  

# Open,close, read file and calculate MD5 on its contents 
with open(file_name, 'rb') as file_to_check:
    # read contents of the file
    data = file_to_check.read()    
    # pipe contents of the file through
    md5_returned = hashlib.md5(data).hexdigest()

# Finally compare original MD5 with freshly calculated
if original_md5 == md5_returned:
    print ("MD5 verified.")
else:
    print ("MD5 verification failed!.")