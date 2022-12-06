from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify
from werkzeug.utils import secure_filename
import os
import cv2
import time
import requests

from datetime import timedelta

# set allowing file format
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'JPG', 'PNG', 'bmp'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


app = Flask(__name__)

@app.route('/hello', methods=['POST', 'GET'])  # add route
def hello():
    return "hello"


@app.route('/', methods=['POST', 'GET'])  # add route
def upload():
    if request.method == 'POST':
        f = request.files['file']

        if not (f and allowed_file(f.filename)):
            return jsonify({"error": 1001, "msg": "请检查上传的图片类型，仅限于png、PNG、jpg、JPG、bmp"})

        basepath = os.getcwd()  # current path of the file

        upload_path = os.path.join(basepath, 'static/images', secure_filename(f.filename))  # pleas mkdir the folder first
        f.save(upload_path)

        # use opencv to transform the img format
        img = cv2.imread(upload_path)
        cv2.imwrite(os.path.join(basepath, 'static/images', 'test.jpg'), img)
        type = requests.get('http://localhost:5000/client?fileAddress='+upload_path).text

        return render_template('upload_ok.html', type=type, val1=time.time())

    return render_template('upload.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8900)
