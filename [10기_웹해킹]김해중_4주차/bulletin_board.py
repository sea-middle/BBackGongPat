from flask import Flask, render_template, request, redirect, url_for, session ,flash, send_from_directory
#session : 서로 다른 세션을 유지하며 정보를 주고 받는 역할
import pymysql

import os 
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'user_secret_key'  # 세션에 사용할 비밀 키 설정 (보안을 위해 필요)

# 업로드 경로와 허용되는 파일 확장자 설정
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'docx', 'xlsx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    # 확장자를 제한하지 않으려면 아래 코드의 주석을 해제하거나, 원하는 확장자 리스트를 유지하세요.
    # return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['jpg', 'jpeg', 'png', 'gif', 'pdf']
    return True  # 모든 확장자 허용


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
    cursor.execute('SELECT id,title, created_at,user_id FROM posts')   #커서 객체를 사용해서 posts테이블의 모든 정보를 가져온다.
    posts = cursor.fetchall()   #실행된 sql 쿼리의 결과행을 리스트로 반환
    conn.close()    #데이터베이스 연결 종료
    return render_template('home.html', posts=posts) #posts 변수에 sql 쿼리 결과인 게시글 목록을 전달한다.

# 회원가입 페이지 및 처리
# 파일 업로드 경로 설정
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']
        name = request.form['name']
        birthday = request.form['birthday']
        email = request.form['email']
        phone_num = request.form['phone_num']

        # 파일 업로드 처리
        if 'profile_pic' not in request.files:
            flash('파일이 업로드되지 않았습니다.')
            return redirect(request.url)

        file = request.files['profile_pic']

        if file.filename == '':
            flash('선택된 파일이 없습니다.')
            return redirect(request.url)

        # 파일이 선택되었고 허용된 확장자라면
        if file:
            filename = secure_filename(file.filename)

            # 저장할 경로가 없으면 디렉터리 생성
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])

            # 파일 저장
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # 데이터베이스에 회원 정보 저장
        conn = get_db_connection()
        cursor = conn.cursor()

        # 아이디 중복 확인
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('이미 존재하는 아이디입니다.')
            return redirect(url_for('sign_up'))

        cursor.execute('INSERT INTO users (user_id, password, name, birthday, email, phone_num, profile_pic) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                       (user_id, password, name, birthday, email, phone_num, filename))
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
        #데이터베이스에 저장돼 있는 users테이블에서 user_id,password를 가져오고 각각의 user_id,password와 비교한다.
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

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 사용자 정보를 가져올 때 프로필 사진 정보도 포함
    cursor.execute('SELECT user_id, name, birthday, email, phone_num, profile_pic FROM users WHERE user_id = %s', (session['user_id'],))
    user = cursor.fetchone()
    conn.close()

    return render_template('mypage.html', user=user)


# 프로필 수정 처리를 위한 라우팅
@app.route('/update_profile', methods=['POST'])
def update_profile():
    if not session.get('logged_in'):
        return redirect(url_for('login_page'))

    # 폼에서 전송된 데이터 가져오기
    user_id = session['user_id']
    name = request.form['name']
    birthday = request.form['birthday']
    email = request.form['email']
    phone_num = request.form['phone_num']

    # 데이터베이스 업데이트
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET name = %s, birthday = %s, email = %s, phone_num = %s WHERE user_id = %s',
                   (name, birthday, email, phone_num, user_id))
    conn.commit()
    conn.close()

    # 세션 업데이트
    session['name'] = name
    session['birthday'] = birthday
    session['email'] = email
    session['phone_num'] = phone_num

    flash('프로필이 성공적으로 업데이트되었습니다.')
    return redirect(url_for('mypage'))


# 글쓰기 페이지
@app.route('/writing', methods=('GET', 'POST'))     # 경로 /add  GET과 POST 요청 모두 허용
def writing():
    if request.method == 'POST':    #클라이언트가 post 요청을 보냈는지 확인하는 조건문
        title = request.form['title']   #add.html에서 입력받은 내용(title)을 title로 지정한다.
        content = request.form['content']   #add.html에서 입력받은 내용(content)을 content에 저장한다.
        secret_check = request.form.get('secret_check') == 'on'
        secret_password = request.form['secret_password'] if secret_check else None
        user_id = session['user_id']  # 현재 로그인한 사용자의 ID

        # 파일 업로드 처리
        file = request.files['file'] if 'file' in request.files else None
        filename = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO posts (title, content, secret_check, secret_password, user_id, file) VALUES (%s, %s, %s, %s, %s,%s)', 
                   (title, content, bool(secret_check), secret_password, session['user_id'], filename))
        #연결 된 DB에 입력 받은 title과 content 부분을 삽입한다.
        conn.commit()   #DB를 저장한다.
        conn.close()
        return redirect(url_for('home'))   #글쓰기가 완료되면 다시 메인 화면으로 돌아간다.
    return render_template('writing.html')

@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# 게시글 조회
@app.route('/post_view/<int:id>', methods=['GET', 'POST'])
def post_view(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # 게시글 정보 가져오기
    cursor.execute('SELECT * FROM posts WHERE id = %s', (id,))
    post = cursor.fetchone()

    # 비밀글인 경우 처리
    if post['secret_check']:
        if request.method == 'POST':  # POST 요청으로 패스워드를 입력했을 경우
            input_password = request.form['secret_password']
            if input_password == post['secret_password']:  # 패스워드가 맞으면 내용을 보여줌
                conn.close()
                return render_template('post_view.html', post=post)
            else:
                conn.close()
                return "<p>비밀번호가 틀렸습니다. 다시 시도하세요.</p>"
        else:
            conn.close()
            # 비밀글이라면 패스워드를 입력받는 폼을 보여줌
            return '''
            <form method="POST">
                <label for="secret_password">비밀글 패스워드 입력:</label>
                <input type="password" id="secret_password" name="secret_password" required>
                <button type="submit">확인</button>
            </form>
            '''
    else:
        conn.close()
        return render_template('post_view.html', post=post)  # 비밀글이 아니면 바로 게시글을 보여줌


# 파일 다운로드 라우트
#@app.route('/uploads/<filename>')
#def download_file(filename):
#    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

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

# 아이디 찾기 페이지
@app.route('/find_id', methods=['GET', 'POST'])
def find_id():
    if request.method == 'POST':
        name = request.form['name']
        birthday = request.form['birthday']

        # 데이터베이스에서 이름과 생년월일이 일치하는 사용자 아이디 조회
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM users WHERE name = %s AND birthday = %s', (name, birthday))
        user = cursor.fetchone()
        conn.close()

        if user:
            return f"당신의 아이디는 {user['user_id']} 입니다."
        else:
            return redirect(url_for('find_id'))

    return render_template('find_id.html')  

# 패스워드 찾기 페이지
@app.route('/find_password', methods=['GET', 'POST'])
def find_password():
    if request.method == 'POST':
        name = request.form['name']
        birthday = request.form['birthday']
        user_id = request.form['user_id']

        # 데이터베이스에서 이름과 생년월일,ID가 일치하는 사용자 패스워드 조회
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT password FROM users WHERE name = %s AND birthday = %s AND user_id = %s', (name, birthday, user_id))
        user = cursor.fetchone()
        conn.close()

        if user:
            return f"당신의 패스워드는 {user['password']} 입니다."
        else:
            return redirect(url_for('find_password'))

    return render_template('find_password.html')

if __name__ == '__main__':
    app.run(debug=True)
