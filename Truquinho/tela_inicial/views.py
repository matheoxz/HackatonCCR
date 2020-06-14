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
historico_fala = []
historico_resp = []
#seta reconhecedor de voz
r = sr.Recognizer()
#define chatter bot
chatbot = ChatBot('Bino')
#define exemplo de conversa

conversa = ['Bino', 'olá cowboy do asfalto, ce ta bem?',
            'tô e você?', 'te corujando aqui, precisa de alguma coisa?',
            'tô não', 'eita! precisa de alguma coisa?',
            'tô com dor de cabeça', 'em que parte da cabeça dói?',
            'do lado direito', 'Você pode estar com enxaqueca. Que tal fazer uma pausa e procurar um lugar tranquilo? Vou procurar um petroleiro que te acomode',
            'do lado esquerdo', 'Você pode estar com enxaqueca. Que tal fazer uma pausa e procurar um lugar tranquilo? Vou procurar um petroleiro que te acomode',
            'dois metros horizontais', 'parece que você está procurando um hotel, aqui vão alguns',
            'nas laterais da cabeça', 'está pulsando? Se sim, diga: está pulsando, se não diga: não está pulsando',
            'está pulsando', 'pode ser por muita tensão, que tal dar uma pausa e relaxar?',
            'não está pulsando', 'mesmo assim é preocupante, que tal dar uma pausa e esperar passar?',
            'estou cansado', 'que tal fazer uma pausa? Aqui vão alguns lugares que podem lhe agradar',
            'estou com sono', 'que tal fazer uma pausa? Aqui vão alguns lugares que podem lhe agradar',
            'não posso parar', 'que tal comer um pouco então? Uma fruta ou um doce ajudam a nos manter acordados',
            'tô com dor nas costas', 'vamos parar e fazer alguns alongamentos, pode ser?',
            'estou há muito tempo no volante', 'que tal fazer uma pausa? Se parece uma boa idéia diga: parece uma boa idéia, se não, pense em quando pode parar e me chame para fazer alguns alongamentos com você, dizendo, vamos alongar!!',
            'parece uma boa idéia', 'Ok, quando parar, me chame dizendo, vamos alongar!',
            'estou com fome', 'Vou pesquisar alguns lugares para você comer',
            'preciso abastecer', 'aqui vão alguns petroleiros próximos',
            'preciso de um lugar para passar a noite', 'aqui vão alguns hotéis próximos',
            'quero comer', 'aqui vão alguns lugares próximos para comer',
            'queria comida', 'aqui vão alguns restaurantes',
            'estou um fedor', 'procurando lugares para você tomar banho',
            'queria me limpar', 'procurando lugares com banheiro por perto',
            'preciso de um banho', 'procurando lugares onde você possa tomar banho',
            'vamos alongar!', 'carregando exercício']

#treina chatter com a conversa exemplo
trainer = ListTrainer(chatbot)
trainer.train(conversa)

def get_latlng():
    a = geocoder.ip('me')
    return a.latlng

def busca_proximidades(type_, keyword):
    latlng = get_latlng()
    link = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location='+str(latlng[0])+','+str(latlng[1])+'&radius=1500&type='+type_+'&keyword='+keyword+'&open_now=true&key='+google_maps_API_key
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

def alongar():
    instrucao = 'em pé segure com as mãos em algo firme. Mantenha os joelhos dobrados e faça uma corcunda largando o peso do corpo para trás. Mantenha a cabeça entre os braços e contraia o abdômem. Faça por 30 segundos'
    imagem = ''
    responde(instrucao)
    return instrucao


def checa_palavra(frase):
    if('posto' in frase or 'abastecer' in frase or 'petroleiro' in frase):
        a = busca_proximidades('posto', 'gasolina')
        return True, a
    if('passar a noite' in frase or 'dormir' in frase or 'dois metros horizontais' in frase):
        a = busca_proximidades('posto', 'pousada')
        return True, a
    if('comer' in frase or 'fome' in frase or 'comida' in frase or 'restaurante' in frase in frase):
        a = busca_proximidades('restaurante', 'comida')
        return True, a
    if('fedor' in frase or 'banho' in frase or 'limp' in frase):
        a = busca_proximidades('hotel', 'banheiro')
        return True, a
    if('cansado' in frase or 'descansar' in frase):
        a = busca_proximidades('posto', 'gasolina')
        return True, a
    if('banheiro' in frase or 'mijar' in frase):
        a = busca_proximidades('posto', 'banheiro')
        return True, a
    if('vamos alongar' in frase):
        a = alongar()
        return 2, a
    return False, []
#gera resposta audível e toca ela
def responde(resp):
    if (resp == ''):
        return
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
        comando_ = False
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
                        responde('Pode repetir por favor?')
                        continue
                    reconheceu = True

            
            resp = chatbot.get_response(str(text))
            print(float(resp.confidence))
            if float(resp.confidence)<0.3:
                resp = 'Não entendi o que foi dito!'
            resp = str(resp)
            responde(resp)
            comando, lugares = checa_palavra(text)
            comando_, lugares_ = checa_palavra(resp)
            if comando == 2:
                resp = lugares
            historico_fala.append(text)
            historico_resp.append(resp)
            print(comando)
            
    except sr.RequestError as e: 
        print("Could not request results; {0}".format(e)) 
          
    except Exception as e: 
        print("unknown error occured" + str(e))

    if comando == 2:
        return render(request, 'index.html', {'conversa':zip(historico_fala, historico_resp), 'imagem': True})
    elif comando_:
        return render(request, 'index.html', {'conversa':zip(historico_fala, historico_resp), 'lugares': lugares_})
    elif comando:
        return render(request, 'index.html', {'conversa':zip(historico_fala, historico_resp), 'lugares': lugares})
    else:
        return render(request, 'index.html', {'conversa':zip(historico_fala, historico_resp)})

def index(request):
    return render(request, 'index.html')

def atendimento(request):
    return render(request, 'atendimento.html')

def perfil(request):
    return render(request, 'perfil.html')

def guia(request):
    return render(request, 'guia_medica.html')