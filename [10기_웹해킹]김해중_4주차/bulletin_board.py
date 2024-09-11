from flask import Flask, render_template, request, redirect, url_for, session ,flash
#session : 서로 다른 세션을 유지하며 정보를 주고 받는 역할
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql

app = Flask(__name__)
app.secret_key = 'user_secret_key'  # 세션에 사용할 비밀 키 설정 (보안을 위해 필요)

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
def home():    #home 함수
    conn = get_db_connection()      #데이터베이스 연결
    cursor = conn.cursor()          #커서객체를 생성 = SQL 명령어 실행하고 결과 가져옴
    cursor.execute('SELECT * FROM posts')   #커서 객체를 사용해서 posts테이블의 모든 정보를 가져온다.
    posts = cursor.fetchall()   #실행된 sql 쿼리의 결과행을 리스트로 반환
    conn.close()    #데이터베이스 연결 종료
    return render_template('home.html', posts=posts) #posts 변수에 sql 쿼리 결과인 게시글 목록을 전달한다.

# 회원가입 페이지 및 처리
@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']
        name = request.form['name']
        birthday = request.form['birthday']
        email = request.form['email']
        phone_num = request.form['phone_num']
        
        # 데이터베이스에 회원 정보 저장
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 같은 아이디가 존재하는지 확인
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            flash('이미 존재하는 아이디입니다.')
            return redirect(url_for('sign_up'))
        
        cursor.execute('INSERT INTO users (user_id, password, name, birthday, email, phone_num) VALUES (%s, %s, %s, %s, %s, %s)', 
                       (user_id, password, name, birthday, email, phone_num))
        conn.commit()
        conn.close()
        
        flash('회원가입이 완료되었습니다. 로그인 해주세요.')
        return redirect(url_for('login_page'))
    
    return render_template('sign_up.html')

#로그인 페이지
# 로그인 페이지
@app.route('/login_page', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']
        
        #데이터베이스에서 사용자 정보를 확인하기
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = %s AND password = %s', (user_id, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            # 로그인 성공 시 세션에 사용자 정보 저장
            session['logged_in'] = True
            session['user_id'] = user['user_id']
            session['name'] = user['name']
            session['birthday'] = user['birthday']
            session['email'] = user['email']
            session['phone_num'] = user['phone_num']
            return redirect(url_for('home'))
        else:
            #로그인 실패 시 처리
            flash('아이디 또는 비밀번호가 잘못되었습니다.')
            return redirect(url_for('login_page'))
    
    return render_template('login_page.html')

# 로그아웃 기능
@app.route('/logout')
def logout():
    session.clear()  # 세션 초기화
    return redirect(url_for('home'))

# 마이페이지
@app.route('/mypage')
def mypage():
    if not session.get('logged_in'):
        return redirect(url_for('login_page'))

    return render_template('mypage.html', user={
        'user_id': session['user_id'],
        'name': session['name'],
        'birthday': session['birthday'],
        'email' : session['email'],
        'phone_num' :session['phone_num']
    })

# 글쓰기 페이지
@app.route('/writing', methods=('GET', 'POST'))     # 경로 /add  GET과 POST 요청 모두 허용
def writing():
    if request.method == 'POST':    #클라이언트가 post 요청을 보냈는지 확인하는 조건문
        title = request.form['title']   #add.html에서 입력받은 내용(title)을 title로 지정한다.
        content = request.form['content']   #add.html에서 입력받은 내용(content)을 content에 저장한다.
        secret_check = request.form.get('secret_check') == 'on'
        secret_password = request.form['secret_password'] if secret_check else None
        user_id = session['user_id']  # 현재 로그인한 사용자의 ID

        # 비밀글 패스워드 해싱
        secret_password_hashed = generate_password_hash(secret_password) if secret_password else None

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO posts (title, content,secret_check,secret_password) VALUES (%s, %s, %s,%s)', (title, content,secret_check,secret_password))
        #연결 된 DB에 입력 받은 title과 content 부분을 삽입한다.
        conn.commit()   #DB를 저장한다.
        conn.close()
        return redirect(url_for('home'))   #글쓰기가 완료되면 다시 메인 화면으로 돌아간다.
    return render_template('writing.html')

# 게시글 조회
@app.route('/view/<int:id>', methods=('GET', 'POST'))
def view(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM posts WHERE id = %s', (id,))
    post = cursor.fetchone()
    conn.close()

    # 비밀글 확인 로직
    if post['is_secret']:
        if request.method == 'POST':
            entered_password = request.form['password']
            if check_password_hash(post['secret_password'], entered_password):
                return render_template('view_post.html', post=post)
            else:
                return render_template('enter_password.html', error="비밀번호가 틀렸습니다.")
        return render_template('enter_password.html', post=post)
    
    return render_template('view_post.html', post=post)


# 게시글 삭제 기능
@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM posts WHERE id = %s', (id,))
    #id를 확인하여서 DB에서 삭제
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

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
    return render_template('home.html', posts=posts)

if __name__ == '__main__':
    app.run(debug=True)
