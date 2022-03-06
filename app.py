from flask import Flask, render_template, request, Response, flash, send_file
from werkzeug.utils import secure_filename
from openCv import VideoCamera
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'omen'
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
auth = False


def generate(video):
    try:
        while True:
            frame = video.get_frame()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    except Exception as e:
        print(f'[generate ERROR]: {e}')


@app.route('/', methods=['GET'])
def index():
    try:
        file_name = [f for f in os.listdir(
            'static/uploads/') if os.path.isfile(os.path.join('static/uploads/', f))]
        for i in file_name:
            os.remove('static/uploads/' + i)
        with open('output.csv', 'w') as f:
            pass
    except:
        pass
    return render_template('index.html')


@app.route('/csv', methods=['GET', 'POST'])
def csv():
    table = pd.read_csv('output.csv', encoding='unicode_escape')
    return render_template('count.html', data=table.to_html())


@app.route('/', methods=['POST'])
def upload_video():
    video = request.files['video']
    video.save(os.path.join(
        app.config['UPLOAD_FOLDER'], secure_filename(video.filename)))

    file_name = [f for f in os.listdir(
        'static/uploads/') if os.path.isfile(os.path.join('static/uploads/', f))]
    return render_template('upload.html', file_name=file_name[0])


@app.route('/download')
def download():
    global auth
    if auth == True:
        auth = False
        return send_file('output.csv', as_attachment=True)
    else:
        flash('First detect the vehicle')
        return render_template('error.html')


@app.route('/cv', methods=['GET'])
def cv():
    global auth
    auth = True
    try:
        return Response(generate(VideoCamera()),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        auth = False
        if str(e) == 'list index out of range':
            flash(f'Please upload a video file')
        else:
            flash(f'[ERROR]: {e}')
        return render_template('error.html')


if __name__ == '__main__':
    app.run(debug=True)
