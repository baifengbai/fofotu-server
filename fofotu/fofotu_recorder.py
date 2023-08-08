import os
import wave
import struct
import socket
import time

class FofotuRecorder:
    """使用麦克风录制语音指令的类"""
    CHUNK = 1024
    CHANNELS = 1
    SAMPLEWIDTH = 2
    RATE = 16000
    RECORD_SECONDS = 5

    # 静默阈值 需要进行实际测试，根据麦的
    SILENCE_THRESHOLD = 0.001
    # 连续静默时长，指令录制过程中若静默连续超过此时长，则停止录制
    # 开始录制时此值应该与最大采集时间相同
    MAX_SILENCE_CONTINUE_SECONDS = 3
    # 指令时间长度
    MAX_CMD_SUM_SECONDS = 10
    # 最大连续采集时间，单位秒
    max_duration = 10
    # 最大接收数据大小，单位字节
    max_data_size = 1400
    # 最大的帧数
    max_frames = 200
    # 最少的指令帧数
    MIN_CMD_FRAMES_COUNTER = 4
    # 默认保存文件名称
    wavefilename = "record.wav"

    def __init__(self):
        pass

    def record(self):
        # 音频流帧数
        frames = []
        # 没有指令的帧数
        continue_silent_frames_counter = 0
        # 指令帧数
        cmd_frames_counter = 0
        # 文件名称（目前采用默认）
        # wavefilename = f"recording-{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.wav"
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind(('0.0.0.0', 8085))
            # 清空文件
            with open(self.wavefilename, 'wb') as f:
                pass
            print("Start recording")
            start_time = time.time()
            self.sock.settimeout(2)
            data_len = 0
            print("开始录制语音指令...")
            while (time.time() - start_time < self.max_duration):
                try:
                    data, addr = self.sock.recvfrom(self.max_data_size)
                    # 判断当前声音是否为静默，连续静默超过2s则结束当前录音
                    rms = self.__root_mean_square(data)
                    print("检测到声音 rms:%f" % rms)
                    if rms < self.SILENCE_THRESHOLD:
                        continue_silent_frames_counter += 1
                    else:
                        # print("检测到指令 rms:%f" % rms)
                        frames.append(data)
                        # 计算数据长度
                        data_len += len(data)
                        # 指令帧+1
                        cmd_frames_counter += 1
                        # 持续静默帧数归0
                        continue_silent_frames_counter = 0

                    # 如果持续静默时间超过指定值（2s），结束本次录制，重新开始侦听
                    if (continue_silent_frames_counter / self.RATE)*1000 >= self.MAX_SILENCE_CONTINUE_SECONDS:
                        print("连续静默时长超过:%.2fs" % ((continue_silent_frames_counter / self.RATE)*1000))
                        break
                    if (cmd_frames_counter / self.RATE*1000) >= self.MAX_CMD_SUM_SECONDS:
                        print("累计指令时长超过:%.2fs" % ((cmd_frames_counter / self.RATE)*1000))
                        break
                    # if len(frames) >= self.max_frames:
                    #     print(f"总帧数超过: {self.max_frames},停止录制!")
                    #     break
                except socket.timeout:
                    pass  # 接收超时，继续执行
            print(f"Received {data_len} bytes！")
            if cmd_frames_counter > 4:  # 如果保存了录音数据（有5条至少），就写入文件保存
                with wave.open(self.wavefilename, 'wb') as wf:
                    wf.setnchannels(self.CHANNELS)
                    wf.setsampwidth(self.SAMPLEWIDTH)
                    wf.setframerate(self.RATE)
                    wf.writeframes(b''.join(frames))
                    file_path = os.path.join(os.getcwd(), self.wavefilename)
                    # print(f"语音指令已保存到 {file_path}")
                return file_path
            else:  # 没有保存录音数据，就不写入文件
                print("Audio recording failed, no audio input detected.")
                return None
        finally:
            self.sock.close()


    def __root_mean_square(self, data):
        """计算RMS"""
        count = len(data) // 2
        format = f"<{count}h"
        shorts = struct.unpack(format, data)
        sum_squares = 0.0
        for sample in shorts:
            n = sample * (1.0 / 32768)
            sum_squares += n * n
        return (sum_squares / count) ** 0.5


if __name__ == "__main__":
    recorder = FofotuRecorder()
    print(recorder.record())
