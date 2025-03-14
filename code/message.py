"""websocket 协议消息封装"""

import ujson as json
import ubinascii as binascii


class ProtoVersion(object):
    V1 = 0b0001


class MessageType(object):
    FULL_CLIENT_REQUEST = 0b0001
    AUDIO_ONLY_REQUEST = 0b0010
    FULL_SERVER_RESPONSE = 0b1001
    AUDIO_ONLY_SERVER_RESPONSE = 0b1011
    ERROR_RESPONSE = 0b1111


class MessageTypeSpecificFlags(object):
    NONE = 0b0000
    AUDIO_ONLY_REQUEST_LAST_PACKAGE = 0b0010


class MessageSerializationMethod(object):
    NONE = 0b0000
    JSON = 0b0001


class MessageCompression(object):
    NONE = 0b0000
    GZIP = 0b0001


class Message(object):

    def __init__(self, proto_version, header_size, message_type, message_type_specific_flags, 
                    message_serialization_method, message_compression, payload=b""):
        """generate protocol header

        Args:
            proto_version (int): 0b0001 - version 1 (目前只有该版本)
            header_size (int): 0b0001 - header size = 4 (1 x 4)
            message_type (int): 0b0001 - 端上发送包含请求参数的 full client request
                                0b0010 - 端上发送包含音频数据的 audio only request
                                0b1001 - 服务端下发包含识别结果的 full server response
                                0b1111 - 服务端处理错误时下发的消息类型（如无效的消息格式，不支持的序列化方法等）
            message_type_specific_flags (int):   0b0000 - full client request 或包含非最后一包音频数据的 audio only request 中设置
                                                b0010 - 包含最后一包音频数据的 audio only request 中设置
            message_serialization_method (int): 0b0000 - 无序列化
                                                0b0001 - JSON 格式
            message_compression (int):   0b0000 - no compression
                                            0b0001 - Gzip 压缩
        """
        self.proto_version = proto_version
        self.header_size = header_size
        self.message_type = message_type
        self.message_type_specific_flags = message_type_specific_flags
        self.message_serialization_method = message_serialization_method
        self.message_compression = message_compression
        self.payload = payload
    
    def __str__(self):
        s = "proto_version: 0b{:04b}\n" \
            "header_size: 0b{:04b}\n" \
            "message_type: 0b{:04b}\n" \
            "message_type_specific_flags: 0b{:04b}\n" \
            "message_serialization_method: 0b{:04b}\n" \
            "message_compression: 0b{:04b}\n".format(
                self.proto_version,
                self.header_size,
                self.message_type,
                self.message_type_specific_flags,
                self.message_serialization_method,
                self.message_compression
            )
        return s
    
    def to_bytes(self):
        header_bytes = bytes(
            [
                (self.proto_version << 4) | self.header_size,
                (self.message_type << 4) | self.message_type_specific_flags,
                (self.message_serialization_method << 4) | self.message_compression,
                0x00
            ]
        )
        return header_bytes + self.payload

    @classmethod
    def from_bytes(cls, raw):
        return cls(
            proto_version=raw[0] >> 4,
            header_size=raw[0] & 0x0F,
            message_type=raw[1] >> 4,
            message_type_specific_flags=raw[1] & 0x0F,
            message_serialization_method=raw[2] >> 4,
            message_compression=raw[2] & 0x0F,
            payload=raw[(raw[0] & 0x0F) * 4:]
        )

    def to_hex(self):
        return binascii.hexlify(self.to_bytes()).decode()
    
    @classmethod
    def from_hex(cls, string):
        return cls.from_bytes(binascii.unhexlify(string))


def MessageWrapper(msg):

    if msg.message_type == MessageType.FULL_SERVER_RESPONSE:
        msg.payload_size = int.from_bytes(msg.payload[:4], "big")
        msg.payload = json.loads(msg.payload[4:])
    elif msg.message_type == MessageType.ERROR_RESPONSE:
        msg.err_code = int.from_bytes(msg.payload[:4], "big")
        msg.err_msg_size = int.from_bytes(msg.payload[4:8], "big")
        msg.message = json.loads(msg.payload[8:])
    elif msg.message_type == MessageType.AUDIO_ONLY_SERVER_RESPONSE:
        msg.sequence_number = int.from_bytes(msg.payload[:4], "big")
        msg.payload_size = int.from_bytes(msg.payload[4:8], "big")
        msg.payload = msg.payload[8:]
    else:
        raise ValueError("unknow message type: 0b{:04b}".format(msg.message_type))
    return msg
