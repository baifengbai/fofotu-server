# ChatGPT火火兔改造示例代码（Server）


## 环境准备

示例在 python3.8.2 版本上测试通过

```
python -m venv .venv
python -m pip install --upgrade pip
pip install -r .\requirements.txt
```

## 示例运行

### 扬声器驱动测试
```
cd .\01-speaker-test\
python .\send-audio-to-esp32.py
```
测试方法：运行以上代码
测试结果：扬声器播放"01-speaker-test\sayhi.wav"

### MIC测试示例
```
cd .\02-mic-test\
python .\receive-audio-from-esp32.py
```
测试方法：

- 运行以上代码
- 按下开发板上BOOT按键或火火兔的Chat按键，MIC可录音5秒

测试结果：服务器完成录音并生成录音文件 "chatgpt-huohuotu-server\02-mic-test\record.wav"