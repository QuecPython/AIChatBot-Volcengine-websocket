"""CLASS TiktokWS"""
from usr.asr_lib import ASRWebSocket , ASRConfig
from usr.tts_lib import TTSWebSocket , TTSConfig
from usr.ark_lib import ChatCompletions , ARKConfig
import utime
from usr.media import media , Mediaconfig
from usr.threading import Queue, Thread
import _thread

class TiktokWS(object):
    def __init__(self):
        #self.asr_ws_client = ASRWebSocket()
        #self.tts_ws_client = TTSWebSocket()
        self.media = media()
        self.chat_resp_queue = Queue()
        self.asr_resp = None

    def config(self, *args, **kwargs):
        config = {
            'Chat': (ARKConfig, {
                'CompletionsPosrURL': 'CHAT_COMPLETIONS_POST_URL',
                'ModelId': 'MODEL_ID',
                'AppKey': 'API_KEY'
            }),
            'ASR': (ASRConfig, {
                'AppId': 'ASR_APP_ID',
                'AuthToken': 'ASR_AUTH_TOKEN',
                'Host': 'ASR_HOST',
                'Cluster': 'ASR_CLUSTER'
            }),
            'TTS': (TTSConfig, {
                'AppId': 'TTS_APP_ID',
                'AuthToken': 'TTS_AUTH_TOKEN',
                'Host': 'TTS_HOST',
                'Cluster': 'TTS_CLUSTER'
            }),
            'Media': (Mediaconfig, {
                'volume': 'AUDIO_VOLUME'
            })
    }
    
        param_mapping = {}
        for group_info in config.values():
            config_class, params = group_info
            for param_name, attr_name in params.items():
                param_mapping[param_name] = (config_class, attr_name)

    # 查询模式：单个位置参数，无关键字参数
        if len(args) == 1 and not kwargs:
            input_key = args[0]
        
        # 子模式1a：查询整个组的参数
            if input_key in config:
                config_class, params = config[input_key]
                return {
                    param: getattr(config_class, attr)
                    for param, attr in params.items()
                }
        
        # 子模式1b：查询单个参数
            elif input_key in param_mapping:
                config_class, attr_name = param_mapping[input_key]
                return getattr(config_class, attr_name)
            
            # 无效输入
            else:
                raise ValueError("Invalid group or parameter name")

    # 模式2：更新操作（关键字参数）
        elif not args and kwargs:
            try:
                for key, value in kwargs.items():
                    # 子模式2a：更新整个组的参数
                    if key in config:
                        config_class, params = config[key]
                        if not isinstance(value, dict):
                            raise False
                        for param, val in value.items():
                            if param not in params:
                                raise False
                            attr_name = params[param]
                            setattr(config_class, attr_name, val)

                    # 子模式2b：更新单个参数
                    elif key in param_mapping:
                        config_class, attr_name = param_mapping[key]
                        setattr(config_class, attr_name, value)
                    # 无效输入
                    else:
                        raise False
                return True
            except:
                raise ValueError("Invalid parameter name or value")
    # 错误处理
    # -----------------------------------------------------------------
        else:
            if args:
                if len(args) > 1:
                    raise ValueError("Query mode supports only one positional argument.")
                else:
                    raise ValueError("Cannot mix query (positional) and update (keyword) arguments.")
            else:
                raise ValueError("No parameters provided.")
    def start_media(self):
        self.media.start()
    
    def stop_media(self):
        self.media.stop()

    # ASR
    def asr(self):
        self.asr_ws_client = ASRWebSocket()
        self.tts_ws_client = TTSWebSocket()
        resp = self.asr_ws_client.full_client_request()
        if resp is None:
            raise ValueError("full client request failed")

        buffer = bytearray()
        while True:
            chunk = self.media.read()
            is_last = chunk is None
            if not is_last:
                if len(buffer) < 16 * 1024:
                    buffer += chunk
                    continue
                self.asr_ws_client.audio_only_request(buffer, is_last=is_last)
                buffer = b''
            else:
                resp = self.asr_ws_client.audio_only_request(buffer, is_last=is_last)
                buffer = bytearray()
                if resp and resp.payload["code"] == 1000:
                    text = resp.payload["result"][0]["text"]
                    return text
                else:
                    raise ValueError("audio only request last packets failed")
    # TTS
    def tts_play(self, chat_resp):
        # print('tts_play: {}\n'.format(chat_resp))
        if chat_resp:
            for data in self.tts_ws_client.full_client_request(chat_resp):
                self.media.write(data)

    def chat(self, asr_resp):
        content = ""
        with ChatCompletions(asr_resp) as cc:
            for text in cc.answer:
                content += text
                if len(content) > 128:
                    # print('smart_chat: {}'.format(content))
                    self.tts_play(content)
                    content = ""
        if content:
            self.tts_play(content)
            
            

        
   