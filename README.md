# Cadence Singer Lab v0.1

A web app for generating AI vocals while keeping **your cadence** and placing the vocal at an **exact bar/beat**.

## Core idea
Instead of asking a generative music model to guess when to sing, the guide performance becomes the timing authority.

1. Perform the actual lyrics with the melody/cadence you want.
2. Preserve internal timing, slides, breaths, pickups, and phrasing.
3. Use a singing voice-conversion engine to change the timbre.
4. Place the result at an exact sample position after synthesis.

"Bar 3, Beat 1" is therefore deterministic, not prompt engineering.

## Modes
### Performance Transfer — recommended
Sing/rap the words once. A voice-conversion backend supplies the target timbre while preserving performance.

### Hum + Lyrics — experimental
Hum the melody and provide text. This needs an SVS engine with explicit phoneme durations and pitch curves (DiffSinger/OpenUtau-style architecture).

## Run locally
Requirements: Python 3.10+, ffmpeg.

```bash
pip install -r requirements.txt
uvicorn server:app --reload --port 8080
```
Open `http://localhost:8080`.

## Connect a singing engine
Set `SINGING_ENGINE_CMD`. It receives `{guide}`, `{voice}`, `{out}`.

Example shape:
```bash
export SINGING_ENGINE_CMD='python /path/to/svc.py --source "{guide}" --target "{voice}" --output "{out}"'
```

Use only voices you own or have permission to use. Stock/licensed voicebanks are ideal for a public-facing product.

## Next build targets
- RMVPE pitch extraction
- lyric/phoneme alignment editor
- pitch curve lane
- syllable split/merge
- breath markers
- formant/tone controls
- stock voice browser
- A/B renders
- doubles/harmonies
- section-loop rendering
- dry/tuned/double/harmony export

## Public test deployment
The Dockerfile runs FastAPI and includes ffmpeg. Push this repository to GitHub, then in Render create a Blueprint from the repository; `render.yaml` defines a Docker web service. The service starts with `uvicorn server:app --host 0.0.0.0 --port $PORT`. Check `/api/health` after deployment. Use HTTPS for Safari audio playback. This is a guide-performance fallback, **not an AI voice model**.

Environment variables:
- `PORT`: assigned by host; defaults to 8080.
- `MAX_UPLOAD_BYTES`: maximum bytes per uploaded audio file, default 104857600.
- `SINGING_ENGINE_CMD`: optional, trusted administrator-provided command template supporting `{guide}`, `{voice}`, `{out}`. Leave unset for the guide fallback. Only configure with a reviewed engine command and a licensed or consented voice.

Uploads are held temporarily for each render and removed after the response. Audio, lyrics, and voice samples are not stored in the Git repository. On small hosting plans, long audio files can exceed CPU, memory, or request time limits. Safari supports audio formats according to the device and OS; WAV and M4A are practical inputs.

## v0.2 Cadence Editor direction
Build on the preserved sample-based alignment: waveform and piano-roll lanes, syllable blocks with duration and pitch curves, slides, vibrato and breath markers, bar/beat/subdivision coordinates, snap toggle, hard-locked first syllable, and natural internal timing as the default. Changes to timing should be explicit edits to guide-derived events. Preserve the working version in Git before adding extraction or synthesis architecture.
