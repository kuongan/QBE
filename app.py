from flask import Flask, render_template, request, jsonify
import os
from storage import setup_db
from recognise import listen_to_song, recognise_song, register_directory, register_song

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    if not request.json:
        return jsonify({'error': 'No JSON data provided.'}), 400

    pathfile = request.json.get('pathfile', None)
    if not pathfile:
        return jsonify({'error': 'Pathfile is required.'}), 400

    if os.path.isdir(pathfile):
        register_directory(pathfile)
    else:
        register_song(pathfile)
    return jsonify({'message': 'Registration completed successfully.'})

@app.route('/recognise', methods=['POST'])
def recognise():
    if not request.json:
        return jsonify({'error': 'No JSON data provided.'}), 400

    pathfile = request.json.get('pathfile', None)
    if not pathfile:
        return jsonify({'error': 'Pathfile is required.'}), 400

    pathfile = os.path.join(r'.\music\snippet\noise', pathfile)
    result = recognise_song(pathfile)
    return jsonify({'results': result})

@app.route('/record', methods=['POST'])
def record():
    result = listen_to_song()
    return jsonify({'result': result})

@app.route('/initialise', methods=['POST'])
def initialise():
    setup_db()
    return jsonify({'message': 'Database initialised successfully.'})

if __name__ == '__main__':
    app.run(debug=True)
