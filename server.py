import base64
import json
from flask import Flask, render_template, request
from flask_cors import CORS
import os
from worker import speech_to_text, text_to_speech, watsonx_process_message

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/speech-to-text', methods=['POST'])
def speech_to_text_route():
    print("Processing Speech-to-Text")
    audio_binary = request.data
    text = speech_to_text(audio_binary)

    response = app.respone_class(
        response=json.dumps({'text': text}),
        status=200,
        mimetype='application/json'
    )

    print(response)
    print(response.data)
    return response


@app.route('/process-message', methods=['POST'])
def process_message_route():
    user_message = request.json['userMessage']
    print('user_message: ', user_message)

    voice = request.json['voice']
    print('voice: ', voice)

    # Generate the response from Watson given the user's message
    watsonx_response_text = watsonx_process_message(user_message)
    # Clean up Watson's response cause he might fuck up
    watsonx_response_text = os.linesep.join([s for s in watsonx_response_text.splitlines() if s])
    # Get Watson's message in speech using the function you created in wokrer.py
    watsonx_response_speech = text_to_speech(watsonx_response_text, voice)
    # Conver Watson's speech into base64 string so it can be passed to the front end in JSON fromat
    watsonx_response_speech = base64.b64encode(watsonx_response_speech).decode('utf-8')

    # Create the JSON response that will be sent back to the front end
    response = app.response_class(
        response=json.dumps({"watsonxResponseText": watsonx_response_text, "watsonxResponseSpeech": watsonx_response_text}),
        status=200,
        mimetype='application/json'
    )

    print(response)
    return response



if __name__ == "__main__":
    app.run(port=8000, host='0.0.0.0')
