from uuid import uuid4
from sklearn.feature_extraction.text import CountVectorizer
import speech_recognition as sr 
import moviepy.editor as mp
import numpy as np
import pandas as pd
import os

def convertText(videoFile) -> str:
  clip = mp.VideoFileClip(videoFile) 
  audio = "audio\\{}.wav".format("converted")
  clip.audio.write_audiofile(audio)
  r = sr.Recognizer()
  audio = sr.AudioFile(audio)
  with audio as source:
    audio_file = r.record(source)
  result = r.recognize_google(audio_file)
  return result

def cosine_similarity(vector1, vector2):
  vector1 = np.array(vector1)
  vector2 = np.array(vector2)
  return np.dot(vector1, vector2) / (np.sqrt(np.sum(vector1**2)) * np.sqrt(np.sum(vector2**2)))

def percentageCalc(text):
  corpus = pd.Series(text)
  vectorizer = CountVectorizer()
  bow_matrix = vectorizer.fit_transform(corpus)
  return cosine_similarity(bow_matrix.toarray()[0], bow_matrix.toarray()[1])

# text = (""" Trigonometry is a branch of mathematics that studies relationships between side lengths and angles of triangles The field emerged in the Hellenistic world during the 3rd century BC from applications""", 
#         """ Driven by the demands of navigation and the growing need for accurate maps of large geographic areas trigonometry grew into a major branch of mathematics Bartholomaeus Pitiscus was the first""")
# print(percentageCalc(text))