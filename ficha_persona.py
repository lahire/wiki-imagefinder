#!/usr/bin/python3
### ficha de persona
### Usa pywikibot para buscar parámetros de la ficha de personas*
### que no se encuentren en Wikidata

import pywikibot
from pywikibot import pagegenerators
from imagefinder import *
from queue import Queue
from threading import Thread

relaciones = {'twitter': 'P2002'}

site = pywikibot.Site('es', 'wikipedia')
repo = site.data_repository()

def addWikidata(page, prop, data):
    item = getQ(page)
    claim = pywikibot.Claim(repo, prop)
    claim.setTarget(data)
    item.addClaim(claim, summary=u'Adding twitter username')


def procesador(q, i):
    while True:
        check(q.get())
        q.task_done()

def check(page):
    twitter = getParameter(page, ['Ficha de persona'], 'twitter')
    if twitter != None:
        if pageHasP(page, 'P2002') == False:
            print("{0} - no twitter on Wikidata".format(page.title()))
            addWikidata(page, 'P2002', twitter.replace('@', '').replace('https://twitter.com/', ''))
        else:
            print("{0} - {1} already in Wikidata".format(page.title(), twitter))
            printToCsv(line=[page.title()], archivo='ficha_no.csv')
    else:
        print("{0} - no twitter".format(page.title()))
        printToCsv(line=[page.title()], archivo='ficha_no.csv')

def main():

    num_fetch_threads = 5

    cola = Queue()
    for i in range(num_fetch_threads):
        worker = Thread(target=procesador, args=(cola, i,))
        worker.setDaemon(True)
        worker.start()

    site = pywikibot.Site('es', 'wikipedia')
    generator = pagegenerators.ReferringPageGenerator(pywikibot.Page(source=site, title='Template:Ficha de persona'), onlyTemplateInclusion=True)
    pages = pagegenerators.PreloadingGenerator(generator, 200 if site.isBot(site.username()) else 50)
    listaRevisados = getCacheDump(dump='ficha_no.csv')
    #pages = [pywikibot.Page(site, 'Eduardo Duhalde')]
    for page in pages:
        if page.title() not in listaRevisados:
            cola.put(page)

    cola.join()


if __name__ == '__main__':
    main()
