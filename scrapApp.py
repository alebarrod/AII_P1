from tkinter import *
from bs4 import BeautifulSoup
import sqlite3
import urllib.request
import re

#Descarga de una a varias páginas html y realiza scrap sobre ellas.
def scrap():
    #Lista que contendra los objetos para la base de dato almacenados durante el scraping
    lista = list()

    #Iteración por cada página del foro que queramos descargar
    for i in range(1,4):
        urllib.request.urlretrieve(f'https://foros.derecho.com/foro/20-Derecho-Civil-General/page{i}',f'{i}.html')
        html_doc = open(f'{i}.html','r')
        soup = BeautifulSoup(html_doc, 'html5lib')

        #Examinar cada contenedor de cada página
        for element in soup.find_all("li", class_="threadbit"):

            #Titulo y link
            elem = element.find('a', class_='title')
            titulo = elem['title']
            enlace = f'https://foros.derecho.com/{elem["href"]}'
            
            #Autor
            elem = element.find('a', class_='username understate')
            autor = elem.string

            #Fechahora
            elem = element.find('span', class_='label')
            elem = re.findall("..\/..\/....\s..\:..", str(elem))    #extraer con expresion regular la fecha y hora
            fechahora = elem[0]

            #Visitas
            elem = element.find('ul', class_='threadstats td alt')  #Contenedor que contiene las visitas y respuestas
            elem1 = re.findall("Visitas:\s[0-9,]{1,}", str(elem))[0]    #Buscamos las visitas
            elem1 = re.findall("[0-9,]+", str(elem1))[0]    #Nos quedamos con los numeros (y las comas porque marcan millares)
            elem1 = elem1.replace(",", "")  #Eliminamos las comas
            visitas = int(elem1)

            #Respuestas (similar a visitas)
            elem1 = re.findall(">[0-9,]{1,}<",str(elem))
            elem1 = re.findall("[0-9,]{1,}",str(elem1))[0]
            elem1 = elem1.replace(",", "")
            respuestas = int(elem1)

            #Crear objeto post
            post = objectDB(titulo, enlace, autor, fechahora, respuestas, visitas)
            lista.append(post)
        
    return lista


class DB:

    #Crea la base de datos y la tabla que vamos a usar  
    def __init__(self, name = "database.db"):
            self.name = name
            connection = sqlite3.connect(self.name)
            connection.execute('''DROP TABLE IF EXISTS POST;''')
            connection.execute('''CREATE TABLE POST
                  (ID INTEGER PRIMARY KEY  AUTOINCREMENT NOT NULL,
                  TITULO           TEXT    NOT NULL,
                  ENLACE           TEXT,
                  AUTOR            TEXT,
                  FECHAHORA        TEXT,
                  RESPUESTAS        INT,
                  VISITAS           INT);''')
            connection.close()

    #Insert con todos los parametros
    def insert(self, titulo, enlace, autor, fechahora, respuestas, visitas):
            connection = sqlite3.connect(self.name)

            template = """INSERT INTO POST (TITULO, ENLACE, AUTOR, FECHAHORA, RESPUESTAS, VISITAS) VALUES ("{titulo}","{enlace}","{autor}","{fechahora}",{respuestas},{visitas});"""
            formatted_string = template.format(titulo = titulo, enlace = enlace, autor = autor, fechahora = fechahora, respuestas = respuestas, visitas = visitas)
            connection.execute(formatted_string);
            connection.commit()
            connection.close()

    #Select todos los objetos. Devuelve una lista con todos los objetos
    def select(self):
            lista = list()
            connection = sqlite3.connect(self.name)
            res = connection.execute("""SELECT * FROM POST;""")
            for obj in res:
                  lista.append(objectDB(obj[1],obj[2],obj[3],obj[4],obj[5],obj[6]))
            connection.close()
            return lista

    #Recibe una cadena para realizar una busqueda y devuelve una lista con objetos que coincidan con el titulo
    def selectTemas(self, busqueda):
            lista = list()
            connection = sqlite3.connect(self.name)

            template = """SELECT * FROM POST WHERE TITULO LIKE '%{busqueda}%';"""
            formatted = template.format(busqueda = busqueda)
            res = connection.execute(formatted)

            for obj in res:
                  lista.append(objectDB(obj[1],obj[2],obj[3],obj[4],obj[5],obj[6]))

            connection.close()

            return lista
    
    #Recibe una cadena para realizar una busqueda y devuelve una lista con objetos que coincidan con el autor
    def selectAutores(self, busqueda):
            lista = list()
            connection = sqlite3.connect(self.name)

            template = """SELECT * FROM POST WHERE AUTOR LIKE '%{busqueda}%';"""
            formatted = template.format(busqueda = busqueda)
            res = connection.execute(formatted)

            for obj in res:
                  lista.append(objectDB(obj[1],obj[2],obj[3],obj[4],obj[5],obj[6]))

            connection.close()

            return lista

    #Devuelve una lista con objetos ordenados por numero de respuestas
    def selectTemasActivos(self):
            lista = list()
            connection = sqlite3.connect(self.name)
            res = connection.execute("""SELECT * FROM POST ORDER BY RESPUESTAS DESC;""")
            for obj in res:
                  lista.append(objectDB(obj[1],obj[2],obj[3],obj[4],obj[5],obj[6]))
            connection.close()
            return lista

    #Devuelve una lista con objetos ordenados por numero de visitas
    def selectTemasPopulares(self):
            lista = list()
            connection = sqlite3.connect(self.name)
            res = connection.execute("""SELECT * FROM POST ORDER BY VISITAS DESC;""")
            for obj in res:
                  lista.append(objectDB(obj[1],obj[2],obj[3],obj[4],obj[5],obj[6]))
            connection.close()
            return lista
    


class App:
    def __init__(self):
        #Creacion de base de datos
        self.dbconnection = DB("practica1.db")

        #Creación de aplicación de escritorio
        self.app = Tk()

        #Creación del menú
        self.menu = Menu(self.app)

        #Desplegable de Datos
        self.datomenu = Menu(self.menu, tearoff = 0)
        self.datomenu.add_command(label = "Cargar", command = self.cargar)
        self.datomenu.add_command(label = "Mostrar", command = self.mostrar)
        self.datomenu.add_separator()
        self.datomenu.add_command(label = "Salir", command = self.app.destroy)

        self.menu.add_cascade(label = "Datos", menu = self.datomenu)

        #Desplegable de Buscar
        self.buscamenu = Menu(self.menu, tearoff = 0)
        self.buscamenu.add_command(label = "Tema", command = self.tema)
        self.buscamenu.add_command(label = "Autor", command = self.autor)

        self.menu.add_cascade(label = "Buscar", menu = self.buscamenu)

        #Desplegable de Estadísticas
        self.estadisticamenu = Menu(self.menu, tearoff = 0)
        self.estadisticamenu.add_command(label = "Temas más populares", command = self.mostrarTemasPopulares)
        self.estadisticamenu.add_command(label = "Temas más activos", command = self.mostrarTemasActivos)

        self.menu.add_cascade(label = "Estadísticas", menu = self.estadisticamenu)

        #Lanzamiento del menu
        self.app.config(menu = self.menu)
        self.app.mainloop()

    #Realiza el scrap y guarda los datos en la base de datos
    def cargar(self):
        lista = scrap()
        for element in lista:
            self.dbconnection.insert(element.titulo,element.enlace,
                element.autor,element.fechahora,element.respuestas,element.visitas)

    #Muestra todos los resultados en un objeto text
    def mostrar(self):
        text = Text(self.app)
        lista = self.dbconnection.select()

        for obj in lista:
            text.insert(INSERT, str(obj.toString()))
            text.insert(INSERT, "\n")
        text.insert(END, "\n")
        text.grid(row=0)
        self.app.mainloop()

    #Crea ventana para introducir una palabra para buscar un tema
    def tema(self):
        #Create new window
        self.temaWindow = Tk()

        #Create label
        self.tituloLabel = Label(self.temaWindow, text="Introduzca el título: ")
        self.tituloLabel.pack(side = LEFT)

        #Create input entry
        self.tituloEntry = Entry(self.temaWindow)
        self.tituloEntry.pack(side = BOTTOM)

        #Create button asociated to getTema
        b = Button(self.temaWindow, text = "Buscar", command = lambda: self.getTema(self.tituloEntry.get()))
        b.pack(side = RIGHT)

        #Run loop
        self.temaWindow.mainloop()

    #Recibe una cadena para realizar una busqueda y muestra los resultados de coincidencias en el titulo
    def getTema(self, entrada):
        #Create new window
        self.getTemaWindow = Tk()

        #Añadimos un scrollbar vertical
        scrollbar = Scrollbar(self.getTemaWindow)
        scrollbar.pack(side=RIGHT, fill=Y)

        #Create list box
        ListboxTema = Listbox(self.getTemaWindow, width = 200, height = 40, yscrollcommand = scrollbar.set)

        #Extraemos los temas relacionados con la cadena recibida y formateamos los resultados
        lista = self.dbconnection.selectTemas(entrada)
        i = 1
        for element in lista:
            ListboxTema.insert(i, f'{element.titulo}    Por: {element.autor} ({element.fechahora})')
            i = i + 1

        ListboxTema.pack()

        self.getTemaWindow.mainloop()

    #Crea ventana para introducir una palabra para buscar un autor
    def autor(self):
        #Create new window
        self.autorWindow = Tk()

        #Create label
        self.autorLabel = Label(self.autorWindow, text="Introduzca el autor: ")
        self.autorLabel.pack(side = LEFT)

        #Create input entry
        self.autorEntry = Entry(self.autorWindow)
        self.autorEntry.pack(side = BOTTOM)

        #Create button asociated to getTema
        b = Button(self.autorWindow, text = "Buscar", command = lambda: self.getAutor(self.autorEntry.get()))
        b.pack(side = RIGHT)

        #Run loop
        self.autorWindow.mainloop()

    #Recibe una cadena para realizar una busqueda y muestra los resultados de coincidencias en el autor
    def getAutor(self, entrada):
        #Create new window
        self.getAutorWindow = Tk()

        #Añadimos un scrollbar vertical
        scrollbar = Scrollbar(self.getAutorWindow)
        scrollbar.pack(side=RIGHT, fill=Y)

        #Create list box
        ListboxTema = Listbox(self.getAutorWindow, width = 200, height = 40, yscrollcommand = scrollbar.set)

        #Extraemos los temas relacionados con la cadena recibida y formateamos los resultados
        lista = self.dbconnection.selectAutores(entrada)
        i = 1
        for element in lista:
            ListboxTema.insert(i, f'{element.titulo}    Por: {element.autor} ({element.fechahora})')
            i = i + 1

        ListboxTema.pack()

        self.getAutorWindow.mainloop()

    #Crea un objeto text en la ventana principal y muestra todos los artículos ordenados por número de respuestas
    def mostrarTemasActivos(self):
        text = Text(self.app)
        lista = self.dbconnection.selectTemasActivos()

        for obj in lista:
            text.insert(INSERT, str(obj.toString()))
            text.insert(INSERT, "\n")
        text.insert(END, "\n")
        text.grid(row=0)
        self.app.mainloop()

    #Crea un objeto text en la ventana principal y muestra todos los artículos ordenados por número de visitas
    def mostrarTemasPopulares(self):
        text = Text(self.app)
        lista = self.dbconnection.selectTemasPopulares()

        for obj in lista:
            text.insert(INSERT, str(obj.toString()))
            text.insert(INSERT, "\n")
        text.insert(END, "\n")
        text.grid(row=0)
        self.app.mainloop()
        

    
class objectDB:
    def __init__(self, titulo, enlace, autor, fechahora, respuestas, visitas):
        self.titulo = titulo
        self.enlace = enlace
        self.autor = autor
        self.fechahora = fechahora.strip()
        self.respuestas = respuestas
        self.visitas = visitas        


    def toString(self):
        return f'''Título: {self.titulo} ({self.enlace}).
Creado por: {self.autor} en {self.fechahora}.
Visitas: {self.visitas}\nRespuestas: {self.respuestas}\n'''


def main():
    App()

main()