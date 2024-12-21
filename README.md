# PubMed FTP search engine

## This Git repository was created for PubMed FTP search engine

### Topic: PubMed Paper Search System  
### Summary: The task involves parsing medical-related papers and, if necessary, combining them with additional information.  
### Author: Nam HyunJun / Kangwon National University
### contact : richy1004@kangwon.ac.kr  

---------------------------------------------------------------------------------------------------------  
## Using files and directories :  
### /root/templates - HTML directory  
 main_page.html : Main page of PubMed search system  
 parsing_management.html : page of Parsing Management  
 search_papers.html : PubMed Paper Search page  
 paper_details.html : Detailed information of each paper.  
 search_history.html : History of searched papers.  

### /root
.gitignore : not uploading Big files(XML, XML.GZ, JSON..)  
README : Readme file  
app_V2.py : FLASK  
down_updatefiles_V3 : Download FTP, Checksum Hash  
make_test_file.py : make example file for checksum Hash  
parse_sql_unzip_V3.py : Unzip XML.gz files, Parsing XML by Json to SQL  

## not using files and directories :
### /root/saveresult - temporal dierctory of Parsing results. Currently replaced with SQL(MariaDB)  
### /root
ftp_download_log.txt  
main.py  
parsing_errors_log  
parsing_status.html  
