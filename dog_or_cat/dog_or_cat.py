from flask import Flask, render_template, request
#request - 사용자가 보낸 요청을 처리

app = Flask(__name__)

@app.route('/',methods=['GET'])
def home():     #사용자가 / 경로에 접근 했을 때 실행 되는 함수
    animal = request.args.get('animal')
    #쿼리 파라미터로 전달 된 animal 값을 가져온다.
    image_url = None
    #url 변수 초기화
    if animal == 'dog':
        image_url = '/static/dog.jpg'
        #사용자가 dog를 선택할 경우 dog.jpg를 가져온다.
    elif animal == 'cat':
        image_url = 'https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2FMjAyMTAyMDJfMTEz%2FMDAxNjEyMjIyNzg3OTUz.QtApp2XIHlPApb7smrblXxrZhryinsHiD37zVivLuZ0g._w-Mj3SgiLhzQmzbJwyCKRBUufOwNp53FTMYAubCqekg.JPEG.kimr0319%2FIMG_4931.JPG&type=sc960_832'
        #외부의 링크를 통해 고양이 사진을 가져온다.
    return render_template('dog_or_cat.html',animal=animal, image_url=image_url)

if __name__ == '__main__':
    app.run()