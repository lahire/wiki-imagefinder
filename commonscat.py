#!/usr/bin/python3
### commonscat
### Usa pywikibot para buscar commonscat en Wikipedia en español y chequea que
### no este en Wikidata

import pywikibot
import csv
import re
from pywikibot import pagegenerators

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

def hasWikidataCategory(page):
    """
    hasWikidataImage(page):
        Retorna si el objeto en Wikidata
        tiene una propiedad de imagen asociada o no
    """
    wikidataItem = getQ(page)
    if wikidataItem != None:
        return QhasP(wikidataItem, 'P373')
    return None

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

def main():
    site = pywikibot.Site('es', 'wikipedia')
    listaRevision = getCacheDump('has.csv')
    generator = pagegenerators.ReferringPageGenerator(pywikibot.Page(source=site, title='Template:Commonscat'))
    for p in generator:
        if p.namespace() not in [0, 104] or p.title() in listaRevision:
            print ('<<< {0} skipped'.format(p.title()))
            continue
        elif hasWikidataCategory(p) == False:
            print ('>>> {0} has no P373'.format(p.title()))
            lista = list(filter(lambda x: x[0].title(withNamespace=False).find('Commonscat') > -1, p.templatesWithParams()))
            parameters = (lista[0][1])
            if len(parameters) > 0:
                category = parameters[0]
            else:
                category = p.title(withNamespace=False)
            printToCsv(line=[p.full_url(),getQ(p).full_url(),p.title(),category], archivo='hasno.csv')
        else:
            print('{0} has P373'.format(p.title()))
            printToCsv(line=[p.title()], archivo='has.csv')

if __name__ == '__main__':
    main()
