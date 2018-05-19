#!/usr/bin/python3
### imagefinder
### Usa pywikibot para buscar articulos que tengan imagenes escritas a mano

import pywikibot
import time
import csv
import re
from shutil import copyfile
from os import path, remove
from pywikibot import pagegenerators

SITE = pywikibot.Site('es','wikipedia')
LIMIT = 50 #50 for no-bot users
DUMP='dump.csv'
#DUMP_TRUE='dump_true.csv' #Si tienen p18 TRUE
DUMPCACHE='dump.cache'
DELI='|'

def saveOldDump(dump=DUMP):
    """
    saveOldDump(dump=DUMP_TRUE):
        Guarda el dump.csv previo a la ejecución para tener una "caché"
        y lo abre en memoria
    """
    if path.isfile(dump):
        copyfile(dump,DUMPCACHE)
        return None
    else:
        print('No old dump to save')
        return None

def getCacheDump(dump=DUMPCACHE):
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

def isInDump(titulo, titulos):
    """
    checkDump(titulo, titulos):
        Analiza si la linea investigada existe en el dump
        True si está, False si no
    """
    #print('>>>> {0} - {1}'.format(titulo, titulos))
    #print(titulo in titulos)
    return titulo in titulos

def returnTemplates(templates):
    """
    returnTemplates(templates):
        Devuelve una lista con el nombre de la plantilla:Ficha que tiene el
        artículo. Si no tiene, devuelve un array vacío
    """
    lista_plantilla = list(filter(\
        lambda x: x[0].title().find('Plantilla:Ficha') > -1 or \
        x[0].title().find('Plantilla:Infobox') > -1  , \
         templates))
    return lista_plantilla

def getPhoto(params):
    """
    getPhoto(params):
        Si la plantilla (params) que se le pasa tiene un parámetro de foto
        devuelve el nombre de la foto. de lo contrario, None
    """
    imagen=list(filter(\
    lambda x :\
    x.find('foto=',0,5) > -1 or \
    x.find('photo=',0,6) > -1 or \
    x.find('image=',0,6) > -1 or \
    x.find('imagen=',0,7) > -1\
    ,params[0][1]))
    if len(imagen) == 0:
        return None
    imagen = imagen[0].split('=', 1)[1]
    return None if len(imagen.strip()) == 0 else imagen.strip()

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
    return property in item.toJSON().get('claims').keys()

def hasWikidataImage(page):
    """
    hasWikidataImage(page):
        Retorna si el objeto en Wikidata
        tiene una propiedad de imagen asociada o no
    """
    wikidataItem = getQ(page)
    if wikidataItem != None:
        return QhasP(wikidataItem, 'P18')
    return None

def printToCsv(line, archivo=DUMP,separador=DELI):
    """
    printToCsv(archivo='dump.csv',delimeter=';',line):
    Imprime en archivo la linea, separada por separador como csv
    Jara (Asunción)|Avenida brasilia asuncion paraguay.jpg|<URL>
    """
    with open(archivo,'a') as csv_file:
        writer = csv.writer(csv_file, delimiter=separador)
        writer.writerow(line)
    return None

def main():
    """
    main():
        Main loop
    """
    ##Cleanup
    if path.isfile('dump_images.csv'):
        remove('dump_images.csv')
    saveOldDump()

    generador = pagegenerators.CategorizedPageGenerator(\
                                                    pywikibot.Category(\
                                                    pywikibot.Link(\
                'Category:Wikipedia:Artículos con coordenadas en Wikidata')))
    #for debug
    pages = pagegenerators.PreloadingGenerator(generador, LIMIT)
    #pages = [pywikibot.Page(source=SITE,title='A-138')]

    lista_cache = getCacheDump('dump_skip.csv')
    for p in pages:
        if isInDump(p.title(), lista_cache):
            print('>>>> {0} in dump'.format(p.title()))
            continue
        else:
            print('{0} not in dump'.format(p.title()))
        lista_plantilla = returnTemplates(p.templatesWithParams())
        if len(lista_plantilla) == 0:
            continue
        imagen = getPhoto(lista_plantilla)
        if imagen == None:
            continue
        if hasWikidataImage(p) == False:
            if imagen.find('|') > -1:
                match = re.match(r"\[{2}(Archivo|Media|File):(.[^\|]*)",\
                                 imagen)
                if match != None:
                    imagen = match.group(2)
            if imagen.lower().find('falta ') > -1 or imagen.find('{{') > -1:
                continue
            printToCsv(line=\
                [p.title(), imagen, p.full_url(), getQ(p).full_url()],\
                 archivo='dump_images.csv')
            #print('Title: {0} || Image: {1} || WikidataP18?: {2}'\
            #    .format(p.title(), imagen, tieneP18))
        else:
            printToCsv(line=[p.title()], archivo='dump_skip.csv')

if __name__ == '__main__':
    main()
