#!/usr/bin/python

"""Parser INEGI

Recibe un TSV de informacion nacional y lo transmite hacia
una base de datos PostgreSQL.
http://www3.inegi.org.mx/sistemas/descarga/default.aspx?c=28088

Los nombres de archivos y directorios estan basados en la convencion de nombres
especificada por INEGI
"""

__author__ = '@rafaelcr (Rafael Cardenas)'

import csv
import psycopg2
import sys

class INEGIParser(object):

  def __init__(self):
    self.dbconfigure()
    self.parse()
    self.dbclose()

  def dbconfigure(self):
    self.sqlconn = psycopg2.connect("dbname=inegi user=rafaelcr host=localhost")
    self.sqlconn.autocommit = True
    self.sql = self.sqlconn.cursor()
    self.sql.execute("CREATE TABLE IF NOT EXISTS entidad (\
      id varchar(2) PRIMARY KEY,\
      nombre varchar);")
    self.sql.execute("CREATE TABLE IF NOT EXISTS municipio (\
      entidad varchar(2) references entidad(id),\
      id varchar(3),\
      nombre varchar);")
    self.sql.execute("CREATE TABLE IF NOT EXISTS indicador (\
      id bigint PRIMARY KEY,\
      descripcion varchar);")
    self.sql.execute("CREATE TABLE IF NOT EXISTS valor (\
      indicador bigint references indicador(id),\
      municipio varchar(3),\
      entidad varchar(2),\
      anio integer,\
      valor numeric(20,5));")
    self.sql.execute("CREATE TABLE IF NOT EXISTS categoria (\
      id serial PRIMARY KEY,\
      nombre varchar,\
      parent serial);")
    self.sql.execute("CREATE TABLE IF NOT EXISTS nota (\
      indicador bigint references indicador(id),\
      notas varchar);")

  def dbclose(self):
    self.sql.close()
    self.sqlconn.close()

  def parse(self):
    path = '00_NacionalyEntidadesFederativas'
    anio = [1895,1900,1910,1921,1930,1940,1950,1960,1970,1980,1981,1982,1983,
      1984,1985,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997,
      1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010]

    with open('%s_tsv/%s_Valor.tsv' % (path, path)) as inegi_tsv:
      for l, line in enumerate(csv.reader(inegi_tsv, dialect="excel-tab")):

        # entidad
        self.sql.execute("SELECT * FROM entidad WHERE id=%s",(line[0],))
        if not self.sql.fetchone():
          self.sql.execute("INSERT INTO entidad (id,nombre) VALUES (%s,%s);",
            (line[0],line[1].decode("latin1")))

        # municipio
        self.sql.execute("SELECT * FROM municipio WHERE entidad=%s\
          AND id=%s", (line[0],line[2]))
        if not self.sql.fetchone():
          self.sql.execute("INSERT INTO municipio (entidad,id,nombre) \
            VALUES (%s,%s,%s);", (line[0],line[2],line[3].decode("latin1")))

        # indicador
        self.sql.execute("SELECT * FROM indicador WHERE id=%s", 
          (int(line[7]),))
        if not self.sql.fetchone():
          self.sql.execute("INSERT INTO indicador (id,descripcion) VALUES \
            (%s,%s);", (int(line[7]),line[8].decode("latin1")))

        # valor
        for i, a in enumerate(line[9:]):
          if a:
            self.sql.execute("INSERT INTO valor \
              (indicador,municipio,entidad,anio,valor) VALUES (%s,%s,%s,%s,%s);", 
              (int(line[7]),line[2],line[0],anio[i],float(a)))

        # categoria
        self.sql.execute("SELECT * FROM categoria WHERE nombre=%s", 
          (int(line[7]),))
        if not self.sql.fetchone():
          self.sql.execute("INSERT INTO indicador (id,descripcion) VALUES \
            (%s,%s);", (int(line[7]),line[8].decode("latin1")))

    # with open('%s_tsv/%s_Notas.tsv' % (path, path)) as inegi_tsv:
    #   for l, line in enumerate(csv.reader(inegi_tsv, dialect="excel-tab")):
    #     if l == 0:
    #       continue
    #     # TODO: hay lineas que empiezan sin ID, son linebreaks de la anterior.
    #     # ademas hay algunos IDs repetidos que su desc debe ser concatenada
    #     if line[0].isdigit():
    #       self.sql.execute("SELECT * FROM indicador WHERE id=%s",(int(line[0]),))
    #       previous = self.sql.fetchone()
    #       if not previous:
    #         self.sql.execute("INSERT INTO notas (indicador,notas) VALUES (%s,%s);",
    #           (int(line[0]),line[2]))

def main():
  args = sys.argv[1:]
  # usage = 'usage: parse.py {--print | --dbwrite} [directories...]'
  # if len(args) < 2:
  #   print usage
  #   sys.exit(1)

  # printd = False
  # dbwrite = False
  # if args[0] == '--print':
  #   printd = True
  #   del args[0]
  # elif args[0] == '--dbwrite':
  #   dbwrite = True
  #   del args[0]
  # else:
  #   print usage
  #   sys.exit(1)

  print '* Parser INEGI *'
  p = INEGIParser()
  # for directory in args:
    
  #   if printd:
  #     print p.entradas
  #   elif dbwrite:
  #     p.dbwrite()

if __name__ == '__main__':
  main()