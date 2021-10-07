import time
from flask import Flask, send_file, Response


app = Flask(__name__)


@app.route("/")
def main():
    return send_file("download.html")


def _generate(interval):
    for row in range(10):
        time.sleep(interval)
        yield ';'.join([str(row + i) for i in range(10)]) + '\n'


@app.route('/large.csv')
def stream_large_csv():
    time.sleep(5)
    return Response(_generate(1), mimetype='text/csv')


@app.route('/small.csv')
def stream_small_csv():
    return Response(_generate(0.1), mimetype='text/csv')
