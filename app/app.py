import gradio as gr
import librosa
import matplotlib.pyplot as plt
import plotly.express as px
from radar_chart import radar_factory

from keras.models import load_model
import os
import numpy as np



model = load_model(os.path.join("lstm_all_four_complex.h5"))


def convert_class_to_emotion(pred):
        label_conversion = {0: 'neutral',
                            1: 'calm',
                            2: 'happy',
                            3: 'sad',
                            4: 'angry',
                            5: 'fearful',
                            6: 'disgust',
                            7: 'surprised'}

        return label_conversion[int(pred)]


def make_predictions(file, micro=None):
        if file is not None and micro is None:
            input_audio = file
        elif file is None and micro is not None:
            input_audio = micro
        else:
            print("THERE IS A PROBLEM")
            input_audio = file

        data, sampling_rate = librosa.load(input_audio)
        print(data)
        print(f"THE SAMPLING RATE IS {sampling_rate}")
        mfccs = np.mean(librosa.feature.mfcc(y=data, sr=sampling_rate, n_mfcc=40).T, axis=0)
        x = np.expand_dims(mfccs, axis=1)
        x = np.expand_dims(x, axis=0)
        predictions = np.argmax(model.predict(x), axis=1)

        N = 8
        theta = radar_factory(N, frame='polygon')
        spoke_labels = np.array(['neutral',
                            'calm',
                            'happy',
                            'sad',
                            'angry',
                            'fearful',
                            'disgust',
                            'surprised'])
        fig_radar, axs = plt.subplots(figsize=(8, 8), nrows=1, ncols=1,
                            subplot_kw=dict(projection='radar'))
        vec = model.predict(x)[0]
        axs.plot(theta, vec, color="b")
        axs.fill(theta, vec, alpha=0.3)

        axs.set_varlabels(spoke_labels)

        fig = plt.figure()
        plt.plot(data, alpha=0.8)
        plt.xlabel("temps")
        plt.ylabel("amplitude")


        return convert_class_to_emotion(predictions), fig, fig_radar # 



iface = gr.Interface(
    fn=make_predictions,
    title="Identify emotion of a chunk of audio speech", 
    inputs=[gr.Audio(source="upload", type="filepath", label="File"),
        gr.Audio(source="microphone", type="filepath", streaming=False, label="Microphone")] 
    ,
    examples=[[os.path.join("examples", filename)] for filename in os.listdir("examples")],
    outputs=[gr.Textbox(label="Text output"), gr.Plot(), gr.Plot()]
    )
iface.launch(debug=True)