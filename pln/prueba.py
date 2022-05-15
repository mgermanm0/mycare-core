from __future__ import print_function
from calendar import month
import threading
from pln.internetcheck import InternetCheck
import datetime
from pickletools import markobject
from socket import timeout
from time import sleep
from dateutil.relativedelta import relativedelta
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pyparsing import Regex
import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import wikipedia
from pygame import mixer
import re
import pytz
import schedule
from pln.audioplayer import AudioPlayer
import re
from pln.gestorEventos import GestorEventos
from pln.gestorEventos import Evento

SCOPES = ['https://www.googleapis.com/auth/calendar']

MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
         'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
DIAS = ['lunes', 'martes', 'miercoles',
        'jueves', 'viernes', 'sabado', 'domingo']
DIAS31 = [1, 3, 5, 7, 8, 10, 12]
DIAS30 = [4, 6, 9, 11]
RULE2SPANISH = {'DAILY': 'diaria', 'WEEKLY': 'semanal', 'MONTHLY': 'mensual'}

class AsistenteVoz():
    def __init__(self) -> None:
        self.asistentevision = None
    def __deferedinit(self):
        self.service = self.autentificacion_google()
        self.engine = pyttsx3.init()
        self.listener = sr.Recognizer()
        self.gestorEventos = GestorEventos(self.engine)
        self.audioplayer = AudioPlayer()
        check = InternetCheck(executeIfUp=self.mensajeSubida, executeIfDown=self.mensajeCaida)
        self.gestorEventos.addEjecucionScheduler(check.checkInternet)
        self.username = None
        self.lock = threading.Lock()
        
        voiceSel=None
        for voice in self.engine.getProperty('voices'):
            #print(voice.languages)
            if b'\x05es' in voice.languages:
                voiceSel=voice
        
        if voiceSel is not None:
            print("voice esp encontrada")
            self.engine.setProperty('voice', voiceSel.id)

    def getUsername(self):
        try:
            self.lock.acquire()
            return self.username
        finally:
            self.lock.release()
            
    def setUsername(self, username):
        try:
            self.lock.acquire()
            self.username = username
        finally:
            self.lock.release()        
    
    def autentificacion_google(self):
        try:
            creds = None
            if os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())

            service = build('calendar', 'v3', credentials=creds)
            return service
        except Exception as e:
            print('-- ERROR EN auntetificacion_google() --')
            print(str(e))


    


    # normalize
    #
    # Sirve para eliminar las tildes y pasar las mayusculas a minusculas. Para simplificar comparaciones entre strings
    # param: [in] s String
    # return: string normalizado
    def normalize(self, s):
        replacements = (
            ("á", "a"),
            ("é", "e"),
            ("í", "i"),
            ("ó", "o"),
            ("ú", "u"),
        )
        for a, b in replacements:
            s = s.replace(a, b).replace(a.upper(), b.upper())
        return s


    # Talk
    #
    # Reproduce por voz el texto que se le pasa
    # param: [in] trext String
    def talk(self, text):
        username = self.getUsername()
        if username is not None:
            if "¿" in text or "?" in text:
                self.engine.say(username + ", " + text)
            else:
                self.engine.say(text + ", " + username)
        else:
            self.engine.say(text)
        self.engine.runAndWait()


    # Take_Command
    #
    # Escucha si el usuario dice "alexa [comando]". Si es así, devuelve un string con el comando.
    # return: string con el comando
    def take_command(self):
        try:
            with sr.Microphone() as source:
                self.listener.adjust_for_ambient_noise(source, duration=0.5)
                print("listening...")
                voice = self.listener.record(source, duration=5)
                command = self.listener.recognize_google(voice, language="es-ES")
                command = command.lower()
                print("Audio recogido: ", command)
        except Exception as e:
            command = ""
            print(str(e))
            #talk("Lo siento, ha ocurrido un error. Prueba a repetir el comando.")
            pass

        return command


    # Por si queremos meter alarmas. Está sin terminar.
    def establecer_alarma(self, hora):
        self.gestorEventos.estableceAlarma(hora)
        print('Alarma establecida a las ' + hora)
        self.talk('Alarma establecida a las ' + hora)


    # Text_to_Int
    #
    # Se le pasa un número en texto, ej. "cuatro", y lo devuelve como entero (int) 4
    # param [in] textnum string
    # return int
    def text2int(self, textnum, numwords={}):
        try:
            if not numwords:
                units = [
                    "cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho",
                    "nueve", "diez", "once", "doce", "trece", "catorce", "quince",
                    "dieciseis", "siecisiete", "dieciocho", "diecinueve",
                ]

                tens = ["", "", "veinte", "treinta", "cuarenta",
                        "cincuenta", "sesenta", "setenta", "ochenta", "noventa"]

                scales = ["cien", "mil", "millon", "billon", "trillon"]

                numwords["y"] = (1, 0)
                for idx, word in enumerate(units):
                    numwords[word] = (1, idx)
                for idx, word in enumerate(tens):
                    numwords[word] = (1, idx * 10)
                for idx, word in enumerate(scales):
                    numwords[word] = (10 ** (idx * 3 or 2), 0)

            current = result = 0
            for word in textnum.split():
                if word not in numwords:
                    return None

                scale, increment = numwords[word]
                current = current * scale + increment
                if scale > 100:
                    result += current
                    current = 0

            return result + current
        except:
            print("Error obteniendo count")


    def unidades_horas(self, text):
        units = {
            "cero": "00", "una": "01", "dos": "02", "tres": "03", "cuatro": "04", "cinco": "05", "seis": "06", "siete": "07", "ocho": "08",
            "nueve": "09", "diez": "10", "once": "11", "doce": "12", "trece": "13", "catorce": "14", "quince": "15",
            "dieciseis": "16", "diecisiete": "17", "dieciocho": "18", "diecinueve": "19", "veinte": "20", "veintiuno": "21",
            "veinteidos": "22", "veintitres": "23", "veinticuatro": "00", "cinco": "05", "diez": "10", "quince": "15", "cuarto": "15", "veinte": "20",
            "veinticinco": "25", "media": "30", "treinta": "30", "menos veinticinco": "35", "menos veinte": "40", "menos cuarto": "45", "menos quince": "45",
            "menos diez": "50", "menos cinco": "55", "en punto": "00"}

        tokens = text.split(" ")
        for i, t in enumerate(tokens):
            if t in units:
                return units[t], i
        return None, -1
        
    def get_hora(self, text):

        #hora numerica en mensaje
        regex = re.compile("^([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$")
        match = [t for t in text.split(" ") if re.search(regex, t)]
        if len(match) > 0:
            hora, sec = match[0].split(":")
            if len(hora) < 2:
                hora = "0" + hora
            if len(sec) < 2:
                sec = sec + "0"
            return hora + ":" + sec
        
        if "a las " in text:
            text = text.replace("a las ", "")
        if "y" in text:
            text = text.replace("y", "")
        hora = None
        tokens = text.split(" ")
        hs, ihs = self.unidades_horas(text)
        if hs is not None:
            hora = hs
            ms, ims = self.unidades_horas(" ".join([ t for i, t in enumerate(tokens) if i != ihs]))
            if ms is not None:
                hora += ":" + ms
            else:
                hora += ":00"
        
        if hora is not None:
            print(hora)
            if "tarde" in text or "noche" in text:
                array2 = hora.split(':')
                h = array2[0]
                hi = int(h)
                hi = hi + 12
                hora = str(hi)+":"+array2[1]

            print(hora)
        return hora

    # Función principal que escucha al usuario y determina que orden ejecutar


    def run_alexa(self):
        self.gestorEventos.run_pending()
        comando = self.take_command()
        # talk(command)

        if 'reproduc' in comando:
            song = comando.replace('reproduce', '')
            
            print('reproduciendo' + song)
            self.audioplayer.youtube_search_play(song)
            self.talk('reproduciendo' + song)
        elif 'pausa' in comando:
            if self.audioplayer.isPlaying():
                self.audioplayer.pause()
        elif 'resumir' in comando:
            if not self.audioplayer.isPlaying():
                self.audioplayer.resume()
        elif 'para' in comando:
            self.talk("Parando musica...")
            self.audioplayer.stop()
        elif 'siguiente' in comando:
            self.audioplayer.next()
        elif 'busca' in comando:
            search = comando.replace('busca', '')
            wikipedia.set_lang("es")
            wiki = wikipedia.summary(search, 1)
            #print(search + ": "+ wiki)
            self.talk(wiki)

        elif 'alarma' in comando:
            hora = comando.replace('alarma', '')
            self.talk("¿A qué hora?")
            hora_str = self.take_command()
            hora_str = self.normalize(hora_str)
            hora = self.get_hora(hora_str)
            if hora is not None:
                self.establecer_alarma(hora)
            else:
                self.talk("Perdona, no te he entendido bien.")

        elif 'hora' in comando:
            time = datetime.datetime.now().strftime('%H:%M')
            print(time)
            self.talk('Son las ' + time)

        elif 'recordatorio' in comando:
            self.talk("¿Quieres crear un recordatorio?")
            confirmacion = self.take_command()
            confirmacion = self.normalize(confirmacion)
            print(str(confirmacion))
            if "si" in confirmacion:
                self.crear_recordatorio_voz()
        elif "mi nombre" in comando:
            name = self.getUsername()
            if name is not None:
                self.talk("Eres ")
            else:
                self.talk("Vaya, perdona, pero es que no te conozco. ¿Cómo te llamas?")
                nombre = self.take_command()
                nombre = self.normalize(nombre)
                self.talk("Ah si, me suenas " + nombre + ". Déjame que recuerde quien eres...")
                self.asistentevision.setEntreno(nombre)
        elif "ayuda" in comando:
            self.talk("Hola, soy el asistente virtual MyCare. Puedes pedirme que te recuerde algo diciendo pon un recordatorio o una frase similar y yo te guiaré por el proceso. También puedo reproducir videos de youtube y buscar en la wikipedia. O puedo también decirte la hora")


    # Crear_Recordatorio_Voz
    #
    # Funcion que va preguntando los parametros por voz al usuario. Y crea un evento en el calendar
    def crear_recordatorio_voz(self):
        counti = None
        dia_i = None
        say = ""
        self.talk("Vamos a ello. Dime un nombre para el recordatorio")
        nombre = self.take_command()
        print(str(nombre))
        self.talk("El nombre del recordatorio es "+nombre)

        self.talk("¿Quieres que se repita diariamente, semanalmente, mensualmente o una única vez?")
        freq = self.take_command()
        freq = self.normalize(freq)
        if "semanal" in freq:
            freq = "semanal"
            say = "cuantas semanas"

        elif "mensual" in freq:
            freq = "mensual"
            say = "cuantos meses"

        elif "dia" in freq:
            freq = "dias"
            say = " cuantos días "
            
        elif "unica" in freq:
            freq = "unica"
            say = "unica"
        else:
            self.talk("No entiendo esa frecuencia. Prueba a crear de nuevo el recordatorio")
            return
        self.talk("La frecuencia de repetición es " + freq)
        print(str(freq))

        self.talk("Dime el dia de inicio")
        dia = self.take_command()
        
        self.talk(("El dia de inicio es "+dia))
        dia = self.normalize(dia)
        dia_i = self.get_fecha(dia)
        if dia_i is None:
            self.talk("Perdona, no he entendido bien el dia de inicio.")
            return 
        counti = 1
        if not freq == "unica":
            self.talk(f'¿Durante {say} quieres que se repita?')
            count = self.take_command()
            count = self.normalize(count)
            print(count)
            counti = self.text2int(count)
            if counti is None:
                self.talk("Perdona, no he entendido bien el número de repeticiones.")
                return 
            print(str(counti))

        self.talk("¿A qué hora?")
        hora_str = self.take_command()
        hora_str = self.normalize(hora_str)
        hora = self.get_hora(hora_str)
        if(dia_i is not None and hora is not None):
            dia_i = dia_i.replace(microsecond=0)
            id_calendar = self.set_evento(nombre, dia_i, hora, freq, counti)
            self.gestorEventos.defineEvento(nombre, freq, dia_i, hora, DIAS[dia_i.weekday(
            )], count=counti, id_calendar=id_calendar)  # Agregamos el evento al gestorEventos mediante este método
            self.talk(
                f'¡Perfecto! He creado el recordatorio {nombre} que se repetirá {counti} veces.')
            self.talk(f'Te lo recordaré con frecuencia {freq}')
            return
        self.talk("Perdona, pero no te he entendido bien. Prueba a crear el recordatorio de nuevo")


    def calendar2local(self, event):
        titulo = event['summary']
        calendar_id = event['id']

        # FECHA
        start = event['start'].get(
            'dateTime', event['start'].get('date'))  # Dia y hora
        hora_str = str(start.split("T")[1].split("+")[0])

        # hora_i = int( hora_str.split(':')[0]) #09
        # minute_i = int( hora_str.split(':')[1]) #00
        anio_str = str(start.split("T")[0].split("-")[0])
        mes_str = str(start.split("T")[0].split("-")[1])
        dia_str = str(start.split("T")[0].split("-")[2])

        fechaInicial = datetime.datetime(
            month=int(mes_str), day=int(dia_str), year=int(anio_str))
        #fechaInicial = fechaInicial.replace(hour=hora_i, minute=minute_i)

        # HORA
        hora = hora_str

        # DIA SEMANA (que lo calcule por otro lao)
        dia_semana = DIAS[fechaInicial.weekday()]
        evento = Evento(titulo, "unica", fechaInicial, hora,
                        dia_semana, id_calendar=calendar_id)
        return evento

    # Dado un rango de días obtiene los eventos que haya a lo largo de ese periodo.
    # Los que son recursivos solo muestra el primero con el atributo count>1
    # NO se calcula el Evento.dia_semana
    #
    # return list


    def get_eventos(self, day, end_day, speech=True):
        try:
            # Call the Calendar API
            # now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
            #print(f'Buscando {n} eventos...')
            date = datetime.datetime.combine(day, datetime.datetime.min.time())
            end_date = datetime.datetime.combine(
                end_day, datetime.datetime.max.time())

            utc = pytz.UTC
            date = date.astimezone(utc)
            end_date = end_date.astimezone(utc)

            events_result = self.service.events().list(calendarId='primary', timeMin=date.isoformat(), timeMax=end_date.isoformat(),
                                                singleEvents=True,  # maxResults=n,
                                                orderBy='startTime').execute()

            events = events_result.get('items', [])

            if not events:
                print('No se han encontrado eventos.')
                if speech:
                    self.talk('No se han encontrado eventos.')
                return

            if speech:
                self.talk(f'Se han encontrado {len(events)} eventos.')

            arrayID = list()  # Lista de ids de eventos
            mis_eventos = list()  # Lista de eventos
            for event in events:
                calendar_id = event['id']
                if calendar_id not in arrayID:
                    eventoACrear = None
                    print(event['summary'])
                    # FRECUENCIA
                    if 'recurringEventId' in event:
                        recurringEvent = self.service.events().get(
                            calendarId='primary', eventId=event['recurringEventId']).execute()
                        recurrence = recurringEvent.get("recurrence", [])[0]
                        frecuencia = RULE2SPANISH[recurrence.split(";")[
                            0].split("=")[1]]

                        eventoACrear = self.calendar2local(recurringEvent)
                        eventoACrear.frecuencia = frecuencia

                        instances = self.service.events().instances(
                            calendarId='primary', eventId=event['recurringEventId']).execute()
                        eventlist = instances.get("items", [])
                        arrayID.extend([evento['id'] for evento in eventlist])
                        last_event = self.calendar2local(eventlist[-1])
                        eventoACrear.until = last_event.fechaInicial
                    else:
                        eventoACrear = self.calendar2local(event)

                    arrayID.append(eventoACrear.id_calendar)
                    mis_eventos.append(eventoACrear)

            return mis_eventos

        except Exception as e:
            print('-- ERROR EN get_eventos() --')
            print(str(e))

    # Se le pasan los parametros del evento y lo crea en el calendar


    def set_evento(self, nombre, fecha, hora, freq, count=0, until=None):
        try:
            start = str(fecha.year)+'-'+str(fecha.month) + \
                '-'+str(fecha.day)+'T'+hora+':00+02:00'

            array_hora = hora.split(':')
            houri = int(array_hora[0])
            minutei = int(array_hora[1])
            mins = minutei + 5
            if mins >= 60:
                mins = 0
                houri = houri + 1
                if houri >= 24:
                    houri = 0

            end = str(fecha.year)+'-'+str(fecha.month)+'-' + \
                str(fecha.day)+'T'+str(houri)+':'+str(mins)+':00+02:00'
            
            rrule_freq = None
            if not 'unica' in freq:
                if 'dia' in freq:
                    rrule_freq = 'RRULE:FREQ=DAILY'
                elif 'semana' in freq:
                    rrule_freq = 'RRULE:FREQ=WEEKLY'
                elif 'mensua' in freq:
                    rrule_freq = 'RRULE:FREQ=MONTHLY'

                if until is not None and rrule_freq is not None:
                    untilstr = until.strftime("%Y%m%dT%H%M%SZ")
                    rrule_freq += ';UNTIL=' + untilstr

                elif count != 0 and rrule_freq is not None:
                    rrule_freq += ";COUNT="+str(count)
            event=None
            if rrule_freq:
                event = {
                    'summary': nombre,
                    # 'location': 'Miguel Romera, Jaen',
                    # 'description': 'Una descripcion',
                    'start': {
                        'dateTime': start,
                        'timeZone': 'Europe/Madrid',
                    },
                    'end': {
                        'dateTime': end,
                        'timeZone': 'Europe/Madrid',
                    },
                    'recurrence': [
                        rrule_freq
                    ]
                }
            else:
                event = {
                    'summary': nombre,
                    # 'location': 'Miguel Romera, Jaen',
                    # 'description': 'Una descripcion',
                    'start': {
                        'dateTime': start,
                        'timeZone': 'Europe/Madrid',
                    },
                    'end': {
                        'dateTime': end,
                        'timeZone': 'Europe/Madrid',
                    }
                }  

            ''',
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                    ],
                },'''
            print(event)
            event = self.service.events().insert(calendarId="primary", body=event).execute()
            return event['id']
        except Exception as e:
            print('-- ERROR EN set_evento() --')
            print(str(e))


    # Dado un texto saca la fecha (datetime), ej: "que tengo planeado el 3 de julio" devueve 03/06
    def get_fecha(self, text):
        try:
            text = text.lower()
            now = datetime.datetime.now()

            if text.count("hoy") > 0:
                return now

            dia = -1
            dia_semana = -1
            mes = -1
            anio = now.year
            ndias = 0

            if 'mañana' in text:
                return now + datetime.timedelta(days=1)
            else:
                for word in text.split():
                    if word in MESES:
                        mes = MESES.index(word) + 1
                        if word in DIAS30:
                            ndias = 30
                        elif word in DIAS31:
                            ndias = 31
                        else:
                            ndias = 28
                    elif word in DIAS:
                        dia_semana = DIAS.index(word)
                    elif word.isdigit():
                        dia = int(word)

                if mes < now.month and mes != -1:
                    anio = anio + 1

                if dia < now.day and mes == -1 and dia != -1:
                    mes = now.month + 1
                elif mes == -1 and dia == -1 and dia_semana != -1:
                    dia_semana_actual = now.weekday()
                    dif = dia_semana - dia_semana_actual

                    if dif < 0:
                        dif = dif + 7

                    return now + datetime.timedelta(dif)

                if mes == -1:
                    mes = now.month

            print(f"{dia}/{mes}/{anio}")
            return datetime.datetime(month=mes, day=dia, year=anio)
        except:
            print("error obteniendo fecha")

    def syncCalendars(self):
        hoy = datetime.datetime.now()
        mes = datetime.datetime.now() + relativedelta(months=1)
        eventos_local = self.gestorEventos.getEventosDB()
        for evento in eventos_local:
            if evento.id_calendar is None:
                id = self.set_evento(evento.titulo, evento.fechaInicial,
                                evento.hora, evento.frecuencia, until=evento.until)
                self.gestorEventos.actualizaIDCalendar(evento.id, id)
        eventos_calendar = self.get_eventos(hoy, mes, speech=False)
        for evento in eventos_calendar:
            if not self.gestorEventos.existeEventoConCalendar(evento.id_calendar):
                self.gestorEventos.defineEvento(evento.titulo, evento.frecuencia, evento.fechaInicial, evento.hora,
                                        evento.diaSemana, until_precalc=evento.until, id_calendar=evento.id_calendar)
        print("Actualizado.")

    def mensajeSubida(self):
        self.talk("Vuelvo a tener conexión. Voy a revisar tu Google Calendar por si se han creado nuevos recordatorios...")
        self.syncCalendars()
        self.talk("¡Hecho!")
        
    def mensajeCaida(self):
        self.talk("No tengo conexión a internet. Podré recordarte los eventos de tu calendario, pero no podré hacer mucho mas.")
        
    def mycare_pln_start(self):
        self.__deferedinit()
        self.talk("Hola amigo")
        self.syncCalendars()
        # print(speed)
        self.engine.setProperty('rate', 150)
        #array=get_eventos(get_fecha(text1), get_fecha(text2), SERVICE)
        #gestorEventos.defineEvento("pastillas2", "diaria", datetime.datetime.now(), "17:00:00", "lunes", count=2, id_calendar=None)
        while True:
            self.run_alexa()


'''
#schedule.every().minute.do(ejemploRecordatorioUnaSolaEjec)
while True:
    if(len(schedule.get_jobs()) > 0):
        schedule.run_pending()
        time.sleep(1)
    else:
        print("No hay más recordatorios pendientes, saliendo...")
        break
now = datetime.datetime.now()
dia_i = now + datetime.timedelta(minutes = 10) #Sumamos los minutos, ya que se supone que el usuario diría 'En x minutos'
hora = now.time()
hora_i = dia_i.time()
print("Ahora: ", now, "hoy es ", now.weekday())
print("En 10 minutos: ", dia_i)

get_client()

fecha = datetime.datetime(2022, 4, 30)
fecha = fecha.replace(hour=10, minute=30)
set_evento(service,"Evento Mycare", fecha, "DAILY")
'''


#alexa = Asistente()
# alexa.run()
