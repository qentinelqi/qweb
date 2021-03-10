import time

from flask import Flask, send_file

app = Flask(__name__)


@app.route("/")
def main():
    return send_file("xhr.html")


@app.route("/xhrapi")
def xhrapi():
    time.sleep(2)
    return "Text retrieved using xhr"
