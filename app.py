from flask import Flask, render_template, request, jsonify
import search as s
from record import RecordQuery
import os
from downloader import download

app = Flask(__name__)
# Định nghĩa thư mục lưu trữ
UPLOAD_FOLDER = './music/snippet/'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# ENDPOINTS
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/addsong', methods=['POST'])
def addsong():
    data = request.json
    if 'youtubeUrl' in data: # type: ignore
        youtubeUrl = data['youtubeUrl'] # type: ignore
        pathfile = download(youtubeUrl)
        s.add_song(pathfile)
        return jsonify(success=True)
    else:
        return jsonify(success=False, message='Missing youtubeUrl field')

@app.route('/remove_song', methods=['POST'])
def remove_song():
    title = request.form['title']
    s.remove_song(title)
    return jsonify(success=True)

@app.route('/construct_database', methods=['GET'])
def construct_database():
    s.construct_database()
    return jsonify(success=True)

@app.route('/identify_snippet', methods=['POST'])
def identify_snippet():
    if 'file' in request.files:
        file = request.files['file']
        path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename) # type: ignore
        file.save(path)  # Lưu file tạm thời để xử lý
    else:
        path = request.form.get('filePath')
    
    title = s.identify_snippet(path, 3)

    # Trả về kết quả hoặc lỗi nếu cần
    return jsonify(result=title)

@app.route('/list_songs', methods=['GET'])
def list_songs():
    titles = s.list_songs()
    return jsonify(result=titles)

@app.route('/record', methods=['POST'])
def record():
    RecordQuery(20)
    return jsonify(success=True)

if __name__ == '__main__':
    app.run(debug=True)