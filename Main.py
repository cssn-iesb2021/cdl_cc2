#!/usr/bin/env python
# coding: utf-8

# In[1]:


from ibm_watson import TextToSpeechV1
from ibm_watson.websocket import SynthesizeCallback

from ibm_watson import SpeechToTextV1
from ibm_watson.websocket import RecognizeCallback, AudioSource

from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

from threading import Thread
from queue import Queue, Full
from tkinter import *

import pyaudio
import wave
import base64
import time
import logging


# In[2]:


authenticator = IAMAuthenticator('ps0DnETIH6TeKm_vaoGxV32XXI-dqCEfHYDEkVx4dwK0')
authenticator2 = IAMAuthenticator('RrfBo9s51kwg4K-sLrfrrb_OwHcQ7B-qhrXJN3FApVzU')    
service = TextToSpeechV1(authenticator=authenticator)
speech_to_text = SpeechToTextV1(authenticator=authenticator2)


# In[3]:


class App:
    def __init__(self, master=None):
        self.master = master
        self.fontePadrao = ("Calibri", "10") 

        self.label1 = Frame(master)
        self.label1["pady"] = 10
        self.label1.pack()
        
        self.label2 = Frame(master)
        self.label2["pady"] = 1
        self.label2.pack()

        self.entry = Frame(master)
        self.entry["padx"] = 10
        self.entry.pack()

        self.button1 = Frame(master)
        self.button1["pady"] = 1
        self.button1.pack()

        self.label3 = Frame(master)
        self.label3["pady"] = 10
        self.label3.pack()

        self.button2 = Frame(master)
        self.button2["pady"] = 1
        self.button2.pack()        
 
        self.label4 = Frame(master)
        self.label4["padx"] = 20
        self.label4.pack()

        self.button3 = Frame(master)
        self.button3["pady"] = 1
        self.button3.pack()
        
        self.titulo = Label(self.label1, text="TRANSFORME O SEU TEXTO EM ÁUDIO OU SEU ÁUDIO EM TEXTO")
        self.titulo["font"] = ("Calibri", "11", "bold")
        self.titulo.pack()
        
        self.nomeLabel = Label(self.label2, text="Insira aqui o seu texto e clique em 'OUVIR O TEXTO':", font=self.fontePadrao)
        self.nomeLabel.pack(side=LEFT)

        self.entradatts = Entry(self.entry)
        self.entradatts["width"] = 70
        self.entradatts["font"] = self.fontePadrao
        self.entradatts.focus()
        self.entradatts.pack(side=LEFT)

        self.processtts = Button(self.button1)
        self.processtts["text"] = "OUVIR O TEXTO"
        self.processtts["font"] = ("Calibri","10","bold")
        self.processtts["width"] = 20
        self.processtts["command"] = self.processtos
        self.processtts.pack()
     
        self.vozLabel1 = Label(self.label3, text="Pressione 'GRAVAR' para a capturar seu áudio.\nSerão gravados 10 segundos de voz para transcrição.", font=self.fontePadrao)
        self.vozLabel1.pack(side=LEFT)      
        
        self.record = Button(self.button2)
        self.record["text"] = "GRAVAR"
        self.record["font"] = ("Calibri","10","bold")
        self.record["width"] = 20
        self.record["command"] = self.recordv
        self.record.pack()        
 
        self.record = Button(self.button2)
        self.record["text"] = "CONVERTER PARA TEXTO"
        self.record["font"] = ("Calibri","10","bold")
        self.record["width"] = 20
        self.record["command"] = self.processrecord
        self.record.pack()
        
        self.txtoutput = Label(self.label4,text='',bg ="white",width=70, height=2)
        self.txtoutput.pack(side=LEFT)
        
        self.label2 = Frame(master)
        self.label2["padx"] = 20
        self.label2.pack()
        
        self.quit = Button(self.button3)
        self.quit["text"] = "FECHAR"
        self.quit["font"] = ("Calibri","10","bold")
        self.quit["width"] = 10
        self.quit["fg"] = "red"
        self.quit["command"] =self.master.destroy
        self.quit.pack()
        
    def processtos(self):
        
        text = self.entradatts.get()
        test_callback = MySynthesizeCallback()
        
        service.synthesize_using_websocket(text,
                                           test_callback,
                                           accept='audio/wav',
                                           voice="pt-BR_IsabelaVoice"
                                           #voice="pt-BR_IsabelaV3Voice"
                                           )
    
    def recordv(self):

        CHUNK = 512
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        RECORD_SECONDS = 10
        
        WAVE_OUTPUT_FILENAME = "output.wav"

        p = pyaudio.PyAudio()

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        print("==> GRAVANDO")

        frames = []

        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        print("==> FIM DA GRAVAÇÃO")

        stream.stop_stream()
        stream.close()
        p.terminate()

        global wf
        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        

    def processrecord(self):        
        with open('output.wav','rb') as audio_file:
            speech_recognition_results = speech_to_text.recognize(
            audio=audio_file,
            model='pt-BR_BroadbandModel',
            content_type='audio/wav'       
            ).get_result()
        result = speech_recognition_results['results']
        result = result[0]
        result = result['alternatives']
        result = result[0]
        result = result['transcript']
        self.txtoutput.destroy()
        self.txtoutput = Label(self.label4, text=result, font=self.fontePadrao, bg ="white", width=70, height=2)
        self.txtoutput["font"] = ("Calibri", "10", "bold")
        self.txtoutput.pack(side=LEFT)


# In[4]:


class Play(object):

    def __init__(self):
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 22050
        self.chunk = 512
        self.pyaudio = None
        self.stream = None

    def start_streaming(self):
        self.pyaudio = pyaudio.PyAudio()
        self.stream = self._open_stream()
        self._start_stream()

    def _open_stream(self):
        stream = self.pyaudio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            output=True,
            frames_per_buffer=self.chunk,
            start=False
        )
        return stream

    def _start_stream(self):
        self.stream.start_stream()

    def write_stream(self, audio_stream):
        self.stream.write(audio_stream)

    def complete_playing(self):
        self.stream.stop_stream()
        self.stream.close()
        self.pyaudio.terminate()

class MySynthesizeCallback(SynthesizeCallback):
    def __init__(self):
        SynthesizeCallback.__init__(self)
        self.play = Play()

    def on_connected(self):
        self.play.start_streaming()
         
    def on_audio_stream(self, audio_stream):
        self.play.write_stream(audio_stream)
        return audio_stream
    
    def on_data(self, data):
        return data

    def on_close(self):
        self.play.complete_playing()


# In[5]:


class MyRecognizeCallback(RecognizeCallback):
    def __init__(self):
        RecognizeCallback.__init__(self)


# In[6]:


root = Tk()
root.title("SÍNTESE DE VOZ COM IBM WATSON")
App(root)
mainloop()

