from flask import Flask, send_file

app = Flask(__name__)


@app.route("/")
def main():
    return send_file("cookies.html")
