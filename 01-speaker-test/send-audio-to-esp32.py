import socket
import time
import wave

# 需要根据实际情况修改
SERVER_UDP_IP = "192.168.1.8"
SERVER_UDP_PORT = 8085
WAV_FILE_NAME = "sayhi.wav"


def send_audio_stream_with_udp(ip, port, src_file_path):
    PACKET_SIZE = 1024
    # 打开wav文件
    with wave.open(src_file_path, 'rb') as wav_file:
        # 获取参数
        params = wav_file.getparams()
        num_frames = params.nframes
        # 读取PCM数据
        pcm_data = wav_file.readframes(num_frames)
        # 创建 UDP Socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        file_size = 0
        # 分包发送
        data = pcm_data
        print("Prepare to sending audio stream")
        while data:
            file_size += len(data)
            sock.sendto(data[:PACKET_SIZE], (ip, port))
            data = data[PACKET_SIZE:]
            time.sleep(0.02)
        print(f"sending data {file_size} bytes")
        sock.close()
        print("Finish！")


if __name__ == '__main__':
    send_audio_stream_with_udp(SERVER_UDP_IP, SERVER_UDP_PORT, WAV_FILE_NAME)
