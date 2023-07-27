import socket
import time
import pyaudio
import wave

# 需要根据实际情况修改
ESP32_UDP_PORT = 8085
WAV_FILE_NAME = "record.wav"
# 持续录音时间（单位s）
MAX_RECORD_DURATION = 5


def paly_wav(filename):
    wave_file = wave.open(filename, 'rb')
    sample_width = wave_file.getsampwidth()
    channels = wave_file.getnchannels()
    sample_rate = wave_file.getframerate()
    audio = pyaudio.PyAudio()
    stream = audio.open(format=audio.get_format_from_width(sample_width),
                        channels=channels,
                        rate=sample_rate,
                        output=True)
    data = wave_file.readframes(1024)
    while data:
        stream.write(data)
        data = wave_file.readframes(1024)
    stream.stop_stream()
    stream.close()
    wave_file.close()
    audio.terminate()


def recv_audio_stream_to_file_with_udp(filename):
    max_data_size = 1400  # 最大接收数据大小，单位字节
    max_frames = 200
    # 创建 UDP Socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind(('0.0.0.0', ESP32_UDP_PORT))
        # 清空文件
        with open(filename, 'wb') as f:
            pass
        print("Start recording")
        start_time = time.time()
        sock.settimeout(0.2)
        frames = []
        data_len = 0
        while (time.time() - start_time < MAX_RECORD_DURATION):
            try:
                data, addr = sock.recvfrom(max_data_size)
                frames.append(data)
                data_len += len(data)
                if len(frames) >= max_frames:
                    print(f"Reach the max_frames: {max_frames},stop recording!")
                    break
            except socket.timeout:
                pass  # 接收超时，继续执行
        print(f"Received {data_len} bytes")
        # 保存音频数据到文件
        with wave.open(filename, 'wb') as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(16000)
            f.writeframes(b''.join(frames))
    finally:
        sock.close()


if __name__ == '__main__':
    wav_file_name = WAV_FILE_NAME
    # 通过UDP获取音频流，并保存为wav格式文件
    recv_audio_stream_to_file_with_udp(wav_file_name)
    # 播放保存的音频文件
    paly_wav(wav_file_name)