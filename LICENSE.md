# Licences

## coursekit itself

Copyright 2026 Dennis Rudin.

coursekit's own files (`coursekit.py`, `ck.sh`, `README.md`, `SKILL.md`, `requirements.txt`, `LICENSE.md` and `NOTICE`) are licensed under the **Apache License, Version 2.0**. The full text is in `LICENSE`.

In short: you may use, change and redistribute coursekit, commercially too, and include it in your own software. If you redistribute it or something based on it:
- include `LICENSE`
- pass on the credit in `NOTICE`
- mark the files you changed

The licence also gives a patent licence from contributors.

## Third-party software (not included in this repository)

coursekit does not ship any third-party code, programs or models. Everything below is installed by the user (pip via `ck.sh`, or Homebrew) or downloaded on first use into `models/`, which is not part of the repository.

| Component | How coursekit uses it | Licence |
|---|---|---|
| Python | runs coursekit | PSF License v2 (permissive) |
| kokoro-onnx | imported (Kokoro engine) | MIT |
| ↳ phonemizer, espeakng-loader, eSpeak NG | dependencies of kokoro-onnx | GPL-3.0-or-later (phonemizer, eSpeak NG) |
| ONNX Runtime | dependency of kokoro-onnx | MIT |
| piper-tts (Piper) | imported (Piper engine) | GPL-3.0-or-later |
| python-pptx | imported (reads .pptx) | MIT |
| python-soundfile, libsndfile | imported (audio files) | BSD-3-Clause; LGPL-2.1 |
| NumPy | imported | BSD-3-Clause |
| FFmpeg, x264, LAME | run as separate programs (`ffmpeg`, `ffprobe`) | LGPL-2.1+ or GPL-2.0+, depending on the build |
| Poppler (`pdftoppm`, `pdftotext`) | run as separate programs | GPL (GPL-2.0/3.0 mix) |
| LibreOffice (`soffice`), optional | run as a separate program | MPL-2.0 |
| Voicebox, optional | reached over its local web API | MIT |

## Models and voices (downloaded on first use)

| Model | Licence |
|---|---|
| Kokoro-82M (`kokoro-v1.0.onnx`, `voices-v1.0.bin`), e.g. the voice bm_george | Apache-2.0 (model card: usable "from production environments to personal projects") |
| Piper voices, e.g. sv_SE-nst-medium | each voice has its own licence in its `MODEL_CARD` on huggingface.co/rhasspy/piper-voices. Check it before commercial use. The NST Swedish data it was trained on is published as CC0. |

## What this means

- **Using coursekit, privately or inside an organisation:** no obligations from any of these licences.
- **Things you make with coursekit** (MP3/M4B, MP4, SRT): not covered by these licences. They are yours, subject to the rights in your own input material (slides, notes, media).
- **Sharing coursekit's own files:** they are Apache-2.0. Apache-2.0 is compatible with GPL-3.0, so coursekit may import Piper and kokoro-onnx's GPL-3.0 dependencies at run time.
- **Distributing coursekit together with Piper or phonemizer** (for example as one bundle, installer or container image): that combined distribution must follow GPL-3.0, including providing the source. coursekit's own files keep their own licence.
- **FFmpeg, Poppler and LibreOffice** are run as separate programs, so their licences do not extend to coursekit.

Plain-language summary, not legal advice. Sources: the projects' LICENSE files and PyPI pages, and the FSF GPL FAQ (https://www.gnu.org/licenses/gpl-faq.html).
