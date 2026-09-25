from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import tempfile, subprocess, os

app=FastAPI(title='Cadence Singer Lab')
ROOT=Path(__file__).parent

@app.post('/api/render')
async def render(guide:UploadFile=File(...),voice_ref:UploadFile|None=File(None),lyrics:str=Form(''),mode:str=Form('performance'),start_seconds:float=Form(0.0)):
    work=Path(tempfile.mkdtemp(prefix='cadence_singer_'))
    gp=work/('guide_'+(guide.filename or 'guide.wav'));gp.write_bytes(await guide.read())
    vp=None
    if voice_ref:
        vp=work/('voice_'+(voice_ref.filename or 'voice.wav'));vp.write_bytes(await voice_ref.read())
    rendered=work/'rendered.wav'
    engine=os.environ.get('SINGING_ENGINE_CMD','').strip()
    if mode=='performance':
        if engine:
            if not vp: raise HTTPException(400,'Reference voice required for configured performance-transfer engine.')
            cmd=engine.format(guide=str(gp),voice=str(vp),out=str(rendered))
            subprocess.run(cmd,shell=True,check=True)
        else:
            subprocess.run(['ffmpeg','-y','-i',str(gp),'-ar','44100','-ac','1',str(rendered)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    else:
        raise HTTPException(501,'Hum + Lyrics needs an SVS backend with explicit phoneme duration/pitch control.')
    aligned=work/'ai_vocal_aligned.wav'
    subprocess.run(['ffmpeg','-y','-f','lavfi','-i',f'anullsrc=r=44100:cl=mono:d={start_seconds:.6f}','-i',str(rendered),'-filter_complex','[0:a][1:a]concat=n=2:v=0:a=1[out]','-map','[out]','-ar','44100','-c:a','pcm_s24le',str(aligned)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return FileResponse(aligned,media_type='audio/wav',filename='ai_vocal_aligned.wav')

app.mount('/',StaticFiles(directory=ROOT,html=True),name='site')
