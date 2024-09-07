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
@app.route('/')     #라우팅 경로 설정 메인 경로
def index():    #index 함수
    conn = get_db_connection()      #데이터베이스 연결
    cursor = conn.cursor()          #커서객체를 생성 = SQL 명령어 실행하고 결과 가져옴
    cursor.execute('SELECT * FROM posts')   #커서 객체를 사용해서 posts테이블의 모든 정보를 가져온다.
    posts = cursor.fetchall()   #실행된 sql 쿼리의 결과행을 리스트로 반환
    conn.close()    #데이터베이스 연결 종료
    return render_template('index.html', posts=posts) #posts 변수에 sql 쿼리 결과인 게시글 목록을 전달한다.

# 게시글 작성 페이지
@app.route('/add', methods=('GET', 'POST'))     # 경로 /add  GET과 POST 요청 모두 허용
def add():
    if request.method == 'POST':    #클라이언트가 post 요청을 보냈는지 확인하는 조건문
        title = request.form['title']   #add.html에서 입력받은 내용(title)을 title로 지정한다.
        content = request.form['content']   #add.html에서 입력받은 내용(content)을 content에 저장한다.
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO posts (title, content) VALUES (%s, %s)', (title, content))
        #연결 된 DB에 입력 받은 title과 content 부분을 삽입한다.
        conn.commit()   #DB를 저장한다.
        conn.close()
        return redirect(url_for('index'))   #글쓰기가 완료되면 다시 메인 화면으로 돌아간다.
    return render_template('add.html')

# 게시글 수정 페이지
@app.route('/edit/<int:id>', methods=('GET', 'POST'))   #/edit/ 뒤에 숫자 id 값을 받아 해당 경로에서 get 및 post 요청을 처리
def edit(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM posts WHERE id = %s', (id,))      #해당 id 값을 게시글을 조회
    post = cursor.fetchone()    #조회한 게시글을 post에 저장

    if request.method == 'POST':    #클라이언트가 post 요청을 보냈는지 확인하는 조건문
        title = request.form['title']
        content = request.form['content']
        cursor.execute('UPDATE posts SET title = %s, content = %s WHERE id = %s', (title, content, id))
        #입력 받은 값으로 DB의 데이터를 수정 한다.
        conn.commit()
        conn.close()
        return redirect(url_for('index'))   #수정이 완료 되면 초기 화면으로 돌아간다.

    conn.close()
    return render_template('edit.html', post=post)
    #
    # GET : 해당 게시글 정보를 가져와 수정할 수 있는 폼을 표시
    # POST : 수정 된 게시글을 DB에 업데이트

# 게시글 삭제 기능
@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM posts WHERE id = %s', (id,))
    #id를 확인하여서 DB에서 삭제
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# 게시글 검색 기능
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')   #query는 사용자가 입력한 키워드
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts WHERE title LIKE %s OR content LIKE %s", ('%' + query + '%', '%' + query + '%'))
    #입력된 값이 posts 테이블의 title 컬럼 또는 content 컬럼에 있는지 확인 
    posts = cursor.fetchall()
    conn.close()
    return render_template('index.html', posts=posts)

if __name__ == '__main__':
    app.run(debug=True)
