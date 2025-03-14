import audio
from usr.threading import Queue, Thread

# 音频配置
# AUDIO_VOLUME = 8  # 音量 0~11
AUDIO_CHANNEL = 0
RECORD_FORMAT = audio.Record.MP3
RECORD_SAMPLE_RATE = 8000

class Mediaconfig(object):
    AUDIO_VOLUME = 8

class media(object):
    def __init__(self):
        self.audio_q = Queue(max_size=5)
        self.record_q = Queue()

        play_thread = Thread(self.__play_stream)
        play_thread.start()

        self.record_obj = audio.Record(AUDIO_CHANNEL)
        self.record_obj.end_callback(self.__record_cb)
        self.record_status = 0

        self.audio_obj = audio.Audio(AUDIO_CHANNEL)
        self.audio_obj.setVolume(Mediaconfig.AUDIO_VOLUME)

    def start(self):
        self.record_q.clear()
        self.record_obj.stream_start(RECORD_FORMAT, RECORD_SAMPLE_RATE, 0)
        self.record_status = 1

    def stop(self):
        self.record_obj.stream_stop()
        self.record_status = 0
        
    def read(self):
        if self.record_status == 0:
            return None
        return self.record_q.get()
    
    def write(self, data):
        return self.audio_q.put(data)

    def __play_stream(self):
        while True:
            data = self.audio_q.get()
            self.audio_obj.playStream(3, data)

    def __record_cb(self, para):
        if(para[0] == "stream"):
            if(para[2] == 1):
                if para[1] > 0:
                    read_buf = bytearray(para[1])
                    self.record_obj.stream_read(read_buf, para[1])
                    self.record_q.put(read_buf)
            elif (para[2] == 3):
                self.record_q.put(None)
            else:
                pass

