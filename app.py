from flask import Flask, render_template, request, jsonify
from storage import setup_db
from recognise import listen_to_song, recognise_song, register_directory, register_song
import os 

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        pathfile = request.json.get('pathfile')  # Access JSON data
        if os.path.isdir(pathfile):
            register_directory(pathfile)
        else:
            register_song(pathfile)
        return jsonify({'message': 'Registration completed successfully.'})

from flask import jsonify

@app.route('/recognise', methods=['POST'])
def recognise():
    if request.method == 'POST':
        data = request.json  
        listen = data.get('listen')
        pathfile = data.get('pathfile')
        pathfile = os.path.join(r'C:\Users\User\abracadabra\music\snippet\noise', pathfile)
        print("Received pathfile:", pathfile)
        result = recognise_song(pathfile)
        
        # Assuming `recognise_song` returns a list of titles
        result_text = '\n'.join(result)  
        print(result_text)

        return result_text, 200  # Return plain text response



    
@app.route('/record', methods=['POST'])
def record():
    if request.method == 'POST':
        listen = request.json.get('listen')  # Access JSON data
        result = listen_to_song()
        print(result)
        return jsonify({'result': result})
    
@app.route('/initialise', methods=['POST'])
def initialise():
    if request.method == 'POST':
        setup_db()
        return jsonify({'message': 'Database initialised successfully.'})

if __name__ == '__main__':
    app.run(debug=True)
