#!/usr/bin/python

"""Parser INEGI

Recibe un TSV de informacion de cierta Entidad Federativa y lo transmite hacia
una base de datos MongoDB.
http://www3.inegi.org.mx/sistemas/descarga/default.aspx?c=28088

Los nombres de archivos y directorios estan basados en la convencion de nombres
especificada por INEGI

"""

__author__ = '@rafaelcr (Rafael Cardenas)'

import csv
import sys

class INEGIParser(object):

  def __init__(self, directory):
    self.columnas = None
    self.valores = {}
    self.unidades = {}
    self.fuentes = {}
    self.path = directory.strip('/')
    self.entidad = self.path.split('/')[-1:][0][:-3]
    self.parse()

  def parse(self):
    """Parsea los archivos hacia diccionarios."""
    filelist = ['%sValor.tsv' % (self.entidad),
      '%sUnidadMedida.tsv' % (self.entidad),
      '%sFuente.tsv' % (self.entidad)]
    dictlist = [self.valores, self.unidades, self.fuentes]
    for f, filename in enumerate(filelist):
      with open('%s/%s' % (self.path, filename), 'r') as inegi_tsv:
        for l, line in enumerate(csv.reader(inegi_tsv, dialect="excel-tab")):
          # la primer linea indica las columnas
          if not self.columnas:
            self.columnas = line
          else:
            # ignorar la primera linea si ya tenemos las columnas
            if l == 0:
              continue
            entrada = {}
            for i, val in enumerate(line):
              if val:
                entrada[self.columnas[i]] = val
            dictlist[f][entrada['Id_Indicador']] = entrada
    print self.valores[0]

def main():
  args = sys.argv[1:]
  if not args:
    print 'usage: parse.py [directory...]'
    sys.exit(1)

  p = INEGIParser(args[0])

if __name__ == '__main__':
  main()