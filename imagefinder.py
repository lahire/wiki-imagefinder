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
import datetime
from os import path, remove, chdir

def getQ(page):
    """
    getQ(page):
        Obtiene el Q de la página. Si no tiene, devuelve None
    """
    try:
        return page.data_item()
    except pywikibot.exceptions.NoPage:
        print('{0} has no Q element.'.format(page))
        return None

def pageHasP(page, property):
    """
    pageHasP(page, property):
        Determina si la página page tiene la propiedad P
    """
    wikidataItem = getQ(page)
    if wikidataItem == None:
        return False
    return QhasP(wikidataItem, property)

def QhasP(item, property='P18'):
    """
    QhasP(item):
        Devueve True si el Q tiene propiedad P. False si no.
    """
    if 'claims' not in item.toJSON().keys():
        return False
    return property in item.toJSON().get('claims').keys()

def getLimite(site):
    """
    getLimite(site):
        Obtiene el límite de páginas que puede obtener previamente.
        Si el usuario es bot se limita a 200, sino a 50
    """
    return 200 if site.isBot(site.username()) else 50

def printToCsv(line, archivo='dump.csv',separador='|'):
    """
    printToCsv(archivo='dump.csv',delimeter=';',line):
    Imprime en archivo la linea, separada por separador como csv
    Jara (Asunción)|Avenida brasilia asuncion paraguay.jpg|<URL>
    """
    with open(archivo,mode='a', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file, delimiter=separador)
        writer.writerow(line)
    return None

def getCacheDump(dump='dump.csv'):
    """
    getCacheDump(dump):
        Obtiene el elemento del cache según la especificación de CSV
    """
    try:
        dumpstring = []
        with open(dump, mode='rt', encoding='utf-8') as archivo:
            for row in csv.reader(archivo, delimiter='|'):
                dumpstring.append(row[0])
        return sorted(dumpstring)
    except FileNotFoundError:
        return []

def hasTemplate(page, categoriesToCheck=[]):
    """
    hasTemplate(page, categoriesToCheck):
        Determina si las categorias de una página está presente en
        las catregorias a comprobar
    """
    categories = filter(lambda x: x[0].title(withNamespace=False) in categoriesToCheck, page.templatesWithParams())
    return list(categories)

def getParameter(page, templates=[], parameter=''):
    """
    getParameter(page, templates=[], parameter=''):
        Obtiene un parametro desde las plantillas de búsqueda
        En caso de no encontrar el parámetro, retorna None
    """
    templates = hasTemplate(page, templates)
    for template, parameters in templates:
        for param in parameters:
            param = param.strip()
            if param.find(parameter+'=') > -1:
                parametro = param.replace(parameter+'=', '').strip()
                return None if len(parametro) == 0 else parametro
    return None

def getLimite(site):
    """
    getLimite(site):
        Obtiene el valor limite a obtener si el usuario actual es un bot o no
        Se deja en 200, a pesar que el límite sean 500 por un tema de red
    """
    return 200 if site.isBot(site.username()) else 50

def createJSON(dump, keys=[]):
    """
    createJSON(dump, keys):
        Crea un archivo json dump.json a partir de un dump.csv
        con las cabeceras keys
    """
    elements = []
    try:
        with open(dump,'rt') as archivo:
            for row in csv.reader(archivo, delimiter='|'):
                elements.append(dict(zip(keys, row)))
    except FileNotFoundError:
        items = []
    with open(dump.replace('.csv', '.json'), mode='w', encoding='utf-8') as json_archive:
        json_archive.write(json.dumps(elements))

def getConfigFile(cwd, file="/.config"):
    """
    getConfigFile(cwd, file="/.config"):
        Obtiene el archivo de configuracion desde un directorio externo o
        desde el directorio actual.
        En caso de ser falso, retorna None
    """
    if path.isfile(cwd+file) == False:
        if path.isfile('.'+file) == False:
            return None
        return '.'+file
    return cwd+file

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

    """.format(datetime.datetime.now().utcnow().month,\
               datetime.datetime.now().utcnow().day,\
               datetime.datetime.now().utcnow().year,\
               datetime.datetime.now().utcnow().hour,\
               datetime.datetime.now().utcnow().minute)
    with open('index.html',mode='w', encoding='utf-8') as f:
        f.write(HTML)
