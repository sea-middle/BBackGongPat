from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/',methods=['GET'])
def home():
    animal = request.args.get('animal')
    image_url = None

    if animal == 'dog':
        image_url = '/static/dog.jpg'
    elif animal == 'cat':
        image_url = 'https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2FMjAyMTAyMDJfMTEz%2FMDAxNjEyMjIyNzg3OTUz.QtApp2XIHlPApb7smrblXxrZhryinsHiD37zVivLuZ0g._w-Mj3SgiLhzQmzbJwyCKRBUufOwNp53FTMYAubCqekg.JPEG.kimr0319%2FIMG_4931.JPG&type=sc960_832'

    return render_template('dog_or_cat.html',animal=animal, image_url=image_url)

if __name__ == '__main__':
    app.run()