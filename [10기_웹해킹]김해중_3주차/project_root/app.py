from flask import Flask, render_template, request, redirect, url_for
import pymysql

# flask : 플래스크를 사용하기 위한 클래스
# request : HTTP 요청 데이터를 다루기 위한 객체
# redirect : 클라이언트를 다른 URL로 리디렉션 할때 사용하는 함수
# url_for : 플래스크 내에서 url을 생성하는데 사용
# render_template : HTML 템플릿 파일을 렌더링하여 사용자에게 보낼때 사용
# pymysql : mysql에 연결하고 sql쿼리를 실행하기 위한 모듈
# cursors : pymysql 모듈 내의 서브 모듈 쿼리 실행 후 결과를 처리

app = Flask(__name__)

# MySQL 데이터베이스 연결 설정
def get_db_connection():
    return pymysql.connect(
        host='localhost',  # MySQL 호스트
        user='root',       # MySQL 사용자
        password='1q2w3e',  # MySQL 비밀번호
        db='bulletin_board',  # 사용할 데이터베이스 이름
        port=3306,         # 포트는 기본값 3306
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

# 메인 페이지: 게시글 목록
@app.route('/')     #라우팅 경로 설정
def index():    #index 함수
    conn = get_db_connection()      #데이터베이스 연결
    cursor = conn.cursor()          #커서객체를 생성 = SQL 명령어 실행하고 결과 가져옴
    cursor.execute('SELECT * FROM posts')   #커서 객체를 사용해서 posts테이블의 모든 정보를 가져온다.
    posts = cursor.fetchall()   #실행된 sql 쿼리의 결과행을 리스트로 반환
    conn.close()    #데이터베이스 연결 종료
    return render_template('index.html', posts=posts) #posts 변수에 sql 쿼리 결과인 게시글 목록을 전달한다.

# 게시글 작성 페이지
@app.route('/add', methods=('GET', 'POST'))
def add():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO posts (title, content) VALUES (%s, %s)', (title, content))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add.html')

# 게시글 수정 페이지
@app.route('/edit/<int:id>', methods=('GET', 'POST'))
def edit(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM posts WHERE id = %s', (id,))
    post = cursor.fetchone()

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        cursor.execute('UPDATE posts SET title = %s, content = %s WHERE id = %s', (title, content, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    conn.close()
    return render_template('edit.html', post=post)

# 게시글 삭제 기능
@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM posts WHERE id = %s', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# 게시글 검색 기능
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts WHERE title LIKE %s OR content LIKE %s", ('%' + query + '%', '%' + query + '%'))
    posts = cursor.fetchall()
    conn.close()
    return render_template('index.html', posts=posts)

if __name__ == '__main__':
    app.run(debug=True)
