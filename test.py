from flask import Flask, render_template    #render_template 렌더링을 위한 함수 

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('test.html')    #templates 폴더에 있는 test.html 파일을 렌더링하여 반환 

if __name__ == '__main__':
    app.run()