from pathlib import Path
import os
import shutil
import subprocess
import tempfile

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.background import BackgroundTask

ROOT = Path(__file__).resolve().parent
app = FastAPI(title='Cadence Singer Lab')
MAX_UPLOAD = int(os.getenv('MAX_UPLOAD_BYTES', str(100 * 1024 * 1024)))

@app.get('/api/health')
def health():
    return {'ok': True, 'engine': 'configured' if os.getenv('SINGING_ENGINE_CMD') else 'guide fallback'}

async def save_upload(upload, destination):
    size = 0
    with destination.open('wb') as output:
        while chunk := await upload.read(1024 * 1024):
            size += len(chunk)
            if size > MAX_UPLOAD:
                raise HTTPException(413, 'Audio file exceeds upload limit')
            output.write(chunk)
    if not size:
        raise HTTPException(400, 'Empty audio file')

@app.post('/api/render')
async def render(guide: UploadFile = File(...), voice_ref: UploadFile | None = File(None),
                 lyrics: str = Form(''), mode: str = Form('performance'),
                 start_seconds: float = Form(0), first_sound_seconds: float = Form(0)):
    if mode != 'performance':
        raise HTTPException(501, 'Hum + Lyrics requires a singing synthesis backend.')
    if not (0 <= start_seconds <= 36000 and 0 <= first_sound_seconds <= 36000):
        raise HTTPException(400, 'Invalid timeline position')
    work = Path(tempfile.mkdtemp(prefix='cadence_singer_'))
    try:
        gp, vp, rendered, aligned = (work / name for name in ('guide.input', 'voice.input', 'rendered.wav', 'ai_vocal_aligned.wav'))
        await save_upload(guide, gp)
        if voice_ref:
            await save_upload(voice_ref, vp)
        engine = os.getenv('SINGING_ENGINE_CMD', '').strip()
        if engine:
            if not voice_ref:
                raise HTTPException(400, 'Reference voice required by configured engine')
            # A trusted deployment administrator configures this command, never a web user.
            subprocess.run(engine.format(guide=str(gp), voice=str(vp), out=str(rendered)),
                           shell=True, check=True, timeout=300, capture_output=True)
        else:
            subprocess.run(['ffmpeg', '-nostdin', '-y', '-i', str(gp), '-ar', '44100', '-ac', '1', str(rendered)],
                           check=True, timeout=120, capture_output=True)
        first_sample = round(first_sound_seconds * 44100)
        start_sample = round(start_seconds * 44100)
        filters = f'[0:a]atrim=start_sample={first_sample},asetpts=PTS-STARTPTS,adelay={start_sample}S[out]'
        subprocess.run(['ffmpeg', '-nostdin', '-y', '-i', str(rendered), '-filter_complex', filters,
                        '-map', '[out]', '-ar', '44100', '-ac', '1', '-c:a', 'pcm_s16le', str(aligned)],
                       check=True, timeout=120, capture_output=True)
        return FileResponse(aligned, media_type='audio/wav', filename='ai_vocal_aligned.wav',
                            background=BackgroundTask(shutil.rmtree, work, ignore_errors=True))
    except HTTPException:
        shutil.rmtree(work, ignore_errors=True)
        raise
    except (subprocess.SubprocessError, OSError, ValueError):
        shutil.rmtree(work, ignore_errors=True)
        raise HTTPException(422, 'Audio processing failed; check that the upload is a supported audio file')

app.mount('/', StaticFiles(directory=ROOT, html=True), name='site')
