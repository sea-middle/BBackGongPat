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

# 회원가입 함수
def sign_up(user_database):
    username = input("Enter your username: ")
    if username in user_database:
        print("Username already exists. Please choose a different username.")
        return
    
    password = input("Enter your password: ")
    
    # 사용자의 정보(이름과 비밀번호)를 딕셔너리에 저장하고 파일에 기록
    user_database[username] = password
    save_user_database(user_database)
    print("Sign-up successful!")

# 로그인 함수
def log_in(user_database):
    global current_user  # 전역 변수 사용
    username = input("Enter your username: ")
    if username not in user_database:
        print("Username does not exist. Please sign up first.")
        return False
    
    password = input("Enter your password: ")
    
    # 비밀번호 확인
    if user_database[username] == password:
        current_user = username  # 현재 로그인한 사용자를 저장
        print(f"Login successful! Welcome, {username}")
        return True
    else:
        print("Incorrect password. Please try again.")
        return False

# 회원 탈퇴 함수
def delete_account(user_database):
    global current_user  # 전역 변수 사용
    
    if current_user is None:
        print("You need to log in first.")
        return
    
    confirmation = input(f"Are you sure you want to delete the account '{current_user}'? (yes/no): ")
    
    if confirmation.lower() == 'yes':
        del user_database[current_user]
        save_user_database(user_database)
        print(f"Account '{current_user}' deleted successfully.")
        current_user = None  # 로그아웃 처리
    else:
        print("Account deletion canceled.")

# 로그아웃 함수 (로그아웃 시 계정 삭제)
def log_out(user_database):
    global current_user  # 전역 변수 사용
    
    if current_user is None:
        print("You are not logged in.")
        return
    
    # 로그아웃 시 계정 삭제
    del user_database[current_user]
    save_user_database(user_database)
    print(f"User '{current_user}' has been logged out and account has been deleted.")
    current_user = None  # 로그아웃 처리

# 메뉴 실행
def main():
    user_database = load_user_database()  # 프로그램 시작 시 사용자 정보 로드
    
    while True:
        print("\n1. Sign up")
        print("\n2. Log in")
        print("\n3. Delete Account")
        print("\n4. Log out and delete account")
        print("\n5. Exit")
        choice = input("Choose an option: ")
        
        if choice == "1":
            sign_up(user_database)
        elif choice == "2":
            log_in(user_database)
        elif choice == "3":
            delete_account(user_database)
        elif choice == "4":
            log_out(user_database)
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please choose again.")

if __name__ == "__main__":
    main()