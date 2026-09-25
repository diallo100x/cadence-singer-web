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
