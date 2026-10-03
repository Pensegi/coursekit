# coursekit

**Turn a slide deck and teacher's notes into an audiobook, a video course and subtitles.**

coursekit renders a narrated course from a presentation:

- **Audiobook:** MP3, plus M4B with chapter marks.
- **Video course:** one MP4 per module, with the slides turning in time with the narration.
- **Subtitles:** SRT, in any number of languages.
- **YouTube chapter lists**, ready to paste.

Everything renders locally with open-source tools and voices. Claude writes the narration script and the subtitle translations; coursekit does the rest, with no AI and no token cost.

```
slide deck + notes ──► Claude writes the narration ──► coursekit renders ──► audiobook · videos · subtitles
   (PPTX or PDF)          (script/*.md, one per module)    (local, no tokens)     (MP3/M4B · MP4 · SRT)
```

> Status: early. Tested end to end on Linux, with English narration (Kokoro) and English and Swedish subtitles. The Piper voices for other languages haven't been tested yet. Built to run on macOS with Homebrew.

---

## Contents

- [How it came about](#how-it-came-about)
- [Requirements](#requirements)
- [Quick start](#quick-start)
- [Setting up Claude](#setting-up-claude)
- [Making a course with Claude](#making-a-course-with-claude)
- [Commands](#commands)
- [Configuration: course.json](#configuration-coursejson)
- [Voices and languages](#voices-and-languages)
- [Script format](#script-format)
- [Output](#output)
- [Publishing on YouTube](#publishing-on-youtube)
- [Tips and limits](#tips-and-limits)
- [Licence and copyright](#licence-and-copyright)
- [Credits](#credits)

---

## How it came about

coursekit is a spin-off of a personal project, *Ukulele with Claude*. Over nine days (24 September – 2 October 2026), Dennis Rudin and Claude (Opus 5.5, in Claude Cowork) turned a question about ukulele chords into a whole course:

- a 541-page book, *A comprehensive guide to Ukulele in G-C-F-B♭ tuning*
- a companion CD of 282 tracks on four discs, rendered from the book's own notation
- a 17.7-hour audiobook with a teacher-style narrator, the Kokoro voice "George", with the CD tracks dropped in where they belong
- 27 read-along videos, the book pages turning in time with the narration, with subtitles in five languages

The pipeline that made the audiobook, the videos and the subtitles turned out not to depend on ukulele at all. coursekit is that pipeline made general: any slide deck plus notes, narrated in English, or in other languages with an extra voice.

The project also tested a way of working: AI-assisted development, not AI generation. Claude typed the code, the text and the narration; ordinary programs did the repetitive rendering at no token cost. Dennis wrote zero lines of code, but he oversaw all of it. As a senior developer, he set the direction and the requirements, made the design decisions, reviewed and tested the results, and asked for changes until they were right. Nothing went into this repository without his review.

## Requirements

- macOS or Linux, with Python 3.10–3.13 (kokoro-onnx does not support 3.14 yet)
- **ffmpeg** and **Poppler**: `brew install ffmpeg poppler`
- For a `.pptx` deck, either a PDF export of it saved next to it with the same name (in PowerPoint: File → Export → PDF), or LibreOffice installed
- Optional: **Voicebox** (voicebox.sh) to narrate in your own cloned voice

The first run of `ck.sh` creates a Python environment in `.venv/` from `requirements.txt` (kokoro-onnx, piper-tts, soundfile, numpy, python-pptx). `bash ck.sh setup` downloads the English voice model (Kokoro, about 350 MB) into `models/`. Voices for other languages are optional extra downloads; see [Voices and languages](#voices-and-languages).

## Quick start

```bash
git clone https://github.com/pensegi/coursekit.git && cd coursekit

# 0. First run: set up Python and download the voices (a few minutes; asks for nothing)
bash ck.sh setup                                         # the English voices (Kokoro); other languages: see Voices and languages

# 1. Make a course folder from a deck (its slides become images; its text and speaker notes are extracted)
bash ck.sh init ~/Courses/meetings.pptx --lang en
#    -> ~/Courses/meetings_course/  slides/  source/slides.md  course.json  script/  media/

# 2. Write the narration in script/01_*.md, 02_*.md ... (normally Claude does this; see below)

# 3. Check it, listen to the voice, then render everything
bash ck.sh check     ~/Courses/meetings_course
bash ck.sh voicetest ~/Courses/meetings_course           # -> out/voice_test.wav
bash ck.sh all       ~/Courses/meetings_course           # audio, video and subtitles
```

## Setting up Claude

coursekit renders on its own, but the narration is written by Claude. That needs a Claude plan with the skill feature; skills are available on the Free, Pro, Max, Team and Enterprise plans. Setup takes about ten minutes, once.

**1. Install the tools and coursekit.** In Terminal:

```bash
brew install ffmpeg poppler            # Homebrew: https://brew.sh
git clone https://github.com/pensegi/coursekit.git ~/git/coursekit
cd ~/git/coursekit
bash ck.sh setup                       # sets up Python and downloads the English voices; prints "ready"
```

You can put coursekit anywhere; `~/git/coursekit` is just a suggestion. Run `setup` in your own Terminal: it downloads the voice models, and Claude's sandbox may not be allowed to reach the download sites.

**2. Add the skill to Claude.** The skill (`SKILL.md`) is the recipe Claude follows.

- **Claude desktop app or claude.ai, including Cowork:**
  1. Run `bash ck.sh skill`. It makes `dist/slide-video-course.zip`.
  2. In Claude, open **Customize → Skills**, click **Add** and choose that zip file.
  3. Switch the skill on.

  Code execution must be enabled in Claude for skills to work. On Team and Enterprise plans, your administrator may need to allow custom skills.
- **Claude Code:** run `bash ck.sh skill --code`. It installs the skill in `~/.claude/skills/slide-video-course/`, and Claude Code picks it up automatically.

**3. Give Claude access to your files.**

- **Cowork (desktop app):** start a task on your computer and connect two folders with **Add folder**: the coursekit folder and the folder with your slide deck. Claude then runs coursekit there directly.
- **Claude Code:** start it in the folder with your deck, and tell it where coursekit is if it isn't in `~/git/coursekit`.

**4. Optional: your own voice.** Install Voicebox (voicebox.sh), record a voice profile, and keep the app running while you render. Then in the course's `course.json`, set `"engine": "voicebox"` and `"voicebox_profile": "<your profile name>"`.

## Making a course with Claude

Ask in plain words, for example:

> Make a video course of `~/Courses/meetings.pptx`, using the speaker notes and `guide.docx`. Narration in English, subtitles in German and Spanish.

Claude then works through these steps with you:

1. **Questions:** Claude asks about the audience, the narration language and voice, the subtitle languages, and how to split the course into modules.
2. **Reading:** it runs `init`, then reads the slide images, the slide text and the speaker notes.
3. **Writing:** it writes the narration in a teacher's voice, one script file per module, with `[SLIDE n]` markers where the slides change.
4. **Checking:** it runs `check`, and gives you a short list of points to proofread. You answer, and it revises the script.
5. **Listening:** you listen to `out/voice_test.wav` (from `voicetest`) before the full render.
6. **Rendering:** run `bash ck.sh all <course folder>` in your Terminal (fastest), or let Claude run it in short steps.
7. **Subtitles:** if you asked for other languages, Claude translates them and runs `subs` again.

Claude stays faithful to the slides and notes. Anything unclear is marked `<!-- check: ... -->` for you instead of being invented. Writing and translating use Claude (tokens); everything coursekit renders is free.

## Commands

All commands run through `ck.sh`, which sets up and uses the Python environment:

| Command | What it does |
|---|---|
| `bash ck.sh setup [en] [sv] [piper:VOICE]` | First run: sets up Python and downloads voice models. Default `en` (Kokoro); `sv` or `piper:VOICE` add a Piper voice (see [Voices and languages](#voices-and-languages)). Writes a short spoken test to `models/voice_check_*.wav` |
| `bash ck.sh skill [--code]` | Packages the Claude skill as `dist/slide-video-course.zip`; `--code` also installs it for Claude Code |
| `bash ck.sh init DECK [--course DIR] [--lang en]` | Draws the slides (1920 px PNGs); extracts slide text and speaker notes to `source/slides.md`; writes a `course.json` with default settings for the language |
| `bash ck.sh check DIR` | Checks the scripts: slide numbers exist, slides that are never shown, missing media files, symbols the voice can't read |
| `bash ck.sh voicetest DIR` | Speaks a test sentence with the configured voice, to `out/voice_test.wav` |
| `bash ck.sh audio DIR [01 02 …]` | Renders the narration: MP3, M4B with chapters, and a timing file per module |
| `bash ck.sh video DIR [01 02 …]` | Renders the videos (slides plus narration) and the YouTube chapter lists |
| `bash ck.sh subs DIR` | Exports the text for translation, and writes SRT files for every language that has a translation |
| `bash ck.sh all DIR` | Runs `audio`, `video` and `subs` |

- **Finished work is skipped.** A module is rebuilt only when its script has changed, and unchanged paragraphs come from the speech cache.
- **Pause and resume.** `--budget SECONDS` stops cleanly after that long; run the same command again to continue.

## Configuration: course.json

| Key | Meaning |
|---|---|
| `title`, `author` | Written into the audio files |
| `language` | Narration language: `en`, or another language code such as `de` or `sv` |
| `engine` | `kokoro` (English and other languages), `piper` (many languages, one voice per download), or `voicebox` (your own cloned voice; start the Voicebox app first) |
| `voice` | The voice name. Kokoro has British voices `bm_george`, `bm_lewis`, `bm_daniel`, `bm_fable`, `bf_emma`, `bf_isabella`, `bf_alice` and `bf_lily`, and American `af_*` and `am_*`. For Piper, e.g. `sv_SE-nst-medium` (list all voices with `.venv/bin/python -m piper.download_voices`). For Voicebox, the profile name |
| `speed` | 1.0 is normal; 0.95 is a calm teaching pace |
| `subtitles` | Languages to make SRT files for, the narration language first, e.g. `["en", "de", "es"]` |
| `voicebox_url`, `voicebox_profile` | Voicebox settings (default `http://127.0.0.1:17493`) |

Defaults: `init --lang en` uses Kokoro with `bm_george` at speed 0.95, and `--lang sv` uses Piper with `sv_SE-nst-medium`. For any other language, set `engine`, `voice` and `language` yourself; see below.

## Voices and languages

`bash ck.sh setup` downloads only the English voices. Add other languages when you need them.

### Kokoro (the default)

The Kokoro model is a single download, about 350 MB, and it contains all 54 of its voices. The prefix of the voice name gives the language:

| Prefix | Language | Example voices |
|---|---|---|
| `b` | British English | `bm_george` (default), `bm_fable`, `bf_emma` |
| `a` | American English | `af_*` (female), `am_*` (male) |
| `e`, `f`, `i`, `p` | Spanish, French, Italian, Brazilian Portuguese | see the full voice list; set `language` to `es`, `fr`, `it` or `pt` |
| `j`, `z`, `h` | Japanese, Mandarin, Hindi | not set up in coursekit |

Kokoro's makers note that support for languages other than English "may be absent or thin". coursekit has only been tested with British English. Full voice list: [VOICES.md](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md).

To use another Kokoro voice, change `voice` in the course's `course.json`, then run `voicetest`.

### Piper: other languages

Piper has voices for many languages, one download (about 60 MB) per voice:

```bash
.venv/bin/python -m piper.download_voices        # list all voices
bash ck.sh setup piper:de_DE-thorsten-medium     # download one voice (here German), with a spoken test
bash ck.sh setup sv                              # shortcut for the Swedish voice sv_SE-nst-medium
```

Then set it in the course's `course.json`:

```json
"language": "de",
"engine": "piper",
"voice": "de_DE-thorsten-medium",
"speed": 1.0
```

Each Piper voice has its own licence, in the `MODEL_CARD` file of its folder on [huggingface.co/rhasspy/piper-voices](https://huggingface.co/rhasspy/piper-voices). Some voices don't allow commercial use, so check before you publish. Run the downloads in your own Terminal: Claude's sandbox may not be allowed to reach Hugging Face.

### Your own voice

Use Voicebox (voicebox.sh): set `"engine": "voicebox"` and `"voicebox_profile"` in `course.json`, and keep the app running while you render.

## Script format

One Markdown file per module, in `script/`, named `NN_Name.md` and played in order:

```text
# Module title                  spoken; the first chapter of the module
[SLIDE 3]                       show slide 3 from here on (numbered as in the deck)
## Section title                spoken; a chapter in the M4B and on YouTube
A paragraph is one breath group of one to four sentences, spoken as written.
[PAUSE 3]                       three seconds of silence
[CLIP intro.mp3]                play media/intro.mp3 (any audio file)
The term {fr|déjà vu} ...       a phrase in another language (Kokoro uses that language's pronunciation)
<!-- a note -->                 not spoken: a note for the proofreader
```

Write everything the way it should be said: numbers under a hundred, units and symbols in words, and no abbreviations the voice would trip on. `check` warns about symbols such as % & / = < > € $ # @.

## Output

All output goes into the course folder's `out/` folder:

| Path | Contents |
|---|---|
| `audio/NN_Name.mp3`, `.m4b` | The narration; the M4B has a chapter for every heading |
| `audio/NN_Name.timing.json` | When every heading, paragraph, clip and slide starts and ends |
| `video/NN_Name.mp4` | 1920×1080 video (H.264, AAC); the slides change exactly at the `[SLIDE n]` markers |
| `video/NN_Name.youtube.txt` | Chapter timestamps to paste into the YouTube description |
| `subtitles/src/NN_Name.json` | The spoken text, block by block, for translating |
| `subtitles/tr/LANG/NN_Name.txt` | Translations in `@@ id` format (see `SKILL.md`) |
| `subtitles/srt/NN_Name.LANG.srt` | Timed subtitles, at most two lines of 42 characters per cue |

## Publishing on YouTube

1. Upload the MP4.
2. Paste the contents of the `.youtube.txt` file into the description: YouTube turns the timestamps into chapters.
3. Under **Subtitles**, add each language and upload its SRT file with **With timing**.

AI narration: if you publish elsewhere, check that platform's current rules on AI voices. ACX/Audible rejects AI-narrated audiobooks.

## Tips and limits

- **Run long renders on your own computer.** Speech synthesis runs on the processor. In the ukulele project, a recent Mac (M5 Pro) spoke about 23 paragraphs a minute, against 7–10 in a 2-core cloud container. That made 17.7 hours of audio in about 2 hours.
- **Interrupted runs lose nothing.** Speech is cached per paragraph and videos are built from cached segments, so an interruption never means starting over.
- **Piper speaks foreign phrases with the narrator's pronunciation.** Kokoro switches to the phrase's own language.
- **Piper voices are still untested** in coursekit. Try `voicetest` before a full render.

## Licence and copyright

Copyright 2026 Dennis Rudin.

coursekit is licensed under the **Apache License, Version 2.0**; see [`LICENSE`](LICENSE). You may use, change and redistribute it, commercially too. If you redistribute it or something based on it:

- include `LICENSE`
- keep the credit in [`NOTICE`](NOTICE)
- mark the files you changed

**Third-party software and models.** coursekit doesn't include any. They are installed or downloaded separately, each under its own licence, listed in [`LICENSE.md`](LICENSE.md).

- Piper and phonemizer, which coursekit imports, are GPL-3.0. That is compatible with Apache-2.0. A bundle that ships them together with coursekit must follow GPL-3.0.

**What you make with coursekit** is yours: the audio, the videos and the subtitles. It is subject only to the rights in your own input material: slides, notes and media.

*The licence summaries here and in `LICENSE.md` are in plain language, not legal advice.*

## Credits

- **Kokoro-82M** by hexgrad (Apache-2.0), run through **kokoro-onnx** by thewh1teagle (MIT) on **ONNX Runtime**
- **Piper** by the Open Home Foundation (GPL-3.0); voices from rhasspy/piper-voices
- **eSpeak NG** and **phonemizer**, for turning text into phonemes
- **FFmpeg**, **Poppler**, **LibreOffice**, **python-pptx**, **NumPy** and **python-soundfile**
- Designed, directed and reviewed by **Dennis Rudin**; AI-assisted development with **Claude** (Anthropic), Opus 5.5 in Claude Cowork, during the *Ukulele with Claude* project
