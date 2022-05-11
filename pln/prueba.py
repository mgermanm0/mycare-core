from __future__ import print_function
from calendar import month

import datetime
from socket import timeout
from time import sleep 
from dateutil.relativedelta import relativedelta
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
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

from pln.gestorEventos import GestorEventos
from pln.gestorEventos import Evento

gestorEventos = GestorEventos()
audioplayer = AudioPlayer()

SCOPES = ['https://www.googleapis.com/auth/calendar']

MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
DIAS = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
DIAS31 = [ 1, 3, 5, 7, 8, 10, 12 ]
DIAS30 = [ 4, 6, 9, 11]
RULE2SPANISH = {'DAILY': 'diaria', 'WEEKLY': 'semanal', 'MONTHLY': 'mensual'}
SERVICE = ""

engine = pyttsx3.init()
listener = sr.Recognizer()
# normalize
# 
# Sirve para eliminar las tildes y pasar las mayusculas a minusculas. Para simplificar comparaciones entre strings
# param: [in] s String
# return: string normalizado
def normalize(s):
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
def talk(text):
    engine.say(text)
    engine.runAndWait()
    

# Take_Command
#
# Escucha si el usuario dice "alexa [comando]". Si es así, devuelve un string con el comando.
# return: string con el comando
def take_command():
    try:
        with sr.Microphone() as source:
            print("listening...")
            listener.adjust_for_ambient_noise(source, duration=0.5)
            voice = listener.listen(source, timeout=5)
            command = listener.recognize_google(voice, language="es-ES")
            command = command.lower()
            print("Audio recogido: ", command)           
    except Exception as e:
        command = ""
        print(str(e))
        talk("Lo siento, ha ocurrido un error. Prueba a repetir el comando.")
        pass
    
    return command


#Por si queremos meter alarmas. Está sin terminar.
def establecer_alarma(hora):
    now = datetime.datetime.now()
    hora_actual = now.hour
    
    hora_actuali = int(hora_actual)
    horai = int(hora[0])
    
    #       19                  8                                                  8               7
    if (hora_actuali > 12 and horai < 12 and hora_actuali < (horai+12)) or (hora_actuali < 12 and horai < 12 and hora_actuali > (horai+12)):
        horai = horai+ 12
        
    print('Alarma establecida a las '+str(horai)+' y '+hora[1])
    talk('Alarma establecida a las '+str(horai)+' y '+hora[1])


# Text_to_Int
#
# Se le pasa un número en texto, ej. "cuatro", y lo devuelve como entero (int) 4
# param [in] textnum string
# return int
def text2int(textnum, numwords={}):
    if not numwords:
      units = [
        "cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho",
        "nueve", "diez", "once", "doce", "trece", "catorce", "quince",
        "dieciseis", "siecisiete", "dieciocho", "diecinueve",
      ]

      tens = ["", "", "veinte", "treinta", "cuarenta", "cincuenta", "sesenta", "setenta", "ochenta", "noventa"]

      scales = ["cien", "mil", "millon", "billon", "trillon"]

      numwords["y"] = (1, 0)
      for idx, word in enumerate(units):    numwords[word] = (1, idx)
      for idx, word in enumerate(tens):     numwords[word] = (1, idx * 10)
      for idx, word in enumerate(scales):   numwords[word] = (10 ** (idx * 3 or 2), 0)

    current = result = 0
    for word in textnum.split():
        if word not in numwords:
          raise Exception("Illegal word: " + word)

        scale, increment = numwords[word]
        current = current * scale + increment
        if scale > 100:
            result += current
            current = 0

    return result + current    


# Get_Hora
#
# Se le pasa una hora, ej. "10:30 de la mañana", y extrae la hora "10:30"
def get_hora(text):
    array = text.split()
    hora = array[0]
    print(hora)
    if "tarde" in text or "noche" in text:
        array2 = hora.split(':')
        h = array2[0]
        hi = int(h)
        hi = hi + 12
        hora = str(hi)+":"+array2[1]
    
    print(hora)
    return hora


#Función principal que escucha al usuario y determina que orden ejecutar      
def run_alexa():
    comando = take_command()
    #talk(command)
    
    if 'reproduc' in comando:
        song =  comando.replace('reproduce','')
        talk('reproduciendo'+ song)
        print('reproduciendo'+ song)
        audioplayer.youtube_search_play(song)
        talk("Ha hecho la reprodusion")
    elif 'pausar' in comando:
        if audioplayer.isPlaying():
            audioplayer.pause()
    elif 'resumir' in comando:
        if not audioplayer.isPlaying():
            audioplayer.resume()
    elif 'parar' in comando:
        talk("Parando musica...")
        audioplayer.stop()
    elif 'siguiente' in comando:
        audioplayer.next()
    elif 'busca' in comando:
        search = comando.replace('busca', '')
        wikipedia.set_lang("es")
        wiki = wikipedia.summary(search, 1)
        #print(search + ": "+ wiki)
        talk(wiki)
        
    elif 'alarma' in comando:
        hora = comando.replace('alarma', '')
        hora = re.findall(r'\d+', hora)
        establecer_alarma(hora)  
        
    elif 'hora' in comando:
        time = datetime.datetime.now().strftime('%H:%M')
        print(time)
        talk('La hora es'+ time)   
    
    elif 'recordatorio' in comando:
        talk("¿Quieres crear un recordatorio?")
        confirmacion = take_command()
        confirmacion = normalize(confirmacion)
        print(str(confirmacion))
        if confirmacion == "si":
            crear_recordatorio_voz()        
            

            
# Crear_Recordatorio_Voz
#
# Funcion que va preguntando los parametros por voz al usuario. Y crea un evento en el calendar           
def crear_recordatorio_voz():
    talk("Vamos a ello. Dime un nombre para el recordatorio")
    nombre = take_command()
    print(str(nombre))
    talk("El nombre del recordatorio es "+nombre)
    
    talk("¿Quieres que se repita cada minuto, cada hora, diariamente, semanalmente o mensualmente?")
    freq = take_command()
    freq = normalize(freq)
    talk("La frecuencia de repetición es " + freq)
    print(str(freq))
    
    if "minutos" in freq:
        talk("Dime en cuantos minutos sonará el recordatorio")
        minutos = normalize(take_command())
        minutos_int = text2int(minutos)
        if(minutos_int is not None):
            now = datetime.datetime.now()
            dia_i = now + datetime.timedelta(minutes = minutos_int) #Sumamos los minutos, ya que se supone que el usuario diría 'En x minutos'
            hora = dia_i.time()
            talk(f'El recordatoio sonará cada {minutos_int} minutos. ¿Cuántas veces se repetirá el recordatorio?')
            count = take_command()
            count = normalize(count) 
            counti = text2int(count)
            
    elif "horas" in freq: # Revisar frecuencia horas
        talk("Dime en cuantas horas sonará el recordatorio")
        hora_str = normalize(take_command())
        hora = get_hora(hora_str)
        horaMinutos = hora.split(':')
        hora_int = text2int(horaMinutos[0])
        minutos_int = text2int(horaMinutos[1])
        if(hora is not None):
            now = datetime.datetime.now()
            dia_i = now + datetime.timedelta(hours = hora_int, minutes = minutos_int) #Sumamos las horas y los minutos, ya que se supone que el usuario diría 'En x horas e y minutos'
            hora = str(dia_i.time().hour + ':' + dia_i.time().minute)
            talk(f'El recordatoio sonará cada {minutos_int} horas. ¿Cuántas veces se repetirá el recordatorio?')
            count = take_command()
            count = normalize(count) 
            counti = text2int(count)
            
    elif "semanal" in freq or "mensual" in freq:
        talk("Dime el dia de inicio")                
        dia = take_command()
        talk( ("El dia de inicio es "+dia) )
        dia = normalize(dia)
        dia_i = get_fecha(dia)
        
        if "semanal" in freq:
            talk("¿Durante cuantas semanas quieres que se repita?")

        elif "mensual" in freq:
            talk("¿Durante cuantos meses quieres que se repita?")
        
        count = take_command()
        count = normalize(count)
        print(count)
        counti = text2int(count)
        print(str(counti))
        talk("¿A qué hora?")
        hora_str = take_command()
        hora_str = normalize(hora_str)           
        hora = get_hora(hora_str)
        
    elif "diaria" in freq:
        dia_i = datetime.datetime.now()
        talk("El recordatorio sonará diariamente. ¿A qué hora?")
        hora_str = take_command()
        hora_str = normalize(hora_str)           
        hora = get_hora(hora_str)
        talk("¿Durante cuantos dias?")
        count = take_command()
        count = normalize(count) 
        counti = text2int(count)
        print(str(counti))
    
    gestorEventos.defineEvento(nombre, freq, dia_i, hora, DIAS[dia_i.weekday()], count) #Agregamos el evento al gestorEventos mediante este método
    set_evento(SERVICE, nombre, dia_i, hora, freq, counti)
    talk(f'¡Perfecto! He creado el recordatorio {nombre} con frecuencia {freq} que se repetirá {count} veces.')
  
def auntetificacion_google():
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
  



def calendar2local(event):
    titulo = event['summary']
    calendar_id = event['id']
    
    #FECHA 
    start = event['start'].get('dateTime', event['start'].get('date')) #Dia y hora   
    hora_str =  str(start.split("T")[1].split("+")[0])
    
    #hora_i = int( hora_str.split(':')[0]) #09
    #minute_i = int( hora_str.split(':')[1]) #00
    anio_str = str(start.split("T")[0].split("-")[0])
    mes_str = str(start.split("T")[0].split("-")[1])
    dia_str = str(start.split("T")[0].split("-")[2])
    
    fechaInicial = datetime.datetime(month=int(mes_str), day=int(dia_str), year=int(anio_str))
    #fechaInicial = fechaInicial.replace(hour=hora_i, minute=minute_i)
    
    #HORA
    hora=hora_str
    
    #DIA SEMANA (que lo calcule por otro lao)
    dia_semana=DIAS[fechaInicial.weekday()]
    evento = Evento(titulo, "unica", fechaInicial, hora, dia_semana, count=1, id_calendar=calendar_id)
    return evento

# Dado un rango de días obtiene los eventos que haya a lo largo de ese periodo.
# Los que son recursivos solo muestra el primero con el atributo count>1
# NO se calcula el Evento.dia_semana 
#
# return list
def get_eventos(day, end_day, service, speech=True): 
    try: 
        # Call the Calendar API
        #now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        #print(f'Buscando {n} eventos...')
        date = datetime.datetime.combine(day, datetime.datetime.min.time())
        end_date = datetime.datetime.combine(end_day, datetime.datetime.max.time())
        
        utc = pytz.UTC
        date = date.astimezone(utc)
        end_date = end_date.astimezone(utc)
        
        events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(), timeMax=end_date.isoformat(),
                                                singleEvents=True, #maxResults=n,
                                                orderBy='startTime').execute()
        
        events = events_result.get('items', [])
        
        if not events:
            print('No se han encontrado eventos.')
            if speech:
                talk('No se han encontrado eventos.')
            return
        
        if speech:
            talk(f'Se han encontrado {len(events)} eventos.')
        
        arrayID = list() #Lista de ids de eventos
        mis_eventos = list() #Lista de eventos
        for event in events:
            calendar_id = event['id']
            if calendar_id not in arrayID:
                eventoACrear = None
                print(event['summary'])
                #FRECUENCIA
                if 'recurringEventId' in event:
                    recurringEvent = service.events().get(calendarId='primary', eventId=event['recurringEventId']).execute()
                    recurrence = recurringEvent.get("recurrence", [])[0]
                    frecuencia = RULE2SPANISH[recurrence.split(";")[0].split("=")[1]]
                    
                    eventoACrear = calendar2local(recurringEvent)
                    eventoACrear.recurrente = True
                    eventoACrear.frecuencia = frecuencia
                    
                    instances = service.events().instances(calendarId='primary', eventId=event['recurringEventId']).execute()
                    eventlist = instances.get("items", [])
                    arrayID.extend([evento['id'] for evento in eventlist])
                    last_event = calendar2local(eventlist[-1])
                    eventoACrear.until = last_event.fechaInicial
                else:
                    eventoACrear = calendar2local(event)

                arrayID.append(eventoACrear.id_calendar)
                mis_eventos.append(eventoACrear)
                
        return mis_eventos
    
    except Exception as e: 
        print('-- ERROR EN get_eventos() --')
        print(str(e))
    
# Se le pasan los parametros del evento y lo crea en el calendar
def set_evento(service, nombre, fecha, hora, freq, count):
    try:
        start = str(fecha.year)+'-'+str(fecha.month)+'-'+str(fecha.day)+'T'+hora+'+02:00'
        
        array_hora = hora.split(':')
        houri = int(array_hora[0])
        minutei=int(array_hora[1])
        mins = minutei + 5
        if mins >= 60:
            mins = 0
            houri = houri + 1
            if houri >= 24:
                houri = 0
                
        end = str(fecha.year)+'-'+str(fecha.month)+'-'+str(fecha.day)+'T'+str(houri)+':'+str(mins)+':00+02:00'
        
        if freq == 'diaria':
            freq='RRULE:FREQ=DAILY'
        elif freq == 'semanal':
            freq='RRULE:FREQ=WEEKLY'
        else:
            freq='RRULE:FREQ=MONTHLY'
            
        if count!=0:
            freq=freq+";COUNT="+str(count)
            
        event = {
            'summary': nombre,
            #'location': 'Miguel Romera, Jaen',
            #'description': 'Una descripcion',
            'start': {
                'dateTime': start,
                'timeZone': 'Europe/Madrid',
            },
            'end': {
                'dateTime': end,
                'timeZone': 'Europe/Madrid',
            },
            'recurrence': [
                freq
            ]
        }
        
        ''',
            'reminders': {
                'useDefault': False,
                'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
                ],
            },'''
        
        event = service.events().insert(calendarId="primary", body=event).execute()
        return event['etag']
    except Exception as e:
        print('-- ERROR EN set_evento() --')
        print(str(e))


#Dado un texto saca la fecha (datetime), ej: "que tengo planeado el 3 de julio" devueve 03/06
def get_fecha(text):
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
        dia = now.day + 1
        mes = now.month
        anio = now.year
        if (now.month in DIAS31 and dia > 31) or (now.month in DIAS30 and dia > 30) or (now.month == 2 and dia > 28):
            dia = 1
            mes = mes + 1
            if mes > 12:
                mes = 1
                anio = anio +1
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
        
    if dia < now.day and mes == -1  and dia != -1:
        mes = now.month + 1
    elif mes == -1 and dia == -1 and dia_semana !=-1:
        dia_semana_actual = now.weekday()
        dif = dia_semana - dia_semana_actual
        
        if dif < 0:
            dif = dif + 7
            
        return now + datetime.timedelta(dif)
    
    if mes == -1:
        mes = now.month
        
    print(f"{dia}/{mes}/{anio}")
    return datetime.datetime(month=mes, day=dia, year=anio)

def ejemploRecordatorioUnaSolaEjec():
    print("ILLOOOOO")
    return schedule.CancelJob
#--------------------- MAIN ---------------------
#engine.say('Hello, I am your Alexa')
#engine.say('What can I do for you')
#engine.runAndWait()


def syncCalendars(service):
    hoy = datetime.datetime.now()
    mes = datetime.datetime.now() + relativedelta(months=1)
    eventos_local=gestorEventos.getEventosDB()
    for evento in eventos_local:
        if evento.id_calendar is None:
            etag = set_evento(service, evento.titulo, evento.fechaInicial, evento.hora, evento.frecuencia, evento.count)
            gestorEventos.actualizaIDCalendar(evento.id, etag)
    eventos_calendar = get_eventos(hoy, mes, service, speech=False)
    for evento in eventos_calendar:
        if not gestorEventos.existeEventoConCalendar(evento.id_calendar):
            gestorEventos.defineEvento(evento.titulo, evento.frecuencia, evento.fechaInicial, evento.hora, evento.diaSemana, until_precalc=evento.until, id_calendar=evento.id_calendar)
    print("Actualizado.")
    
def mycare_pln_start():
    talk("Hola amigo")
    
    SERVICE = auntetificacion_google()
    #syncCalendars(SERVICE)
    #print(speed)
    engine.setProperty('rate', 150)
    
    text1="3 de mayo"
    text2="3 de junio"
    #array=get_eventos(get_fecha(text1), get_fecha(text2), SERVICE)
    #gestorEventos.defineEvento("pastillas2", "diaria", datetime.datetime.now(), "17:00:00", "lunes", count=2, id_calendar=None)
    i = False
    while True:
        run_alexa()

    
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
#alexa.run()
