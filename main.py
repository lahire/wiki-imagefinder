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

CWD='/data/project/lahitools/wiki-imagefinder'
SITE = pywikibot.Site('es','wikipedia')
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
    if pageHasP(p, 'P18') == False:
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
    lista_images = getCacheDump('dump_images.csv')
    num_fetch_threads = 5

    cola = Queue(maxsize=400)
    for i in range(num_fetch_threads):
        worker = Thread(target=procesador, args=(cola, i,))
        worker.setDaemon(True)
        worker.start()

    try:
        chdir(CWD)
    except FileNotFoundError:
        pass

    ##Cleanup
    if path.isfile('dump_images.csv'):
        remove('dump_images.csv')
    saveOldDump()

    printToCsv(line=\
        ['Wikipedia', 'Imagen', 'URL Wikipedia', 'URL Q wikidata'],\
        archivo='dump_images.csv')

    generador = pagegenerators.CategorizedPageGenerator(\
                                                    pywikibot.Category(\
                                                    pywikibot.Link(\
                'Category:Wikipedia:Artículos con coordenadas en Wikidata')))
    LIMIT = 200 if SITE.isBot(SITE.username()) else 50
    pages = pagegenerators.PreloadingGenerator(generador, LIMIT)
    #for debug
    #pages = [pywikibot.Page(source=SITE,title='Þeistareykjarbunga')]

    lista_cache = getCacheDump('dump_skip.csv')

    for p in pages:
        if p.title() not in lista_cache:
            cola.put(p)
    cola.join()
    printHtml()

if __name__ == '__main__':
    main()
