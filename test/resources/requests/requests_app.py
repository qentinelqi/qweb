from flask import Flask, render_template, send_file, url_for

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def main():
    return render_template("items.html")


@app.route('/download')
def download():
    return send_file('dummy.pdf')
