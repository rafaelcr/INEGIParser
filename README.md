INEGI Parser
============

Script de Python que toma los archivos TSV de INEGI para todas las Entidades
Federativas de México, los parsea a JSON y los transmite hacia una base de datos
MongoDB.  
Los archivos son tomados de la sección de 
[Descarga Masiva](http://www3.inegi.org.mx/sistemas/descarga/default.aspx?c=28088) 
de la INEGI por un shell script que los descarga y descomprime 
automáticamente.  

Dependencias
------------
* Python 2.7.2
* [MongoDB 2.4.1](http://www.mongodb.org/downloads)
* [pymongo 2.5](http://api.mongodb.org/python/current/)

Ejemplo de uso
------------

    ./parse.py --dbwrite datos/*

Con estas opciones, el script procesa todas las subcarpetas con la notación de
nombre XX\_EEEEEE\_tsv, en donde XX es la clave del estado de 2 dígitos y EEEEEE
es el nombre del estado bajo los 
[estandares de nombramiento del INEGI](http://www3.inegi.org.mx/sistemas/descarga/descargaArchivo.aspx?file=Por+entidad+federativa%2fDescripcion_archivos_txt.txt). 
El repositorio incluye los datos de Nuevo León para pruebas.

Base de Datos
------------

Cada uno de los documentos JSON escritos hacia la BD consiste
en datos de un *indicador* en cierto municipio del país a lo largo del tiempo.
Los [indicadores de la INEGI](http://www3.inegi.org.mx/sistemas/descarga/descargaArchivo.aspx?file=Por+entidad+federativa%2fTabla_de_contenidos_pdf.pdf) 
cubren estadísticas de población, salud, infraestructura, comunicación, agricultura,
etc. Ya que los datos se encuentran en MongoDB, se pueden hacer consultas muy
poderosas con mucha facilidad.  

### Ejemplos

Encontrar el estado que haya beneficiado a la mayor cantidad de familias con el
seguro popular en el 2006 (R: Quintana Roo):  

    db.entidades.find({
      "Id_Indicador": "1004000045", 
      "2006.valor":{$ne:null}, 
      "Cve_Municipio":"000"
      }).sort({"2006.valor": 1}).limit(1).pretty()

    {
      "_id" : ObjectId("5158b884b2a757fb570da0fe"),
      "Desc_Municipio" : "Total estatal",
      "Indicador" : "Familias beneficiadas por el seguro popular",
      "Cve_Entidad" : "23",
      "Id_Indicador" : "1004000045",
      "Tema_nivel_3" : "Derechohabiencia y uso de servicios de salud",
      "Tema_nivel_2" : "Salud",
      "Tema_nivel_1" : "Sociedad y Gobierno",
      "2006" : {
        "fuente" : "Instituto de Salud del Gobierno del Estado.",
        "valor" : 33564
      },
      "2007" : {
        "fuente" : "Instituto de Salud del Gobierno del Estado.",
        "valor" : 59460
      },
      "2005" : {
        "fuente" : "Instituto de Salud del Gobierno del Estado.",
        "valor" : 22034
      },
      "Desc_Entidad" : "Quintana Roo",
      "2008" : {
        "fuente" : "Instituto de Salud del Gobierno del Estado.",
        "valor" : 80837
      },
      "2009" : {
        "fuente" : "Instituto de Salud del Gobierno del Estado.",
        "valor" : 108683
      },
      "Cve_Municipio" : "000"
    }

Funcionalidad pendiente
------------
* Incluir datos de los TSVs de "Notas por valor del indicador"
* Corregir errores en TSVs que vienen con linebreaks extra que rompen el formato
* Por el momento la escritura a la BD hace solo "append", debe sobreescribir valores anteriores que empaten.