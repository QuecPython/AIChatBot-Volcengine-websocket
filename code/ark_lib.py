import ujson as json
import request
from usr.logging import getLogger
from usr.logging import getLogger
logger = getLogger(__name__)



class ARKConfig(object):
    CHAT_COMPLETIONS_POST_URL = 'https://ark.cn-beijing.volces.com/api/v3/chat/completions'
    MODEL_ID = 'xx'
    API_KEY = 'xx'

class ChatCompletionsError(Exception):
    pass


class ChatCompletions(object):
    
    def __init__(self, question):
        if not (isinstance(question, str) and question):
            raise ChatCompletionsError("question must be str type and not blank.")
        self.question = question
        self.resp = None
    
    def __enter__(self):
        self.__post()
        return self

    def __exit__(self, *args, **kwargs):
        if self.resp:
            self.resp.close()

    def __post(self):
        resp = request.post(
            ARKConfig.CHAT_COMPLETIONS_POST_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(ARKConfig.API_KEY)
            },
            json={
                "model": ARKConfig.MODEL_ID,
                "messages": [
                    {"role": "user", "content": self.question},
                ],
                "stream": True
            }
        )

        if resp.status_code != 200:
            raise ChatCompletionsError("query_chat_completions exc: {}".format("".join((_ for _ in resp.text))))

        return resp

    @property
    def answer(self):
        self.resp = self.__post()
        raw = ""
        for temp in self.resp.text:
            raw += temp
            while True:
                data_index = raw.find("data: ")
                line_index = raw.find("\n\n")
                if data_index == -1 or line_index == -1:
                    break
                json_string = raw[data_index + 6 : line_index]
                if json_string == "[DONE]":
                    break
                data = json.loads(json_string)
                yield data["choices"][0]["delta"]["content"]
                raw = raw[line_index + 2:]


if __name__ == "__main__":
    with ChatCompletions("你好") as cc:
        for text in cc.answer:
            print(text, end="")
