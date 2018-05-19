#!/usr/bin/python3
### Imagefinder Lib
### Funciones comunes para main.py (el main runner de imagefinder)
### y commonscat
### Idealmente con from imagefinder import *, teniendo este .py en el mismo cwd
### debería andar
### Mantenedor: Lahi | Usuario:Lahi


import pywikibot
import csv
import json
import time

def getQ(page):
    """
    getQ(page):
        Obtiene el Q de la página. Si no tiene, devuelve None
    """
    try:
        return pywikibot.ItemPage.fromPage(page)
    except pywikibot.exceptions.NoPage:
        print('{0} has no Q element.'.format(page))
        return None

def QhasP(item, property='P18'):
    """
    QhasP(item):
        Devueve True si el Q tiene propiedad P. False si no.
    """
    if 'claims' not in item.toJSON().keys():
        return False
    return property in item.toJSON().get('claims').keys()

def printToCsv(line, archivo='dump.csv',separador='|'):
    """
    printToCsv(archivo='dump.csv',delimeter=';',line):
    Imprime en archivo la linea, separada por separador como csv
    Jara (Asunción)|Avenida brasilia asuncion paraguay.jpg|<URL>
    """
    with open(archivo,'a') as csv_file:
        writer = csv.writer(csv_file, delimiter=separador)
        writer.writerow(line)
    return None

def getCacheDump(dump='dump.csv'):
    """
    getCacheDump(dump):
        Obtiene el cache y limpia los retorno de carro
    """
    try:
        with open(dump,'rt') as archivo:
            dumpstring = archivo.readlines()
        return sorted([item.strip() for item in dumpstring])
    except FileNotFoundError:
        return []

def isInCategory(page, categoriesToCheck=[]):
    """
    isCategory(page, categoriesToCheck):
        Determina si las categorias de una página está presente en
        las catregorias a comprobar
    """
    categories = filter(lambda x: x[0].title(withNamespace=False) in categoriesToCheck, page.templatesWithParams())
    return list(categories)

def createJSON(dump, keys=[]):
    elements = []
    try:
        with open(dump,'rt') as archivo:
            for row in csv.reader(archivo, delimiter='|'):
                elements.append(dict(zip(keys, row)))
    except FileNotFoundError:
        items = []
    with open(dump.replace('.csv', '.json'), 'w') as json_archive:
        json_archive.write(json.dumps(elements))

def printHtml():
    """
    printHTML():
        Imprime el HTML para mostrar al final
    """
    HTML="""
    <html>
    <title>Lahitools | ImageFinder </title>
    <h1> ImageFinder </h1>
    <p>Simple tool to create a csv that looks for articles with image on spanish wikipedia with no p18 on Wikidata</p>
    <p>The csv separator is a pipe: | </p>
    <p>The order as of this moment is: Spanish Article Title | image_name.extension | URL to es.wiki | URL to Q in Wikidata</p>
    <p>My first tool, be gentle</p>

    <a href='https://github.com/lahire/wiki-imagefinder'>Github of this silly thing</a>
    <br/>
    <br/>
    <a href='output.csv'>Download csv here!</a>
    <p> Last modified: {0}/{1}/{2} {3}:{4} UTC </p>
    <br/>
    :D
    </html>

    """.format(timedate.timedate.now().utcnow().month,\
               timedate.timedate.now().utcnow().day,\
               timedate.timedate.now().utcnow().year,\
               timedate.timedate.now().utcnow().hour,\
               timedate.timedate.now().utcnow().minute)
    with open('index.html','w') as f:
        f.write(HTML)
