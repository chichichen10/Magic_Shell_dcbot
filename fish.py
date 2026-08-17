import httpx
from logger import logger

log = logger()


def tts(
    text: str,
    filename: str,
    api_key: str,
    reference_id: str = None,
    format: str = "mp3",
    mp3_bitrate: int = 128,
    latency: str = "normal",
):
    """
    調用 Fish Audio TTS API，將文本轉換為語音並儲存為音檔。

    參數:
    - text (str): 要轉換的文本
    - filename (str): 儲存的音檔名稱（包含副檔名，如 "output.mp3"）
    - api_key (str): Fish Audio API 金鑰
    - reference_id (str, 選填): 參考 ID，例如 "7f92f8afb8ec43bf81429cc1c9199cb1"
    - format (str, 選填): 音訊格式，預設 "mp3"，可選 "wav", "pcm", "mp3", "opus"
    - mp3_bitrate (int, 選填): MP3 比特率，預設 128，可選 64, 128, 192
    - latency (str, 選填): 延遲模式，預設 "normal"，可選 "normal" 或 "balanced"
    """
    request_data = {
        "text": text,
        "reference_id": reference_id,
        "chunk_length": 200,
        "normalize": True,
        "format": format,
        "mp3_bitrate": mp3_bitrate,
        "latency": latency,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    with httpx.Client() as client, open(filename, "wb") as f:
        response = client.post(
            "https://api.fish.audio/v1/tts",
            headers=headers,
            json=request_data,
            timeout=None,
        )

        if response.status_code == 200:
            f.write(response.content)
            log.info(f"TTS 生成完成，已儲存至 {filename}")
        else:
            log.warn(f"請求失敗: {response.status_code}, 錯誤訊息: {response.text}")
