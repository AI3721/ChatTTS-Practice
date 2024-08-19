import io
import av
import math
import wave
import av.option
import numpy as np
from numba import jit
from typing import Dict
from pathlib import Path
from av.audio.resampler import AudioResampler

video_format_dict: Dict[str, str] = {
    "m4a": "mp4",
}

audio_format_dict: Dict[str, str] = {
    "ogg": "libvorbis",
    "mp4": "aac",
}

def wav2(i: io.BytesIO, o: io.BufferedWriter, format: str):
    inp = av.open(i, "r")
    format = video_format_dict.get(format, format)
    out = av.open(o, "w", format=format)
    format = audio_format_dict.get(format, format)
    ostream = out.add_stream(format)
    for frame in inp.decode(audio=0):
        for p in ostream.encode(frame):
            out.mux(p)
    for p in ostream.encode(None):
        out.mux(p)
    out.close()
    inp.close()

def pcm_arr_to_mp3_view(wav: np.ndarray):
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(float_to_int16(wav))
    buf.seek(0, 0)
    buf2 = io.BytesIO()
    wav2(buf, buf2, "mp3")
    buf.seek(0, 0)
    return buf2.getbuffer()

@jit
def float_to_int16(audio: np.ndarray) -> np.ndarray:
    am = int(math.ceil(float(np.abs(audio).max())) * 32768)
    am = 32767 * 32768 // am
    return np.multiply(audio, am).astype(np.int16)

def load_audio(file: str, sr: int) -> np.ndarray:
    # if not Path(file).exists():
        # raise FileNotFoundError(f"File not found: {file}")
    try:
        # container = av.open(file)
        container = av.open(io.BytesIO(file.read()))
        resampler = AudioResampler(format="fltp", layout="mono", rate=sr)
        estimated_total_samples = int(container.duration * sr // 1_000_000)
        decoded_audio = np.zeros(estimated_total_samples + 1, dtype=np.float32)
        offset = 0
        for frame in container.decode(audio=0):
            frame.pts = None
            resampled_frames = resampler.resample(frame)
            for resampled_frame in resampled_frames:
                frame_data = resampled_frame.to_ndarray()[0]
                end_index = offset + len(frame_data)
                if end_index > decoded_audio.shape[0]:
                    decoded_audio = np.resize(decoded_audio, end_index + 1)
                decoded_audio[offset:end_index] = frame_data
                offset += len(frame_data)
        decoded_audio = decoded_audio[:offset]
    except Exception as e:
        raise RuntimeError(f"Failed to load audio: {e}")

    return decoded_audio
