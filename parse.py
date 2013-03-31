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
    self.entradas = {}
    self.path = directory.strip('/')
    self.entidad = self.path.split('/')[-1:][0][:-3]
    self.parse()

  def parse(self):
    """Parsea los archivos hacia diccionarios."""
    with open('%s/%sValor.tsv' % (self.path, self.entidad)) as inegi_tsv:
      for l, line in enumerate(csv.reader(inegi_tsv, dialect="excel-tab")):
        if not self.columnas:
          self.columnas = line
          continue
        self.parseline(line, 'valor')
    with open('%s/%sUnidadMedida.tsv' % (self.path, self.entidad)) as inegi_tsv:
      for l, line in enumerate(csv.reader(inegi_tsv, dialect="excel-tab")):
        if l==0:
          continue
        self.parseline(line, 'unidades')
    with open('%s/%sFuente.tsv' % (self.path, self.entidad)) as inegi_tsv:
      for l, line in enumerate(csv.reader(inegi_tsv, dialect="excel-tab")):
        if l==0:
          continue
        self.parseline(line, 'fuente')

  def parseline(self, line, source):
    entrada = {}
    for i, val in enumerate(line):
      if val:
        if self.columnas[i].isdigit():
          entrada[self.columnas[i]] = {source: val}
        else:
          entrada[self.columnas[i]] = val
    self.organize(entrada, source)

  def organize(self, entrada, source):
    key = '%s-%s' % (entrada['Cve_Municipio'], entrada['Id_Indicador'])
    if not (key in self.entradas):
      self.entradas[key] = entrada
    else:
      for k in entrada.iterkeys():
        if k.isdigit():
          if not (k in self.entradas[key]):
            self.entradas[key][k] = entrada[k]
          else:
            self.entradas[key][k][source] = entrada[k][source]

def main():
  args = sys.argv[1:]
  if not args:
    print 'usage: parse.py [directory...]'
    sys.exit(1)

  p = INEGIParser(args[0])
  print p.entradas

if __name__ == '__main__':
  main()