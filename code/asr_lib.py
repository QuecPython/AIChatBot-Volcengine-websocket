import modem
import ujson as json
from usr import uwebsocket as ws
from usr import uuid
from usr.logging import getLogger
from usr.message import *


logger = getLogger(__name__)



class ASRConfig(object):
    ASR_APP_ID = 'xx'
    ASR_AUTH_TOKEN = 'xxx'
    ASR_HOST = 'wss://openspeech.bytedance.com/api/v2/asr'
    ASR_CLUSTER = 'xx'
  

class ASRConnectError(Exception):
    pass


class ASRQueryError(Exception):
    pass


class ASRWebSocket(object):

    def __init__(self, host=ASRConfig.ASR_HOST, debug=False):
        # self.ASR_APP_ID = ASR_APP_ID
        # self.ASR_AUTH_TOKEN = ASR_AUTH_TOKEN
        # self.ASR_HOST = ASR_HOST
        # self.ASR_CLUSTER = ASR_CLUSTER
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
                headers={"Authorization": "Bearer; {}".format(ASRConfig.ASR_AUTH_TOKEN)}, 
                debug=self.debug
            )
        except Exception as e:
            raise ASRConnectError("ASR websocket connect failed, pls checkout your network! Exception details: {}, {}".format(type(e).__name__, str(e)))
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

    def full_client_request(self):
        """发送 full client request"""
        payload = json.dumps(
            {
                "app": {
                    "appid": ASRConfig.ASR_APP_ID,
                    "token": ASRConfig.ASR_AUTH_TOKEN,
                    "cluster": ASRConfig.ASR_CLUSTER
                },
                "user": {
                    "uid": modem.getDevImei()
                },
                "audio": {
                    "format": "mp3",
                    "rate": 8000,
                    "bits": 16,
                    "channel": 1,
                    "language": "zh-CN"
                },
                "request": {
                    "reqid": str(uuid.uuid4()),
                    # "workflow": "audio_in,resample,partition,vad,fe,decode",
                    "sequence": 1,
                    "nbest": 1,
                    "show_utterances": False
                }
            }
        )

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
            raise ASRQueryError("send error: {}, {}".format(type(e).__name__, str(e)))
        
        try:
            resp_data = self.recv()
        except Exception as e:
            raise ASRQueryError("recv error: {}, {}".format(type(e).__name__, str(e)))
        else:
            resp = MessageWrapper(Message.from_bytes(resp_data.encode()))
            if resp and resp.message_type == MessageType.ERROR_RESPONSE:
                logger.error("err resp: {}".format(resp.payload))
                return None
            # logger.debug("resp: {}".format(resp.payload))
            return resp

    def audio_only_request(self, payload, is_last=False):
        """发送 audio only request"""
        audio_only_request_msg = Message(
            proto_version=ProtoVersion.V1,
            header_size=1,
            message_type=MessageType.AUDIO_ONLY_REQUEST,
            message_type_specific_flags=MessageTypeSpecificFlags.AUDIO_ONLY_REQUEST_LAST_PACKAGE if is_last else MessageTypeSpecificFlags.NONE,
            message_serialization_method=MessageSerializationMethod.NONE,
            message_compression=MessageCompression.NONE,
            payload=len(payload).to_bytes(4, "big") + payload
        )
        # logger.debug("============ audio_only_request_msg =============:\n{}".format(audio_only_request_msg))
        # logger.debug("audio_only_request hex string: ", audio_only_request_msg.to_hex())
        # logger.debug("payload: ", audio_only_request_msg.payload[4:])

        try:
            self.send(audio_only_request_msg.to_bytes())
        except Exception as e:
            raise ASRQueryError("audio_only_request error: {}, {}".format(type(e).__name__, str(e)))

        try:
            resp_data = self.recv()
        except Exception as e:
            raise ASRQueryError("audio_only_request recv error: {}, {}".format(type(e).__name__, str(e)))
        else:
            resp = MessageWrapper(Message.from_bytes(resp_data.encode()))
            if resp and resp.message_type == MessageType.ERROR_RESPONSE:
                raise ASRQueryError("audio_only_request err resp: {}".format(resp.payload))
            # logger.debug("audio_only_request resp: {}".format(resp.payload))
            return resp

    def query_asr(self, input_file_path="/usr/input.mp3", read_buffer_size=8192):

        resp = self.full_client_request()
        if resp is None:
            raise ASRQueryError("query_asr error resp.")

        with open(input_file_path, "rb") as f:
            total_size = f.seek(0, 2)
            f.seek(0, 0)

            chunk_nums = total_size // read_buffer_size
            if total_size % read_buffer_size != 0:
                chunk_nums += 1
            
            logger.debug("input file chunk nums: {}".format(chunk_nums))
            for _ in range(chunk_nums - 1):
                logger.debug("send {} chunk".format(_ + 1))
                chunk = f.read(read_buffer_size)
                resp = self.audio_only_request(chunk)
                if resp is None:
                    break
            else:
                logger.debug("send last chunk")
                chunk = f.read(read_buffer_size)
                resp = self.audio_only_request(chunk, is_last=True)
                if resp and resp.payload["code"] == 1000:
                    return resp.payload["result"][0]["text"]
