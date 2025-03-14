import modem
import ujson as json
from usr import uwebsocket as ws
from usr import uuid
from usr.logging import getLogger
from usr.message import *


logger = getLogger(__name__)


class TTSConfig(object):
    TTS_APP_ID = 'xx'
    TTS_HOST = 'wss://openspeech.bytedance.com/api/v1/tts/ws_binary'
    TTS_AUTH_TOKEN = 'xx'
    TTS_CLUSTER = 'xx'

class TTSConnectError(Exception):
    pass


class TTSQueryError(Exception):
    pass


class TTSError(Exception):
    pass


class TTSWebSocket(object):

    def __init__(self, host=TTSConfig.TTS_HOST, debug=False):
        self.debug = debug
        self.host = host

    def __enter__(self):
        self.open()
        return self
    
    def __exit__(self, *args, **kwargs):
        return self.close()

    @property
    def client(self):
        __client__ = getattr(self, "__client__", None)
        if __client__ is not None:
            return __client__
        
        try:
            __client__ = ws.Client.connect(
                self.host, 
                headers={"Authorization": "Bearer; {}".format(TTSConfig.TTS_AUTH_TOKEN)}, 
                debug=self.debug
            )
        except Exception as e:
            raise TTSConnectError("ASR websocket connect failed, pls checkout your network! Exception details: {}, {}".format(type(e).__name__, str(e)))
        else:
            setattr(self, "__client__", __client__)
            return __client__

    def send(self, data):
        """send data to server"""
        return self.client.send(data)

    def recv(self):
        """receive data from server, return None or "" means disconnection"""
        return self.client.recv()

    def open(self):
        return self.client

    def close(self):
        """close websocket"""
        self.client.close()
        del self.__client__

    def full_client_request(self, text):
        """发送 full client request"""
        request_json = {
                "app": {
                    "appid": TTSConfig.TTS_APP_ID,
                    "token": "access_token",
                    "cluster": TTSConfig.TTS_CLUSTER
                },
                "user": {
                    "uid": "{}".format(modem.getDevImei())
                },
                "audio": {
                    "voice_type": "BV001_streaming",
                    "encoding": "mp3",
                    "speed_ratio": 1.0,
                    "volume_ratio": 1.0,
                    "pitch_ratio": 1.0,
                },
                "request": {
                    "reqid": str(uuid.uuid4()),
                    "text": "",
                    "text_type": "plain",
                    "operation": "query",
                    "with_frontend": 0,
                    "frontend_type": "unitTson"
                }
        }
        request_json['request']['text'] = text
        payload = json.dumps(request_json)

        full_client_request_msg = Message(
            proto_version=ProtoVersion.V1,
            header_size=1,
            message_type=MessageType.FULL_CLIENT_REQUEST,
            message_type_specific_flags=MessageTypeSpecificFlags.NONE,
            message_serialization_method=MessageSerializationMethod.JSON,
            message_compression=MessageCompression.NONE,
            payload=len(payload).to_bytes(4, "big") + payload
        )
    
        # logger.debug("============ full_client_request_msg =============:\n{}".format(full_client_request_msg))
        # logger.debug("full_client_request_msg hex string: ", full_client_request_msg.to_hex())
        # logger.debug("payload: ", json.loads(full_client_request_msg.payload[4:]))

        try:
            self.send(full_client_request_msg.to_bytes())
        except Exception as e:
            raise TTSQueryError("send error: {}, {}".format(type(e).__name__, str(e)))

        res = self.recv()
        if not res:
            logger.error("recv None")
            return

        protocol_version = res[0] >> 4
        header_size = res[0] & 0x0f
        message_type = res[1] >> 4
        message_type_specific_flags = res[1] & 0x0f
        serialization_method = res[2] >> 4
        message_compression = res[2] & 0x0f
        reserved = res[3]
        header_extensions = res[4:header_size*4]

        if message_type == 0x0F:
            code = int.from_bytes(res[header_size * 4 : header_size * 4 + 4], "big")
            msg_size = int.from_bytes(res[header_size * 4 + 4 : header_size * 4 + 8], "big")
            error_msg = res[8:].decode()
            if code != 3011:
                logger.error("tts err msg, code: {}".format(code))
            return

        payload_size = int.from_bytes(res[header_size * 4 + 4: header_size * 4 + 8], "big")

        data_length = 0
        buffer_size = 64 * 1024
        for i in range(header_size * 4 + 8, header_size * 4 + 8 + payload_size, buffer_size):
            data = res[i:i+buffer_size]
            data_length += len(data)
            yield data

        while data_length < payload_size:
            data = self.recv()
            for i in range(0, len(data), buffer_size):
                data = res[i:i+buffer_size]
                data_length += len(data)
                yield data
