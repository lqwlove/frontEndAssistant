from fastapi import FastAPI,BackgroundTasks,WebSocket,WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from src.Agents import AgentClass
from src.Voice import Voice
import uvicorn
from openai import RateLimitError
import uuid
import asyncio
from src.AddDoc import AddDocClass
from src import ChatTTS
from fastapi.responses import StreamingResponse
import torch
import numpy as np
import torchaudio
from pydantic import BaseModel
import io
import zipfile
from src.tools.audio import pcm_arr_to_mp3_view
import argparse
import logging
import re
import requests
import json
from typing import Optional
# from dingtalk_stream import AckMessage
# import dingtalk_stream


app = FastAPI()
# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，您可以根据需要限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World!"}

@app.post("/chat")
def SyncChat(query: str,background_tasks: BackgroundTasks):
    # print("-------")
    # return "345"
    agent = AgentClass()
    msg = agent.run_agent(query)
    unique_id = str(uuid.uuid4()) 

    pattern = r"<!DOCTYPE html>.*?</html>"

    # 使用 re.search 查找匹配项
    # print('msgmsg', msg)
    match = re.search(pattern, msg['output'], re.DOTALL)

    if match:
        # print("Matched content:")
        code = match.group(0)
        htmlPath = './src/demo.html'
        # print(code)
        # 选择文件路径，打开文件并写入 HTML 内容
        with open(htmlPath, "w", encoding="utf-8") as file:
            file.write(code)
        # 创建一个 ZIP 文件并将 HTML 文件添加进去
        zip_file = "./src/demo.zip"
        with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(htmlPath, arcname="demo.html")  # arcname 用于指定在 ZIP 中存储的文件名

        # 打开文件并准备文件上传
        with open(zip_file, 'rb') as file:
           # 准备上传的字段和文件
            files = {
                'media': ('output.zip', file, 'application/zip')  # 'media' 为文件字段
            }
            data = {
                'type': 'file'  # 'type' 字段是普通字段，值为 'file'
            }

            # 发送 POST 请求上传文件
            upload_url = 'https://oapi.dingtalk.com/media/upload?access_token=b733dcddc71e3040869178cf55135ad3'
            response = requests.post(upload_url, files=files, data=data)
        if response.status_code == 200:
            result = response.json()
            print('resultresult:', result)
            media_id = result['media_id']
            print("File uploaded successfully!", media_id)
            send_url = "https://api.dingtalk.com/v1.0/robot/groupMessages/send"
            headers = {
                'x-acs-dingtalk-access-token': 'b733dcddc71e3040869178cf55135ad3'  # 添加 token 到请求头
            }
            send_data = {
                "msgParam": json.dumps({"mediaId": media_id, 'fileName': 'demo.zip', 'fileType': 'zip'}),
                "msgKey" : "sampleFile",
                "openConversationId" : "cidPLPP70a6SPs9h8b4dQ4OCA==",
                "robotCode" : "ding3tyleeqhu1apwaa9"
            }
            send_res = requests.post(send_url, json=send_data, headers=headers)
            if send_res.status_code == 200:
                print('发送成功')
            else:
                print("发送失败:", send_res.text)
        else:
            print(f"Failed to upload file. Status code: {response.status_code}")
            print("Response:", response.text)
        return {"msg": '已为您生成', "id": unique_id}

    else:
        return {"msg": msg, "id": unique_id}

    #voice
    # voice = Voice(uid=unique_id)
    # background_tasks.add_task(voice.get_voice,msg["output"])
    

@app.post("/initChatTTS")
def initChatTTS():
    global chat
    chat = ChatTTS.Chat()
    print("Initializing ChatTTS...")
    if chat.load(source='local', custom_path='/aiserver/src/asset/chattts'):
        print("Models loaded successfully.")
        return {"msg": True}
    else:
        print("Models load failed.")
        return {"msg": False}
    
class ChatTTSParams(BaseModel):
    text: list[str]
    stream: bool = False
    lang: Optional[str] = None
    skip_refine_text: bool = False
    refine_text_only: bool = False
    use_decoder: bool = True
    do_text_normalization: bool = True
    do_homophone_replacement: bool = False
    params_refine_text: ChatTTS.Chat.RefineTextParams
    params_infer_code: ChatTTS.Chat.InferCodeParams

def deterministic(seed=0):
    torch.manual_seed(seed)
    np.random.seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

@app.post("/getAvdio")
def generate_voice(params: ChatTTSParams):

     # audio seed
    # if params.params_infer_code.manual_seed is not None:
    #     deterministic(params.params_infer_code.manual_seed)
    #     params.params_infer_code.spk_emb = chat.sample_random_speaker()
    spk = torch.load('./src/asset/seed_181_restored_emb.pt', map_location="cpu")
    params.params_infer_code.spk_emb = spk
    # text seed for text refining
    if params.params_refine_text:
        text = chat.infer(
            text=params.text, skip_refine_text=False, refine_text_only=True
        )
        print(f"Refined text: {text}")
    else:
        # no text refining
        text = params.text

    wavs = chat.infer(
        text=text,
        stream=params.stream,
        lang=params.lang,
        skip_refine_text=params.skip_refine_text,
        use_decoder=params.use_decoder,
        do_text_normalization=params.do_text_normalization,
        do_homophone_replacement=params.do_homophone_replacement,
        params_infer_code=params.params_infer_code,
        params_refine_text=params.params_refine_text,
    )



    # print("Start voice inference.")
    # wavs = chat.infer(params.text)
    # print("Inference completed.")

    # finally_wavs = torch.tensor(np.concatenate(wavs, axis=-1))
    # file_path = "./output.wav"
    # print('123', finally_wavs)
    # torchaudio.save(file_path, finally_wavs, 24000)
    # audio_file = open(file_path, "rb")
    # return StreamingResponse(audio_file, media_type="audio/wav")


    # zip all of the audio files together
    buf = io.BytesIO()
    with zipfile.ZipFile(
        buf, "a", compression=zipfile.ZIP_DEFLATED, allowZip64=False
    ) as f:
        for idx, wav in enumerate(wavs):
            f.writestr(f"{idx}.mp3", pcm_arr_to_mp3_view(wav))
    print("Audio generation successful.")
    buf.seek(0)
    response = StreamingResponse(buf, media_type="application/octet-stream")
    response.headers["Content-Disposition"] = "attachment; filename=2.mp3"
    return response



# 心跳检测
async def send_heartbeat(websocket: WebSocket):
    while True:
        try:
            await websocket.send_text("Ping")
            await asyncio.sleep(2)  # 心跳间隔
        except Exception as e:
            print("心跳发送失败", e)
            break  # 连接断开

@app.post("/add_urls")
async def add_urls(urls: str):
    add_doc = AddDocClass()
    await add_doc.add_urls(urls)

@app.post("/add_md")
async def add_md(path: str):
    add_doc = AddDocClass()
    res = await add_doc.add_md_doc(path)
    return res

@app.post("/add_pdfs")
def add_pdfs(files: str):
    pass
@app.post("/add_txts")
def add_txts(files: str):
    pass
@app.post("/add_youtubes")
def add_youtubes(files: str):
    pass

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    connection_closed = False
    asyncio.ensure_future(send_heartbeat(websocket))
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            if data == "Pong":
                print("Pong")
            else:
                #处理消息
                try:
                    agent = AgentClass()
                    async for chunk in agent.run_agent_ws(data):
                        await websocket.send_text(chunk)
                #OpenAI 限流
                except RateLimitError:
                        await websocket.send_text("Rate Limit Error")
                        connection_closed = True
                        break
                except Exception as e:
                    print("An error occurred:", e)
                    connection_closed = True
                    break
                #在所有数据块发送完毕后发送一个结束标志
                if not connection_closed:
                    await websocket.send_text("##END##")
    except WebSocketDisconnect:
        print("WebSocket connection closed")
        connection_closed = True
    finally:
        if not connection_closed:
            await websocket.close()
        print("WebSocket connection closed")


def setup_logger():
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter('%(asctime)s %(name)-8s %(levelname)-8s %(message)s [%(filename)s:%(lineno)d]'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)