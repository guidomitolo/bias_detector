### Bias Detector App

A simple Flask web-based app that analyses news portals political bias with NLP.

https://bias-reader.herokuapp.com/

#### 1. NLP Core

CountVectorizer + SGDClassifier model trained on a dataset composed with news gathered from two antagonistic news portal.

#### 2. EDA on vectors

Terms analysis done with NLTK and a java-based POS-tagger model for spanish provided by Stanford.

#### 3. News parsing

Vector transformation done on parsed news with bs4.

#### 4. Presentation

Charts JS engine provided by AnyChart and Charts.js 

#### 5. Deployment

a. Heroku

Procfile, nltk_data and nltk.txt included. Add heroku/java as buildpack.

b. Docker

Built on ubuntu image with java and python.

```
docker-compose up --build
```



