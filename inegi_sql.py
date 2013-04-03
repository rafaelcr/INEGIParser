#!/usr/bin/python

"""Parser INEGI

Recibe un TSV de informacion nacional y lo transmite hacia
una base de datos PostgreSQL.
http://www3.inegi.org.mx/sistemas/descarga/default.aspx?c=28088

Los nombres de archivos y directorios estan basados en la convencion de nombres
especificada por INEGI
"""

__author__ = "@rafaelcr (Rafael Cardenas)"

import csv
import psycopg2
import subprocess
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
      id varchar(3) PRIMARY KEY,\
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
      id serial,\
      nombre varchar PRIMARY KEY,\
      parent integer);")
    self.sql.execute("CREATE TABLE IF NOT EXISTS nota (\
      indicador bigint references indicador(id),\
      notas varchar);")

  def dbclose(self):
    self.sql.close()
    self.sqlconn.close()

  def parse(self):
    # path = "00_NacionalyEntidadesFederativas"
    path = "01_Aguascalientes"
    anio = [1895,1900,1910,1921,1930,1940,1950,1960,1970,1980,1981,1982,1983,
      1984,1985,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997,
      1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010]

    # determinar encoding de csv. algunos malamente no vienen en utf-8
    fenc = subprocess.Popen(["file","--mime-encoding",
      "datos/%s_tsv/%s_Valor.tsv" % (path, path)], stdout=subprocess.PIPE)
    self.encoding = fenc.stdout.read().split(':')[1].strip()

    print "Procesando CSV de valores..."
    with open("datos/%s_tsv/%s_Valor.tsv" % (path, path)) as inegi_tsv:
      for l, line in enumerate(csv.reader(inegi_tsv, dialect="excel-tab")):
        if l == 0 and (not line[0].isdigit()):
          continue
        self.wentidad(line[0],line[1])
        self.wmunicipio(line[0],line[2],line[3])
        self.windicador(line[7],line[8])
        self.wcategoria(line[4],"")
        self.wcategoria(line[5],line[4])
        self.wcategoria(line[6],line[5])
        for i, a in enumerate(line[9:]):
          if a:
            self.wvalor(int(line[7]),line[2],line[0],anio[i],float(a))

    print "Procesando CSV de notas..."
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

  def strdecode(self, s):
    if not self.encoding == "utf-8":
      return s.decode("latin1")
    else:
      return s

  def wvalor(self, indicador, municipio, entidad, anio, valor):
    self.sql.execute("INSERT INTO valor \
      (indicador,municipio,entidad,anio,valor) VALUES (%s,%s,%s,%s,%s);", 
      (indicador,municipio,entidad,anio,valor))

  def wentidad(self, eid, nombre):
    try:
      self.sql.execute("INSERT INTO entidad (id,nombre) VALUES (%s,%s);",
          (eid,self.strdecode(nombre)))
    except Exception, e:
      pass
        
  def wmunicipio(self, entidad, mid, nombre):
    try:
      self.sql.execute("INSERT INTO municipio (entidad,id,nombre) \
        VALUES (%s,%s,%s);", (entidad,mid,self.strdecode(nombre)))
    except Exception, e:
      pass

  def windicador(self, iid, descripcion):
    try:
      self.sql.execute("INSERT INTO indicador (id,descripcion) VALUES \
        (%s,%s);", (int(iid),self.strdecode(descripcion)))
    except Exception, e:
      pass

  def wcategoria(self, nombre, parent):
    if nombre:
      self.sql.execute("SELECT * FROM categoria WHERE nombre=%s", 
        (self.strdecode(nombre),))
      if not self.sql.fetchone():
        if parent:
          self.sql.execute("SELECT * FROM categoria WHERE nombre=%s", 
            (self.strdecode(parent),))
          parent = int(self.sql.fetchone()[0])
        else:
          parent = 0 
        self.sql.execute("INSERT INTO categoria (nombre,parent) VALUES \
          (%s,%s);", (self.strdecode(nombre),parent))

def main():
  args = sys.argv[1:]

  print '* Parser INEGI *'
  p = INEGIParser()

if __name__ == '__main__':
  main()