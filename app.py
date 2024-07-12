from flask import Flask, render_template, request, jsonify
import os
from storage import setup_db
from recognise import listen_to_song, recognise_song, register_directory, register_song
import pyodbc
app = Flask(__name__)

DIRECTORY = r'C:\Users\User\freezam\music\snippet\noise'
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
    print(pathfile)
    if not pathfile:
        return jsonify({'error': 'Pathfile is required.'}), 400

    try:
        pathfile = os.path.join(DIRECTORY, pathfile)
        result = recognise_song(pathfile)
        print(result)
        
        # Convert pyodbc.Row to a list or dictionary
        if isinstance(result, pyodbc.Row):
            result = [item for item in result]

        # Ensure result is in the expected format
        if isinstance(result, (list, tuple)) and all(isinstance(item, str) for item in result):
            return jsonify({'results': result}), 200
        elif isinstance(result, str):
            return jsonify({'results': [result]}), 200
        else:
            return jsonify({'error': 'Unexpected result type from recognise_song.'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500






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
