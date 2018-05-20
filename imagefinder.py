#!/usr/bin/python3
### Imagefinder Lib
### Funciones comunes para main.py (el main runner de imagefinder)
### y commonscat
### Idealmente con from imagefinder import *, teniendo este .py en el mismo cwd
### debería andar
### Mantenedor: Lahi | Usuario:Lahi


import pywikibot
import csv

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
