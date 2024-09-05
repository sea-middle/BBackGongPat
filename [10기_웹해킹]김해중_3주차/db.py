import pymysql

#DB 연결하기
db = pymysql.connect(host="localhost",user="root",password="1q2w3e",charset="utf8")

cursor = db.cursor()

print(db)