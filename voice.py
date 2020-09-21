import random
import speech_recognition as sr 
import pandas as pd
import os.path
import os
import pygame
from gtts import gTTS 
from inputimeout import inputimeout, TimeoutOccurred
from PyDictionary import PyDictionary as pyd
import numpy as np

sample_rate = 48000
chunk_size = 2048


pygame.init()
pygame.mixer.init()

r = sr.Recognizer() 
fname = "Meanings.xlsx"
sound_folder = "sounds/"
if	os.path.exists(fname):
	df = pd.read_excel(fname, index_col=0)
else:
	df = pd.DataFrame(columns=["Word", "Meaning", "Marked"])

df = df.drop_duplicates(subset='Word', keep='last')
df = df.reset_index(drop=True)
df.to_excel(fname)
words = df.shape[0]
remove_prev = input("Delete previous session yes or no, default no\n")
if remove_prev == 'yes':
	for index in range(0, df.shape[0]):
		df.iloc[index,2]='NO'
else:
	words = 0
	for index in range(0, df.shape[0]):
		if df.iloc[index,2] == 'NO':
			words = words + 1
			
remove_incorrect = input("Remove the incorrect words using dictionary yes or no, default no \n")
if remove_incorrect == "yes":
	for index in range(0, df.shape[0]):
		if pyd().meaning(df.iloc[index, 0]) == None:
			if input("remove word %s?\n" %  df.iloc[index, 0]) == 'y':
				if df.iloc[index,2] == 'NO':
					words = words - 1
				df = df.drop(index)
				df.to_excel(fname)

df.to_excel(fname)
input_timeout = input("input timeout yes or no, default no\n")
def inp(text, default, timeout=3):
	try:
		if input_timeout == 'yes':
			ans = inputimeout(prompt=text, timeout=timeout)
		else:
			ans = input(text)
		return ans
	except TimeoutOccurred:
		return default
		
voice_rec = False
def listen(text, default='', timeout=3):
	if not voice_rec:
		return inp(text, default, timeout)
	else:
		with sr.Microphone(sample_rate = sample_rate, chunk_size = chunk_size) as source: 
			r.adjust_for_ambient_noise(source) 
			try: 
				audio = r.listen(source) 
				text = r.recognize_google(audio)
				return text
			except Exception:
				return inp(text, default, timeout)

text_to_speech_on = input("Text to speech on or off, default on\n")
if text_to_speech_on != "off":
	text_to_speech = input("Text to speech fast or slow, default fast\n")
def say(text):
	if text_to_speech_on != "off":
		while pygame.mixer.music.get_busy() and text_to_speech == 'slow':
			pass
		if not os.path.exists(sound_folder+text+".mp3"):
			v =gTTS(text=text,lang="en") 
			v.save(sound_folder+text+".mp3")
		pygame.mixer.music.load(sound_folder+text+".mp3")
		pygame.mixer.music.play()	
	
while True:
	say("test or new entry")
	df.to_excel(fname)
	print("Words to ask = %d" % words)
	reply = listen("Test -> t or new entry -> n \n", 't')
	if reply == 'n':
		original_size = df.shape[0]
		word, meaning = input("Enter word meaning \n").split(",")
		print ("Meaning in the dictionary is:")
		print (pyd().meaning(word))
		df2 = pd.DataFrame([[word, meaning, "NO"]], columns=["Word","Meaning","Marked"])
		df = df.append(df2, ignore_index=True)
		df = df.drop_duplicates(subset='Word', keep='last')
		df = df.reset_index(drop=True)
		words = words + df.shape[0] - original_size
	else :
		if words == 0:
			print("No more words left")
			continue
		got_word=False
		while not got_word:
			index = np.random.choice(a=df.index.values)
			if df.iloc[index, 2] == 'NO':
				break
		say("word is : %s\n"% df.iloc[index, 0])
		meaning = listen("Enter the meaning for the word: %s\n"% df.iloc[index, 0], '', 5)
		if inp("Should I give the answer? \n", 'y') == 'y':
			say("Correct meaning is %s \n" % df.iloc[index, 1])
			print ("Correct meaning is %s"% df.iloc[index, 1])
			print (pyd().meaning(df.iloc[index, 0]))
			if inp("should I wait? \n",'') == 'y':
				garb = input('waiting...\n')
			say("Should I repeat this word?\n")
			if inp("Should I repeat this word yes or no, default no \n",'') != 'yes':
				words = words - 1
				df.iloc[index, 2] = 'YES'
			 
		else:
			words = words - 1
			say("Good, moving on")
			print ("Good, moving on")
			df.iloc[index, 2] = 'YES'
