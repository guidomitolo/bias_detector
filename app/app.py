import os
import re
import requests

import dill

from bs4 import BeautifulSoup

from flask import render_template, request, Flask

from textblob import TextBlob

from nltk.tag import StanfordPOSTagger

from collections import defaultdict

jar = 'stanford_tagger/stanford-postagger.jar'
model = 'stanford_tagger/models/spanish-ud.tagger'
pos_tagger = StanfordPOSTagger(model, jar, encoding='utf8' )

class Config:
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

app = Flask(__name__)
app.config.from_object(Config)

with open('core/vectorizer.dill', 'rb') as f:
	vectorizer = dill.load(f)

with open('core/classifier.dill', 'rb') as f:
	classifier = dill.load(f)

def parse_response(url):
    respuesta = requests.get(
        url,
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'
        }
    )
    return BeautifulSoup(respuesta.content, "html.parser")

def predecir(texto):

    cantidad = len(texto.split(" "))

    text_vectorized = vectorizer.transform([texto])
    bias_prob = classifier.predict_proba(text_vectorized)
    tags = pos_tagger.tag(vectorizer.get_feature_names())

    lexicon = defaultdict(int)

    data = []

    for key, value, tag in zip(vectorizer.get_feature_names(), text_vectorized.todense().tolist()[0], tags):
        if value == 0:
            pass
        else:
            data.append({"x":key,"value":value, "category": tag[1]})
            lexicon[tag[1]] += 1


    tags = list(lexicon.keys())
    nums = list(lexicon.values())

    return data, bias_prob, cantidad, tags, nums

@app.route('/', methods=['GET','POST'])
def index():

    data = None
    bias = None
    portal = None
    label = None
    aviso = None
    cantidad = None

    tags = None
    nums = None

    if request.method == 'POST':
        if re.match("http", request.form.get('text'), re.IGNORECASE):
            if re.search("lanueva", request.form.get('text'), re.IGNORECASE):
                texto = ""
                articulo = parse_response(request.form.get('text')).find('div', {'class':"desarrollo width100"})
                children = articulo.findChildren("p" , recursive=False)
                for child in children:
                    texto += child.text
                data, bias, cantidad, tags, nums = predecir(texto)
                portal = 'La Nueva Provincia'
            elif re.search("derechadiario", request.form.get('text'), re.IGNORECASE):
                articulo = parse_response(request.form.get('text')).find('div', {'class':"jsx-2701897770 editor body"}).text
                data, bias, cantidad, tags, nums = predecir(articulo)
                portal = 'Derecha Diario'
            elif re.search("lanacion", request.form.get('text'), re.IGNORECASE):
                texto = ""
                articulo = parse_response(request.form.get('text')).findAll('p', {'class':"com-paragraph"})
                for parrafo in articulo:
                    texto += parrafo.text
                data, bias, cantidad, tags, nums = predecir(texto)
                portal = 'La Nación'
            elif re.search("cronista", request.form.get('text'), re.IGNORECASE):
                articulo = parse_response(request.form.get('text')).find('div', {'class':"content vsmcontent"}).text
                data, bias, cantidad, tags, nums = predecir(articulo)
                portal = 'El Cronista'
            elif re.search("pagina", request.form.get('text'), re.IGNORECASE):
                articulo = parse_response(request.form.get('text')).find('div', {'class':"article-main-content article-text"}).text
                data, bias, cantidad, tags, nums = predecir(articulo)
                portal = 'Página 12'
            else:
                aviso = 'News Portal unidentified'

            if bias is not None:
                if bias[0][0] < 0.3:
                    label = "Right"
                elif bias[0][0] > 0.7:
                    label = 'Left'
                else:
                    label = 'Center'
                bias = int(bias[0][1]*100)

        else:
            aviso = 'This is not a web page!'

    return render_template(
        "home.html", 
        title='Bias Detector', 
        wc=data, 
        bias=bias, 
        portal=portal, 
        label=label,
        mensaje = aviso,
        cantidad=cantidad,
        tags = tags,
        nums = nums
    )

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug = True)