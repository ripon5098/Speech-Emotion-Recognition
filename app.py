from flask import Flask, render_template, request, redirect, url_for
from flask_debugtoolbar import DebugToolbarExtension
from gradio_client import Client
import os

app = Flask(__name__)

# Initialize Debug Toolbar
toolbar = DebugToolbarExtension(app)

# Mapping of emotions to emoji symbols
emotion_to_emoji = {
    "neutral": "😐",
    "calm": "😌",
    "happy": "😄",
    "sad": "😢",
    "angry": "😠",
    "fearful": "😨",
    "disgust": "🤢",
    "surprised": "😲"
}


# @app.route('/', methods=['POST'])
# def upload_audio():
#     if 'audio' in request.files:
#         audio_file = request.files['audio']
#         # Process the audio file here
#         # You can save it, analyze it, or perform any other necessary operations.
#         return 'Audio file uploaded successfully.'
#     else:
#         return 'No audio file uploaded.'


@app.route('/', methods=['GET', 'POST'])
def index():
    emotion_label = ""
    emoji = ""
    if request.method == 'POST':
        # output = predict_emotions(request.files['audio'])
        # audio_file = request.files['audio']
        # Add this line for debugging
        print(predict_emotions(request.files['audio']))
        # output = predict_emotions(audio_file)
        input_audio = request.files['audio']
        result = predict_emotions(input_audio)
        print(result)
        # print(type(confidence_list))
        # if confidence_list:
        #     labels = [elem['label']
        #               for elem in confidence_list if elem['confidence'] >= 0.5]
        #     emotion_label = ", ".join(labels)
        if result and isinstance(result, tuple) and len(result) >= 2:
            # emotion_label = result[0]
            emotion_label, emoji = result[:2]
            print(emotion_label)
            print(type(emotion_label))
            if emotion_label:
                # Redirect to the 'result' page and pass the emotion_label as a query parameter
                return redirect(url_for('result', emotion_label=emotion_label))
        # return render_template('result.html', input_audio=input_audio, output=label_audio)
        return render_template('index.html', emotion_label=emotion_label, emoji=emoji)
    else:
        # , labels="No results")
        return render_template('index.html', emotion_label=emotion_label, emoji=emoji)
    # Example debugging statement
    # print("Debugging: Inside the index route")
    # Your view function logic here
    # return 'Hello, World!'


def predict_emotions(input_audio):
    # Print current working directory
    # print("Current Working Directory:", os.getcwd())
    # Get the current working directory
    current_dir = os.getcwd()
    # Get the filename from the input audio object
    filename = input_audio.filename

    # Create the absolute file path by joining the current directory and filename
    abs_file_path = os.path.join(current_dir, filename)

    # Check if the file exists
    if os.path.isfile(abs_file_path):
        print("File Path:", input_audio.filename)
        client = Client(
            "https://minhaj-ripon-speech-emotion-detector.hf.space/", api_name=None)
        result = client.predict(
            # str (filepath or URL to file) in 'File' Audio component
            # "https://github.com/gradio-app/gradio/raw/main/test/test_files/audio_sample.wav",
            # str (filepath or URL to file) in 'Microphone' Audio component
            # "https://github.com/gradio-app/gradio/raw/main/test/test_files/audio_sample.wav",
            # str(input_audio),
            # input_audio.filename
            abs_file_path,
            ""
            # "/predict"
        )

        print(result)
        # print(type(result))
        # Assuming 'result' contains the emotion label as a string
        emotion_label = result[0]

        # Get the corresponding emoji symbol
        # Use a question mark if the emotion is not recognized
        emoji = emotion_to_emoji.get(emotion_label, "❓")

        return emotion_label, emoji

        # return result
    else:
        print("Error: Audio file not found.")
        return None


def api_response():
    from flask import jsonify
    if request.method == 'POST':
        return jsonify(**request.json)


@app.route('/result')
def result():
    # Retrieve the emotion_label from the context or set a default value
    emotion_label = request.args.get('emotion_label', 'No emotion detected')
    emoji = emotion_to_emoji.get(emotion_label, "❓")
    return render_template('result.html', emotion_label=emotion_label, emoji=emoji)

    # if 'confidences' in result:
    #     confidence_list = result['confidences']
    #     # For debugging, you can remove this in production
    #     print(confidence_list)
    #     return confidence_list
    # else:
    #     # Handle the case when 'confidences' key is not found in the result
    #     # You can return an empty list or raise an exception as needed
    #     return []


@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.debug = True  # Enable debug mode
    app.run()
