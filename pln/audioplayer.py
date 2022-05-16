import pafy
import vlc
import time
import threading
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# No hace falta generar una nueva
DEVELOPER_KEY = 'AIzaSyAQc7OKxUDZIX01RsA4gAU3r4WTPOphSkQ'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

# Encargado de reproducir audio
class AudioPlayer():
    def __init__(self) -> None:
        self.mutex = threading.Lock()
        self.t = None
        self.skip = False
        self.queuemutex = threading.Lock()
        self.queue = []
        self.playing = False
        self.playingmutex = threading.Lock()
        instance = vlc.Instance()
        self.player = instance.media_player_new()
        pass
    
    def __get_next_song(self):
        try:
            self.queuemutex.acquire()
            if len(self.queue) > 0:
                return self.queue.pop(0)
            return None
        finally:
            self.queuemutex.release()
    def addSource(self, source):
        try:
            self.queuemutex.acquire()
            self.queue.append(source)
            print("Added - ", source.title)
        finally:
            self.queuemutex.release()
    # Funcion encargada de la reproduccion del audio y de revisar si se ha acabado
    def __playloop(self):
        song = self.__get_next_song()
        print(song.title)
        while True:
            current_state = 6
            if song is not None:
                self.mutex.acquire()
                self.__new_player_media(self.player, song)
                self.player.play()
                self.mutex.release()
                current_state = 1
                self.playingmutex.acquire()
                self.playing = True
                self.playingmutex.release()
                while current_state != 6:
                    self.mutex.acquire()
                    if self.skip:
                        current_state = 6
                        self.skip = False
                        self.player.stop()
                    else:
                        current_state = self.player.get_state()
                    self.mutex.release()
                    time.sleep(5)
            else:
                self.playingmutex.acquire()
                self.playing = False
                self.playingmutex.release()
            song = self.__get_next_song()
            if song != None:
                print(song.title)
    
    def isPlaying(self):
        try:
            self.playingmutex.acquire()
            return self.playing
        finally:
            self.playingmutex.release()
    # Pausar la cancion actual
    def pause(self):
        self.mutex.acquire()
        self.playingmutex.acquire()
        self.playing = False
        self.player.pause()
        self.playingmutex.release()
        self.mutex.release()
    
    def next(self):
        self.mutex.acquire()
        self.skip = True
        self.mutex.release()
    # Parar el reproductor
    def stop(self):
        self.queuemutex.acquire()
        self.mutex.acquire()
        self.playingmutex.acquire()
        self.queue.clear()
        self.skip=True
        self.playing=False
        self.playingmutex.release()
        self.queuemutex.release()
        self.mutex.release()
    
    # Seguir reproduciendo cancion
    def resume(self):
        self.mutex.acquire()
        self.playingmutex.acquire()
        self.playing = True
        self.player.play()
        self.playingmutex.release()
        self.mutex.release()
    
    
    def __new_player_media(self, player, source):
        playurl = source.getbest().url
        instance = vlc.Instance()
        media = instance.media_new(playurl, ":no-video", ":nooverlay", ":role=music", ":network-caching=5000", ":disk-caching=5000",":file-caching=5000", ":live-caching=100")
        media.get_mrl()
        player.set_media(media)
        
    # Obtener Streaming y Crear, a partir de VLC, la reproducción.
    def play(self, source):
        self.addSource(source)
        if self.t is None:
            self.t = threading.Thread(name='audioplayer', target=self.__playloop)
            self.t.daemon = True
            self.t.start()
        
    # Para debuggear, esperar a que el loop de reproduccion acabe
    def wait(self):
        self.t.join()

    # Crea objeto con metadatos de video
    def pafy_video(self, video_id):
        url = 'https://www.youtube.com/watch?v={0}'.format(video_id)
        vid = pafy.new(url)
        return vid

    # Crear objeto con metadatos de playlist
    def pafy_playlist(self, playlist_id):
        url = "https://www.youtube.com/playlist?list={0}".format(playlist_id)
        playlist = pafy.get_playlist(url)
        return playlist


    def ytsearch(self, query, max_res=3):
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

        # Realizar consulta
        search_response = youtube.search().list(q=query, part='id,snippet', maxResults=max_res).execute()

        # Obtener resultados
        videos = []
        playlists = []
        for search_result in search_response.get('items', []):
            if search_result['id']['kind'] == 'youtube#video':
                videos.append('%s' % (search_result['id']['videoId']))
            elif search_result['id']['kind'] == 'youtube#playlist':
                playlists.append('%s' % (search_result['id']['playlistId']))

        if videos:
            print('Videos:{0}'.format(videos))
        elif playlists:
            print('Playlists:{0}'.format(playlists))
        
        return [self.pafy_video(x) for x in videos]

    # Buscar y reproducir en YT
    def youtube_search_play(self, query, max_res=3):
        res = self.ytsearch(query, max_res)
        # Si hay video, reproducirlo. Simular una pausa y esperar hasta el final.
        self.play(res[0])