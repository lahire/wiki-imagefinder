#!/usr/bin/python3
### commonscat
### Usa pywikibot para buscar commonscat en Wikipedia en español y chequea que
### no este en Wikidata

import pywikibot
import csv
import re
from pywikibot import pagegenerators
from imagefinder import *
from os import path, remove

def main():
    ##Cleanup
    if path.isfile('hasno.csv'):
        remove('hasno.csv')
    site = pywikibot.Site('es', 'wikipedia')
    listaRevision = getCacheDump('has.csv')
    generator = pagegenerators.ReferringPageGenerator(pywikibot.Page(source=site, title='Template:Commonscat'))
    for p in generator:
        if p.namespace() not in [0, 104] or p.title() in listaRevision:
            print ('<<< {0} skipped'.format(p.title()))
            continue
        elif pageHasP(p, 'P373') == False:
            print ('>>> {0} has no P373'.format(p.title()))
            lista = hasTemplate(p, ['Commonscat', 'Commons cat', 'Categoría Commons', 'Commonscat-inline', 'Commons category', 'Commons category-inline'])
            parameters = (lista[0][1])
            if len(parameters) > 0:
                category = parameters[0]
            else:
                category = p.title(withNamespace=False)
            printToCsv(line=[p.full_url(),getQ(p).full_url(),p.title(),category], archivo='hasno.csv')
            createJSON('hasno.csv', ['wikipedia', 'wikidata', 'article', 'category_commons'])
        else:
            print('{0} has P373'.format(p.title()))
            printToCsv(line=[p.title()], archivo='has.csv')
            printHtml(output='has.csv')
if __name__ == '__main__':
    main()
