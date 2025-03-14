from machine import ExtInt
from usr.tiktokws import TiktokWS  # 豆包websocket
from usr.threading import Queue, Thread

KEY1_GPIO_NUM = 46
tiktok = None
tts_queue = None

def start_chat_flow():
    global tts_queue
    global tiktok
    try:
        # ASR
        tiktok.start_media()
        asr_resp = tiktok.asr()
        print('asr_resp: {}\n'.format(asr_resp))
        # LLM + TTS
        tiktok.chat(asr_resp)
    except Exception as e:
        print("{}(\"{}\")".format(type(e).__name__, str(e)))
        
    

def key1_cb(args):
    global tiktok
    
    gpio_num, level = args
    if level:
        print('please speak to ai.')
        Thread(target=start_chat_flow).start(stack_size=128)
    else:
        tiktok.stop_media()
        print('speak over and wait ai response.')

if __name__ == "__main__":
    tiktok = TiktokWS()
    tts_queue = Queue()
    key1 = ExtInt(getattr(ExtInt, "GPIO{}".format(KEY1_GPIO_NUM)), ExtInt.IRQ_RISING_FALLING, ExtInt.PULL_PU, key1_cb)
    key1.enable()
    
    print("ai start success...\nplease press kEY S2 to start")
