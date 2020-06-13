from django.shortcuts import render
import speech_recognition as sr
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from gtts import gTTS
from playsound import playsound

#seta reconhecedor de voz
r = sr.Recognizer()
#define chatter bot
chatbot = ChatBot('Bino')
#define exemplo de conversa
conversa = ['oi', 'olá, eu sou Bino. tudo bem?', 'tudo e com você?', 'comigo também']

#treina chatter com a conversa exemplo
#trainer = ListTrainer(chatbot)
#trainer.train(conversa)


#gera resposta audível e toca ela
def responde(resp):
    resp_falada = gTTS(text= resp, lang='pt')
    resp_falada.save('resposta.mp3')
    playsound('resposta.mp3')

# Create your views here.
def ouve(request):
    print('aqui')
    text = ''
    resp = ''
    
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.2)
            print('Ouvindo...')
            audio_data = r.listen(source, timeout=3)
            print('Reconhecendo...')
            text = r.recognize_google(audio_data, language='pt-BR')
            print(text)
            resp = chatbot.get_response(str(text))
            print(resp)
            responde(str(resp))
    except sr.RequestError as e: 
        print("Could not request results; {0}".format(e)) 
          
    except Exception as e: 
        print("unknown error occured" + str(e))

    return render(request, 'index.html', {'fala': text, 'resposta': resp})

def index(request):
    return render(request, 'index.html')