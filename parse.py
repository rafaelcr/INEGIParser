#!/usr/bin/python

"""Parser INEGI

Recibe un TSV de informacion de cierta Entidad Federativa y lo transmite hacia
una base de datos MongoDB.
http://www3.inegi.org.mx/sistemas/descarga/default.aspx?c=28088

"""

__author__ = '@rafaelcr (Rafael Cardenas)'

import csv
import sys

class INEGIParser(object):

  def __init__(self, filename):
    self.rows = []
    self.cols = None
    self.parse(filename)
    print self.rows[0]

  def parse(self, filename):
    """Parsea los archivos hacia una lista de diccionarios"""
    inegi_tsv = open(filename, 'r')
    for line in csv.reader(inegi_tsv, dialect="excel-tab"):
      # la primer linea indica las columnas
      if not self.cols:
        self.cols = line
      else:
        # cada fila es un diccionario que se transmitira a MongoDB
        nrow = {}
        for i, val in enumerate(line):
          if val:
            nrow[self.cols[i]] = val
        self.rows.append(nrow)


def main():
  args = sys.argv[1:]
  if not args:
    print 'usage: parse.py [file...]'
    sys.exit(1)

  p = INEGIParser(args[0])

if __name__ == '__main__':
  main()