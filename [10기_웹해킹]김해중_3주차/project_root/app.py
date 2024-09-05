from flask import Flask, render_template, request, redirect, url_for
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
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

# 메인 페이지: 게시글 목록
@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM posts')
    posts = cursor.fetchall()
    conn.close()
    return render_template('index.html', posts=posts)

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
