#!/usr/bin/python3
### commonscat
### Usa pywikibot para buscar commonscat en Wikipedia en español y chequea que
### no este en Wikidata

import pywikibot
import csv
import re
from pywikibot import pagegenerators
from imagefinder import *

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
