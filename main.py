import os
import openai
import traceback
from fofotu.fofotu_recorder import FofotuRecorder
from fofotu.fofotu_speaker import FofotuSpeaker
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
speech_key = os.getenv("AUZRE_TTS_KEY")
service_region = os.getenv("AUZRE_TTS_REGION")


recorder = FofotuRecorder()
speaker = FofotuSpeaker(speech_key=speech_key, service_region=service_region)

# messages = [{"role": "system", "content": '你是一个知识渊博，乐于助人的智能机器人,你的名字叫“火火兔”，你的任务是陪我聊天，请用简短的对话方式，用中文讲一段话，每次回答不超过50个字！'}]
messages = []


def run():
    global messages
    # robot_say("我的名字叫Nancy，你可以呼唤我Hey Nancy,我就会开始和你聊天")
    while True:
        while True:
            # 开始接收录音指令，超时或2s无人说话则退出
            # TODO：如果未结束指令前超时，则继续录，直到指令时间超过5s，停止录入
            result = recorder.record()
            print(result)
            # 录制到指令
            if result:
                audio_file = open(result, "rb")
                transcript = openai.Audio.transcribe("whisper-1", audio_file)
                audio_file.close()
                if transcript is None:
                    print("whisper未识别到指令")
                    # robot_say("抱歉，我没有听清楚你说")
                else:
                    # 如果超时30s无对话，则清空messages列表
                    print("whisper识别到指令:%s"%transcript["text"])
                    messages.append({"role": "system", "content": '你是一个知识渊博，乐于助人的智能机器人,你的名字叫“火火兔”，你的任务是陪我聊天，请用简短的对话方式，用中文讲一段话，每次回答不超过50个字！'})
                    messages.append({"role": "user", "content": transcript["text"]})
                    # while len(messages) > 5:
                    #     messages.pop()
                    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
                    messages.clear()
                    system_message = response["choices"][0]["message"]
                    # system_message['content']= "测试回答"
                    # speaker.speak("测试的答案")
                    speaker.speak(system_message['content'])


def FofotuRun():
    try:
        run()
    except Exception as e:
        print(traceback.format_exc())


if __name__ == "__main__":
    FofotuRun()