from django.shortcuts import render
import speech_recognition as sr
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from gtts import gTTS
from playsound import playsound
import geocoder
import json
import requests

google_maps_API_key = 'AIzaSyBvrcq4Uit7s1hGsGVL9wPZCuwpHHkkXMc'

#seta reconhecedor de voz
r = sr.Recognizer()
#define chatter bot
chatbot = ChatBot('Bino')
#define exemplo de conversa
conversa = ['olá', 'oi, como você está se sentindo?',
            'estou com dor de cabeça', 'em que região da cabeça dói?',
            'do lado direito', 'Você pode estar com enxaqueca. Que tal fazer uma pausa e procurar um lugar tranquilo? Prefere um posto ou um hotel?',
            'hotel', 'parece que você está procurando um hotel, aqui vão alguns',
            'do lado esquerdo', 'Você pode estar com enxaqueca. Que tal fazer uma pausa e procurar um lugar tranquilo? Prefere um posto ou um hotel?',
            'queria dormir', 'parece que você está procurando um hotel, aqui vão alguns',
            'nas laterais da cabeça', 'está pulsando? Se sim, diga: está pulsando, se não diga: não está pulsando',
            'está pulsando', 'pode ser por muita tensão, que tal dar uma pausa e relaxar?',
            'não está pulsando', 'mesmo assim é preocupante, que tal dar uma pausa e esperar passar?',
            'estou cansado', 'que tal fazer uma pausa? Aqui vão alguns lugares que podem lhe agradar',
            'estou com sono', 'que tal fazer uma pausa? Aqui vão alguns lugares que podem lhe agradar',
            'não posso parar', 'que tal comer um pouco então? Uma fruta ou um doce ajudam a nos manter acordados',
            'estou com dor nas costas', 'você está há muito tempo no volante? Se sim diga: estou há muito tempo no volante, se não, diga: não estou há muito tempo no volante',
            'estou há muito tempo no volante', 'que tal fazer uma pausa? Se parece uma boa idéia diga: parece uma boa idéia, se não, pense em quando pode parar e me chame para fazer alguns alongamentos com você, dizendo, vamos alongar!!',
            'parece uma boa idéia', 'Ok, quando parar, me chame dizendo, vamos alongar!',
            ]

#treina chatter com a conversa exemplo
#trainer = ListTrainer(chatbot)
#trainer.train(conversa)

def get_latlng():
    a = geocoder.ip('me')
    return a.latlng

def busca_proximidades(type_, keyword):
    latlng = get_latlng()
    link = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location='+str(latlng[0])+','+str(latlng[1])+'&radius=1500&type='+type_+'&keyword='+keyword+'&key='+google_maps_API_key
    print(link)
    lugares_json = requests.get(link)
    lugares = json.loads(lugares_json.text)
    lugares = lugares['results']
    lugares_string = ''
    lugares_html = []
    for i in lugares:
        lugares_html.append ([i['name'], i['rating'], i['vicinity']])
        lugares_string += i['name'] + ', '
    responde(lugares_string)
    return lugares_html
    #print(lugares)


def checa_palavra(frase):
    if('posto' in frase or 'abastecer' in frase):
        a = busca_proximidades('posto', 'gasolina')
        return True, a
    if('passar a noite' in frase or 'dormir' in frase or 'hotel' in frase):
        a = busca_proximidades('hotel', 'dormir')
        return True, a
    if('comer' in frase or 'fome' in frase or 'comida' in frase or 'restaurante' in frase in frase):
        a = busca_proximidades('restaurante', 'comida')
        return True, a
    if('fedor' in frase or 'banho' in frase or 'limp' in frase):
        a = busca_proximidades('hotel', 'banheiro')
        return True, a
    if('cansado' in frase or 'descansar' in frase):
        a = busca_proximidades('posto', 'descanso')
        return True, a
    if('banheiro' in frase or 'mijar' in frase):
        a = busca_proximidades('posto', 'banheiro')
        return True, a

#gera resposta audível e toca ela
def responde(resp):
    resp_falada = gTTS(text= resp, lang='pt')
    resp_falada.save('resposta.mp3')
    playsound('resposta.mp3')

# Create your views here.
def ouve(request):
    text = ''
    resp = ''


    try:
        ouviu = False
        reconheceu = False
        comando = False
        while (not ouviu or not reconheceu):
            with sr.Microphone() as source:
                try:
                    r.adjust_for_ambient_noise(source, duration=0.2)
                    print('Ouvindo...')
                    audio_data = r.listen(source, timeout=3)
                except:
                    continue
                else:
                    ouviu = True

                print('Reconhecendo...')
                try:
                    text = r.recognize_google(audio_data, language='pt-BR')
                    print(text)
                except:
                    continue
                else:
                    if (text == ''):
                        continue
                    reconheceu = True

            
            resp = chatbot.get_response(str(text))
            responde(str(resp))
            comando, lugares = checa_palavra(text)

            
    except sr.RequestError as e: 
        print("Could not request results; {0}".format(e)) 
          
    except Exception as e: 
        print("unknown error occured" + str(e))

    if comando:
        return render(request, 'index.html', {'fala': text, 'resposta': resp, 'lugares': lugares})
    else:
        return render(request, 'index.html', {'fala': text, 'resposta': resp})

def index(request):
    return render(request, 'index.html')