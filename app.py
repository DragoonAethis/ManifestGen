from flask import Flask, render_template

from generator import generate_text
#from mockgen import generate_text


app = Flask(__name__)


@app.route('/', endpoint="index")
def generate():
    return render_template('index.html', text=generate_text())


@app.route('/about', endpoint="about")
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run()
