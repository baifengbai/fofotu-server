

import azure.cognitiveservices.speech as speechsdk
import socket
import time
import threading
import argparse
import wave

import socket
import time
import os

ip = "192.168.1.9" # 目标IP地址
port = 8085 # 目标端口号
PACKET_SIZE = 1024
voice = "zh-CN-XiaoshuangNeural"

class FofotuSpeaker:
    def __init__(self, speech_key, service_region):
        """performs speech synthesis and pull audio output from a stream"""
        # Creates an instance of a speech config with specified subscription key and service region.
        self.speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
        self.speech_config.speech_synthesis_voice_name = voice
        # Creates an audio output stream
        self.pull_stream = speechsdk.audio.PullAudioOutputStream()
        # Creates a speech synthesizer using pull stream as audio output.
        self.wav_file_name = "chatgptanswer.wav"
        self.file_config = speechsdk.audio.AudioOutputConfig(filename=self.wav_file_name)

    def speakwithpull(self, content_text):
        self.speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=self.stream_config)
        try:
            text = content_text
        except EOFError:
            pass
        result = self.speech_synthesizer.speak_text_async(text).get()
        # Check result
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesized for text [{}], and the audio was written to output stream.".format(text))
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))
        # Destroys result which is necessary for destroying speech synthesizer
        del result
        # Destroys the synthesizer in order to close the output stream.
        del self.speech_synthesizer
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Reads(pulls) data from the stream
            audio_buffer = bytes(PACKET_SIZE)
            total_size = 0
            filled_size = self.pull_stream.read(audio_buffer)
            while filled_size > 0:
                sock.sendto(audio_buffer, (ip, port))
                time.sleep(0.003)
                # print("{} bytes received.".format(filled_size))
                total_size += filled_size
                filled_size = self.pull_stream.read(audio_buffer)
            print("Totally {} bytes received.".format(total_size))
        finally:
            sock.close()


    def send_audio_stream_with_udp(self):
        PACKET_SIZE = 1024
        # 打开wav文件
        with wave.open(self.wav_file_name, 'rb') as wav_file:
            # 获取参数
            params = wav_file.getparams()
            num_frames = params.nframes
            # 读取PCM数据
            pcm_data = wav_file.readframes(num_frames)
            # 创建 UDP Socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            file_size = 0
            # 分包发送数据
            data = pcm_data
            print("Prepare to sending data")
            while data:
                file_size += len(data)
                sock.sendto(data[:PACKET_SIZE], (ip, port))
                data = data[PACKET_SIZE:]
                # 添加缓冲后可以控制发送速度
                time.sleep(0.02)

            print(f"sending data {file_size} bytes.%d")
            sock.close()
            print("Finish！")


    def speak(self, content_text):
        self.speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=self.file_config)
        try:
            text = content_text
        except EOFError:
            pass
        result = self.speech_synthesizer.speak_text_async(text).get()
        # Check result
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesized for text [{}], and the audio was saved to [{}]".format(text, self.wav_file_name))
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))
        # Destroys result which is necessary for destroying speech synthesizer
        del result
        # Destroys the synthesizer in order to close the output stream.
        del self.speech_synthesizer
        send_thread = threading.Thread(target=self.send_audio_stream_with_udp)
        # time.sleep(5)
        send_thread.start()


if __name__ == "__main__":
    speaker = FofotuSpeaker()
    speaker.speak("你好！有什么我可以帮助你的吗？你好！有什么我可以帮助你的吗？")