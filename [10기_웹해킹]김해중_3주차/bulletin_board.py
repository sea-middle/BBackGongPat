from flask import Flask, request, redirect, url_for, render_template
import pymysql.cursors

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
    connection = pymysql.connect(
        host='localhost',   #DB 접속 주소 (docker를 이용해서 mysql을 실행해서 localhost 사용)
        user='root',    #user명
        password='1q2w3e',  #DB명
        port=3306,  #포트 명
        cursorclass=pymysql.cursors.DictCursor  #DB 쿼리 결과를 딕셔너리 형태로 반환
    )
    return connection

# 홈 페이지
@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')

    connection = get_db_connection()
    with connection.cursor() as cursor:
        sql = 'SELECT COUNT(*) AS total FROM posts WHERE title LIKE %s OR content LIKE %s'
        cursor.execute(sql, (f'%{search}%', f'%{search}%'))
        total_posts = cursor.fetchone()['total']

        posts_per_page = 5
        offset = (page - 1) * posts_per_page
        total_pages = (total_posts + posts_per_page - 1) // posts_per_page

        prev_page = page - 1 if page > 1 else None
        next_page = page + 1 if page < total_pages else None

        sql = '''
            SELECT * FROM posts 
            WHERE title LIKE %s OR content LIKE %s 
            ORDER BY created_at DESC 
            LIMIT %s OFFSET %s
        '''
        cursor.execute(sql, (f'%{search}%', f'%{search}%', posts_per_page, offset))
        posts = cursor.fetchall()

    connection.close()
    return render_template('index.html', posts=posts, prev_page=prev_page, next_page=next_page)


# 게시물 작성 페이지
@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute('INSERT INTO posts (title, content) VALUES (%s, %s)', (title, content))
        connection.commit()
        connection.close()
        return redirect(url_for('index'))
    return render_template('create.html')

# 게시물 수정 페이지
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    connection = get_db_connection()
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        with connection.cursor() as cursor:
            cursor.execute('UPDATE posts SET title=%s, content=%s WHERE id=%s', (title, content, id))
        connection.commit()
        connection.close()
        return redirect(url_for('index'))
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM posts WHERE id=%s', (id,))
        post = cursor.fetchone()
    connection.close()
    return render_template('edit.html', post=post)

# 게시물 삭제
@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute('DELETE FROM posts WHERE id=%s', (id,))
    connection.commit()
    connection.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
