import os
import pickle
import re
import unidecode
import json
import requests

from bs4 import BeautifulSoup

from flask import render_template, request, Flask

ejemplo = "La inflación de noviembre fue del 3,2\xa0% en comparación a octubre de 2020, mientras que respecto de noviembre de 2019 el aumento fue del 35,8\xa0%, según informó este martes el Indec. El rubro Alimentos y bebidas no alcohólicas subió en un año 40,4\xa0%, es decir por encima del nivel general. El organismo también indicó que el acumulado en el año es de 30,9\xa0%.La inflación núcleo, aquella que no incluye a los precios de productos o servicios estacionales y regulados, aceleró hasta 3,9\xa0% mensual; en octubre, había aumentado 3,5\xa0%.El organismo informó que la división Recreación y cultura fue la que mostró el mayor incremento en noviembre (5,1\xa0%), debido a la mayor apertura de actividades recreativas presenciales en gimnasios y alquiler de canchas. Sin embargo, la división Alimentos y bebidas no alcohólicas (2,7\xa0%) registró la mayor incidencia en todas las regiones. Se destacaron en este último caso las subas en Carnes y derivados; Frutas; y Aceites, grasas y manteca.En noviembre se registraron fuertes subas de las carnes, las frutas y verduras. También el Gobierno autorizó aumentos de Precios Máximos.Los rubros que más subieron fueron Recreación y Cultura, con un aumento del 5,1\xa0%; Equipamiento y mantenimiento del hogar, 3,9\xa0%; Prendas de vestir y calzado, Salud con 3,7\xa0%. Mientras que los que menos subieron fueron Educación, con un 0,4\xa0%, y Comunicación, -0,6\xa0%.Los consultores económicos que integran el Relevamiento de Expectativas de Mercado (REM) del Banco Central proyectan una inflación para este año de 36,7\xa0%.La suba de los precios impacta en el poder adquisitivo de los salarios, que ya perdieron en la era Macri (más del 20\xa0%) y este año tendrán un nuevo derrumbe. Las paritarias negociadas en 2020 profundizan el deterioro porque los ajustes son menores a la inflación que se calcula este año.Te puede interesar: El primer año de Alberto: balance y perspectivas"

class Config:
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

app = Flask(__name__)
app.config.from_object(Config)

def removal(text):
    text = re.sub(r'(\d|\$|\%|\+)', '', text.lower())
    no_accents = unidecode.unidecode(re.sub(r'\d+', '', text))
    return no_accents

with open('core/vectorizer.pkl', 'rb') as f:
	vectorizer = pickle.load(f)

with open('core/classifier.pkl', 'rb') as f:
	classifier = pickle.load(f)

def parse_response(url):
    respuesta = requests.get(
        url,
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'
        }
    )
    return BeautifulSoup(respuesta.content, "html.parser")

def predecir(texto):

    text_vectorized = vectorizer.transform([texto])
    bias_prob = classifier.predict_proba(text_vectorized)

    data = []
    for key, value in zip(vectorizer.get_feature_names(), text_vectorized.todense().tolist()[0]):
        if value == 0:
            pass
        else:
            data.append({"x":key,"value":value, "category":"noun"})

    return data, bias_prob

@app.route('/', methods=['GET','POST'])
def index():

    data = None
    bias = None
    portal = None
    label = None

    if request.method == 'POST':
        if re.match("http", request.form.get('text'), re.IGNORECASE):
            if re.search("izquierda", request.form.get('text'), re.IGNORECASE):
                print('izquierda diario')
                # soup = parse_url(request.form.get('text'))
                # print(soup.find('div', {'class': 'articulo'}).findAll('p'))
            elif re.search("derechadiario", request.form.get('text'), re.IGNORECASE):
                articulo = parse_response(request.form.get('text')).find('div', {'class':"jsx-2701897770 editor body"}).text
                data, bias = predecir(articulo)
                portal = 'Derecha Diario'
            elif re.search("lanacion", request.form.get('text'), re.IGNORECASE):
                texto = ""
                articulo = parse_response(request.form.get('text')).findAll('p', {'class':"com-paragraph"})
                for parrafo in articulo:
                    texto += parrafo.text
                data, bias = predecir(texto)
                portal = 'La Nación'
            elif re.search("cronista", request.form.get('text'), re.IGNORECASE):
                articulo = parse_response(request.form.get('text')).find('div', {'class':"content vsmcontent"}).text
                data, bias = predecir(articulo)
                portal = 'El Cronista'
            elif re.search("pagina", request.form.get('text'), re.IGNORECASE):
                articulo = parse_response(request.form.get('text')).find('div', {'class':"article-main-content article-text"}).text
                data, bias = predecir(articulo)
                portal = 'Página 12'

        if bias[0][0] < 0.3:
            label = "Right"
        elif bias[0][0] > 0.7:
            label = 'Left'
        else:
            label = 'Center'
        print(bias)
        bias = int(bias[0][1]*100)

    return render_template(
        "home.html", 
        title='Bias Detector', 
        wc=data, 
        bias=bias, 
        portal=portal, 
        label=label
    )

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug = True)