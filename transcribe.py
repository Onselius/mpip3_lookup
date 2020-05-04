#! /bin/python3

import speech_recognition
import os
import pydub

sound = pydub.AudioSegment.from_mp3("20150421.mp3")
sound.export("output.wav", format="wav")

audio_file = "output.wav"

r = speech_recognition.Recognizer()
with speech_recognition.AudioFile(audio_file) as source:
    audio = r.record(source) 
    print("Transcription: " + r.recognize_google(audio))