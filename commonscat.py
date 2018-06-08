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

def work(pages):
    listaRevision = getCacheDump('has.csv')

    for page in pages:
        if page.exists() == False or page.namespace() not in [0, 104] or page.title() in listaRevision:
            print ('<<< {0} skipped'.format(page.title()))
            continue
        elif pageHasP(page, 'P373') == False:
            print ('>>> {0} has no P373'.format(page.title()))
            lista = hasTemplate(page, ['Commonscat', 'Commons cat', 'Categoría Commons', 'Commonscat-inline', 'Commons category', 'Commons category-inline'])
            parameters = (lista[0][1])
            category = category[0].replace('1=', '') if len(parameters) > 0 else page.title(withNamespace=False)
            printToCsv(line=[page.full_url(),getQ(page).full_url(),page.title(),category], archivo='hasno.csv')
        else:
            print('{0} has P373'.format(page.title()))
            printToCsv(line=[page.title()], archivo='has.csv')

def write_result():
    write_file('templates/commons.tpl', 'commons.html', getNow(), getGitVersion())

def main(*args):
    ##Cleanup
    site = pywikibot.Site('es', 'wikipedia')
    local_args = pywikibot.handle_args(args)
    page = None
    for arg in local_args:
        if arg.startswith('-page:'):
            page = arg[6:]
            pages = [pywikibot.Page(source=site, title=page)]
    if page == None:
        tpl = pywikibot.Page(source=site, title='Template:Commonscat')
        pages = pagegenerators.ReferringPageGenerator(tpl)

    if path.isfile('hasno.csv'):
        remove('hasno.csv')
    if path.isfile('hasno.json'):
        remove('hasno.json')

    work(pages)
    write_result()

if __name__ == '__main__':
    main()
