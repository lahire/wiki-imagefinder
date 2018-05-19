#!/usr/bin/python3
### imagefinder
### Usa pywikibot para buscar articulos que tengan imagenes escritas a mano

import pywikibot
import time
import json
from pywikibot import pagegenerators

SITE= pywikibot.Site('es','wikipedia')
generador = pagegenerators.CategorizedPageGenerator(\
                                                pywikibot.Category(\
                                                pywikibot.Link(\
            'Category:Wikipedia:Artículos con coordenadas en Wikidata')))
#pages = [pywikibot.Page(source=SITE,title='Ruta de Illinois 21')]
pages = pagegenerators.PreloadingGenerator(generador, 50)

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

for p in pages:
        lista_plantilla = returnTemplates(p.templatesWithParams())
        if len(lista_plantilla) == 0:
            continue
        imagen = getPhoto(lista_plantilla)
        if imagen == None:
            continue
        tieneP18 = hasWikidataImage(p)
        if tieneP18 == False:
            print('Title: {0} || Image: {1} || WikidataP18?: {2}'\
                .format(p.title(), imagen, tieneP18))
        else:
            print ('Title: {0} - has P18'.format(p.title()))

#templates=PAGE.raw_extracted_templates
#templates=templates[0][1]
#if 'image' in templates.keys():
#    DICKEY='image'
#else:
#    DICKEY='imagen'
#print('Start Process')
