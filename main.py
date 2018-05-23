#!/usr/bin/python3
### imagefinder
### Usa pywikibot para buscar articulos que tengan imagenes escritas a mano

import pywikibot
import time
import csv
import re
from shutil import copyfile
from os import path, remove, chdir
from pywikibot import pagegenerators
from imagefinder import *
from queue import Queue
from threading import Thread
import configparser


CWD='/data/project/lahitools/wiki-imagefinder'
CONFIG='{0}/.config'.format(CWD)

DUMP='dump_skip.csv'
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

def isInDump(titulo, titulos):
    """
    isInkDump(titulo, titulos):
        Analiza si la linea investigada existe en el dump
        True si está, False si no
    """
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
    if config['SITE']['site'] == 'wikipedia':
        if config['SITE']['language'] == 'es':
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
        if config['SITE']['language'] == 'en':
            imagen=list(filter(\
            lambda x :\
            x.find('photo=',0,6) > -1 or \
            x.find('image=',0,6) > -1 \
            ,params[0][1]))
            if len(imagen) == 0:
                return None
            imagen = imagen[0].split('=', 1)[1]
                return None if len(imagen.strip()) == 0 else imagen.strip()
#esto suena a poco óptimo si llega a crecer
    else:
        # No se como procesar otras cosas, solo para es.wiki
        return None
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

def procesador(q, i):
    """
    procesador(q,i):
        Bucle infinito que corre los elementos en la cola
    """
    while True:
        p = q.get()
        factoring(p)
        q.task_done()

def factoring(p):
    """
    factoring(p):
        Realiza verificaciones y escrituras en los csv usando p
        Esta funcion se llama repetidas veces en procesador
    """
    lista_plantilla = returnTemplates(p.templatesWithParams())
    if len(lista_plantilla) == 0:
        return None
    imagen = getPhoto(lista_plantilla)
    if imagen == None:
        return None
    if hasWikidataImage(p) == False:
        if imagen.find('|') > -1:
            match = re.match(r"\[{2}(Archivo|Media|File|Imagen?):(.[^\|]*)",\
                             imagen,flags=re.IGNORECASE)
            if match != None:
                imagen = match.group(2)
        if imagen.lower().find('falta ') > -1 or imagen.find('{{') > -1:
            return None

        printToCsv(line=\
            [p.title(), imagen, p.full_url(), getQ(p).full_url()],\
            archivo='dump_images.csv')
    else:
        printToCsv(line=[p.title()], archivo='dump_skip.csv')

def main():
    """
    main():
        Main loop
    """
    lista_images = getCacheDump(config['FILES']['images'])
    num_fetch_threads = config['THREAD']['threads']

    cola = Queue(config['THREAD']['threads'])
    for i in range(num_fetch_threads):
        worker = Thread(target=procesador, args=(cola, i,))
        worker.setDaemon(True)
        worker.start()

    try:
        chdir(CWD)
    except FileNotFoundError:
        pass

    ##Cleanup
    if path.isfile(config['FILES']['images']):
        remove(config['FILES']['images'])
    saveOldDump()

    generador = pagegenerators.CategorizedPageGenerator(\
                                                    pywikibot.Category(\
                                                    pywikibot.Link(\
                config['SITE']['cat'])))
    LIMIT = 200 if SITE.isBot(SITE.username()) else 50
    pages = pagegenerators.PreloadingGenerator(generador, LIMIT)
    #for debug
    #pages = [pywikibot.Page(source=SITE,title='Þeistareykjarbunga')]

    lista_cache = getCacheDump(config['FILES']['images'])

    for p in pages:
        if isInDump(p.title(), lista_cache) == False:
            cola.put(p)
    cola.join()
    printHtml()

if __name__ == '__main__':
    if os.path.isfile(CONFIG) == False:
            print('Error: ¿existe el archivo en {0}?'.format(CONFIG))
            exit(1)
    else:
        config = configparser.ConfigParser()
        config.read(CONFIG)
        #Declaro SITE
        SITE = pywikibot.Site(config['SITE']['language'],config['SITE']['site'])
    main()
