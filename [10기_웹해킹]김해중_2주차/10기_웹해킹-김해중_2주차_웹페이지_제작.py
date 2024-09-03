from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# 사용자 정보를 저장할 파일 경로
file_path = "user_information.txt"
current_user = None  # 현재 로그인한 사용자를 저장할 변수

# 파일에서 사용자 정보를 로드하는 함수
def load_user_database():
    user_database = {}
    try:
        with open(file_path, "r") as file:
            for line in file:
                username, password = line.strip().split(',')
                user_database[username] = password
    except FileNotFoundError:
        pass  # 파일이 없으면 빈 딕셔너리를 반환
    return user_database

# 사용자 정보를 파일에 저장하는 함수
def save_user_database(user_database):
    with open(file_path, "w") as file:
        for username, password in user_database.items():
            file.write(f"{username},{password}\n")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    user_database = load_user_database()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # 스페이스바 포함 여부 검사
        if ' ' in username or ' ' in password:
            return render_template('signup.html', error="Username and password cannot contain spaces.")
        
        if username in user_database:
            return render_template('signup.html', error="Username already exists.")
        
        user_database[username] = password
        save_user_database(user_database)
        return render_template('success.html', message="Sign-up successful!")
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def log_in():
    global current_user
    user_database = load_user_database()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # 스페이스바 포함 여부 검사
        if ' ' in username or ' ' in password:
            return render_template('login.html', error="Username and password cannot contain spaces.")
        
        if username in user_database and user_database[username] == password:
            current_user = username
            return render_template('success.html', message=f"Login successful! Welcome, {username}")
        else:
            return render_template('login.html', error="Invalid username or password.")
    
    return render_template('login.html')

@app.route('/delete_account', methods=['GET', 'POST'])
def delete_account():
    global current_user
    user_database = load_user_database()
    if request.method == 'POST':
        if current_user and request.form['confirmation'].lower() == 'yes':
            del user_database[current_user]
            save_user_database(user_database)
            current_user = None
            return render_template('success.html', message="Account deleted successfully.")
    
    return render_template('delete_account.html', user=current_user)

@app.route('/logout', methods=['POST'])
def log_out():
    global current_user
    user_database = load_user_database()
    if current_user:
        del user_database[current_user]
        save_user_database(user_database)
        current_user = None
        return render_template('success.html', message="Logged out and account deleted.")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
