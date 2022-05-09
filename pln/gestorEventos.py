from cgitb import reset
import schedule
import time
import sqlite3
import os
import datetime
dirname = os.path.dirname(__file__)
dbFile = 'myCareDB.db'
class Evento:
    #Titulo, es lo que el asistente de voz entonará al activarse el evento/recordatorio
    #Frecuencia es p.e minutos, semanal, diaria
    #Fecha (objeto datetime) tendrá toda la información del día, mes, año y hora
    def __init__(self, titulo, frecuencia, fechaInicial, hora, diaSemana, count, id=None, id_calendar=None):
        self.id = id
        self.id_calendar = id_calendar
        self.titulo = titulo
        self.frecuencia = frecuencia
        self.fechaInicial = fechaInicial
        self.hora = hora
        self.diaSemana = diaSemana
        self.count = count
    def eventoIteracion(self):
        self.count -= 1

class GestorEventos:
    def __init__(self):
        self.eventos = []
        self.conn = sqlite3.connect(dbFile, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        self.cur = self.conn.cursor()
        #Comprobamos que la tabla 'eventos' existe
        self.cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='eventos' ''')
        if self.cur.fetchone()[0]==0 :
            sqlite_create_table_query = '''CREATE TABLE eventos (
                id INTEGER PRIMARY KEY, 
                calendar_id TEXT UNIQUE,
                titulo TEXT, 
                frecuencia TEXT, 
                fechaInicial DATETIME, 
                hora TEXT, 
                diaSemana TEXT, 
                count INTEGER);'''
            self.cur.execute(sqlite_create_table_query)
            print('Tabla eventos creada')
        else:
            print('Tabla eventos ya existe')
        self.recuperaEventosDB()
    
        
    #Método utilizado para recuperar los eventos de la base de datos sqlite
    
    def recuperaEventosDB(self):
        eventosDB = self.getEventosDB()
        for evento in eventosDB:
            print("EVENTO CARGADO: ", evento.id, evento.titulo, evento.frecuencia)
            self.eventos.append(evento)
            self.addEventoScheduler(evento)
            
    def addEventoScheduler(self, evento):
        frecuencia = evento.frecuencia
        hora = evento.hora
        diaSemana = evento.diaSemana
        titulo = evento.titulo
        if frecuencia == "minutos":
            schedule.every().day.at(hora).do(self.ejecutaEvento,titulo) 
                
        elif frecuencia == "horas":
            schedule.every().day.at(hora).do(self.ejecutaEvento,titulo)
        elif frecuencia == "semanal":
            if diaSemana == "lunes":
                schedule.every().monday.at(hora).do(self.ejecutaEvento,titulo)
            elif diaSemana == "martes":
                schedule.every().tuesday.at(hora).do(self.ejecutaEvento,titulo)
            elif diaSemana == "miercoles":
                schedule.every().wednesday.at(hora).do(self.ejecutaEvento,titulo)
            elif diaSemana == "jueves":
                schedule.every().thursday.at(hora).do(self.ejecutaEvento,titulo)
            elif diaSemana == "viernes":
                schedule.every().friday.at(hora).do(self.ejecutaEvento,titulo)
            elif diaSemana == "sabado":
                schedule.every().saturday.at(hora).do(self.ejecutaEvento,titulo)
            elif diaSemana == "domingo":
                schedule.every().sunday.at(hora).do(self.ejecutaEvento,titulo)
        elif frecuencia == "diaria":
            schedule.every().day.at(hora).do(self.ejecutaEvento, titulo)

    def ejecutaEvento(self, args):
        print("RECORDATORIO: ", args)
        evento_index = self.buscaEvento(args)
        evento = self.eventos[evento_index]
        evento.count = evento.count - 1
        if(evento.count <= 0): #Si el contador está a 0 o menos es qu¡ no se desea que se repita más, borraremos el evento de la lista y de la BBDD
            delete_sqlite = '''DELETE FROM eventos WHERE id = ?'''
            self.cur.execute(delete_sqlite, (evento.id))
            self.conn.commit()
            self.eventos.remove(evento)
            return schedule.CancelJob #Se cancela la tarea en el Scheduler
        else: #Actualizaremos el contador en la BBDD
            update_sqlite = '''UPDATE eventos SET count = ? WHERE id = ? '''
            data_tuple = (evento.count, evento.id)
            self.cur.execute(update_sqlite, data_tuple)
            self.conn.commit()
        
    

    def defineEvento(self, titulo, frecuencia, fechaInicial, hora = "00:00", diaSemana = "", count = 1, id_calendar=None ):
        sqlite_insert = """INSERT INTO 'eventos' 
                        ('calendar_id', 'titulo', 'frecuencia', 'fechaInicial', 'hora', 'diaSemana', 'count')
                        VALUES (?,?,?,?,?,?,?);"""
        data_tuple = (id_calendar, titulo, frecuencia, fechaInicial, hora, diaSemana, count)
        self.cur.execute(sqlite_insert, data_tuple)
        self.conn.commit()
        auto_id = self.cur.lastrowid
        evento = Evento(id_calendar, titulo, frecuencia, fechaInicial, hora, diaSemana, count)
        print("id auto generado es: ", auto_id)
        self.eventos.append(evento)
        self.addEventoScheduler(evento)

    def actualizaIDCalendar(self, id, id_calendar):
        self.cur.execute('''UPDATE eventos SET calendar_id = ? WHERE id = ?''', (id_calendar, id))
        self.conn.commit()
    
    def existeEventoConCalendar(self, id_calendar):
        self.cur.execute('''SELECT * from eventos WHERE calendar_id = ?''', (id_calendar,))    
        return len(self.cur.fetchall()) > 0
    
    def buscaEvento(self, titulo):
        for evento in self.eventos:
            if(titulo == evento.titulo):
                return self.eventos.index(evento)

    def getEventosDB(self):
        sqlite_select_query = '''SELECT * from eventos'''
        self.cur.execute(sqlite_select_query)
        eventos = self.cur.fetchall()
        res = []
        for e in eventos:
            fechai = datetime.datetime.strptime(e[4], '%Y-%m-%d %H:%M:%S')
            res.append(Evento(e[2], e[3], fechai , e[5], e[6], count=e[7], id=e[0], id_calendar=e[1]))
        return res
"""
hoy = datetime.datetime.now()
ayer = datetime.datetime.now() - datetime.timedelta(days=1)
"""