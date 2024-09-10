from flask import Flask, render_template, request, redirect, url_for, session
#session : 서로 다른 세션을 유지하며 정보를 주고 받는 역할
import pymysql

app = Flask(__name__)

# MySQL 데이터베이스 연결 설정
def get_db_connection():
    return pymysql.connect(
        host='localhost',  # MySQL 호스트
        user='root',       # MySQL 사용자
        password='1q2w3e',  # MySQL 비밀번호
        db='bulletin_board',  # 사용할 데이터베이스 이름
        port=3306,         # 포트는 기본값 3306
        charset='utf8',
        cursorclass=pymysql.cursors.DictCursor
    )

# 메인 페이지: 게시글 목록
@app.route('/')     #라우팅 경로 설정 메인 경로
def home():    #index 함수
    conn = get_db_connection()      #데이터베이스 연결
    cursor = conn.cursor()          #커서객체를 생성 = SQL 명령어 실행하고 결과 가져옴
    cursor.execute('SELECT * FROM posts')   #커서 객체를 사용해서 posts테이블의 모든 정보를 가져온다.
    posts = cursor.fetchall()   #실행된 sql 쿼리의 결과행을 리스트로 반환
    conn.close()    #데이터베이스 연결 종료
    return render_template('home.html', posts=posts) #posts 변수에 sql 쿼리 결과인 게시글 목록을 전달한다.

if __name__ == '__main__':
    app.run(debug=True)
