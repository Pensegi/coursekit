---
name: slide-video-course
description: Turn a slide deck (PPTX/PDF) plus teacher's notes or a guide into a narrated audiobook, a slide-turning video course and translated subtitles with the local coursekit toolkit.
---

# Slide deck to audiobook and video course

Claude writes the narration and the subtitle translations (tokens). The coursekit toolkit on the user's computer does everything else locally, with open-source voices and no tokens: slide images, speech, mixing, video, subtitle timing.

## The toolkit

- **Finding coursekit.** It's the folder holding `ck.sh`, `coursekit.py` and `README.md`, wherever the user cloned it (often `~/git/coursekit`).
  - Look in the folders connected to this session first.
  - If you can't find it, ask the user where it is. In Cowork, also ask them to connect it with "Add folder".
  - Read its `README.md` for the script format, the `course.json` keys and the commands.
- **Commands** (in the user's Terminal, or in the device sandbox): `bash ck.sh setup`, `skill`, `init DECK --lang en|sv`, `check DIR`, `voicetest DIR`, `audio DIR`, `video DIR`, `subs DIR`, `all DIR`.
  - Add `--budget 150` to stop after about 150 s; the same command resumes.
  - Finished modules are skipped. Changed scripts are rebuilt, reusing unchanged speech.
- **Voices:**
  - English: Kokoro (default `bm_george`, British, speed 0.95).
  - Other languages: a Piper voice, downloaded once with `bash ck.sh setup piper:VOICE` (`bash ck.sh setup sv` for Swedish, `sv_SE-nst-medium`). `setup` without arguments downloads only the English voices.
  - The user's own voice: Voicebox, with the profile named in `course.json`. The Voicebox app must be running, and only the user's computer can reach it.
- **Requirements on the user's computer:** `brew install ffmpeg poppler`. A .pptx also needs a PDF export next to it with the same name, or LibreOffice.
- **Where to run it:**
  - **First run:** if `models/` has no voice models yet, ask the user to run `bash ck.sh setup` once in their own Terminal. It downloads the voices, and the download sites (Hugging Face for Piper) may be blocked from Claude's sandbox.
  - **After that:** Claude can drive renders in the device sandbox with repeated `--budget 150` calls, also when the user is away. Each sandbox command lasts at most 180 s, and background processes stop when it ends.
  - **Long renders:** these are faster in the user's own Terminal, so offer them the command (`bash ck.sh all DIR`).
  - **Speed:** a recent Mac renders roughly 20-30 paragraphs a minute; video encodes at about 20x real time.

## Procedure

1. **Clarify.** Use AskUserQuestion for anything not given:
   - deck and guide files
   - audience and level
   - narration language and voice
   - subtitle languages
   - module split
   - target length
   - whether it will be published (YouTube public or unlisted, internal only)
2. **Init.** Run `bash ck.sh init DECK --lang LANG`. This creates `DECK_course/` with:
   - `slides/s-NNN.png`
   - `source/slides.md`: slide text plus speaker notes, with hidden slides marked
   - `course.json`: set title, author, voice and subtitles.
3. **Read the material.**
   - Read `source/slides.md` and any guide document.
   - Look at the slide images (stage them into the cloud workspace and Read them). Diagrams and charts carry meaning that the text extraction misses.
4. **Plan modules.** One script file per module (`script/01_Name.md`, `02_...`), usually one per deck section or chapter, 5-20 minutes each (about 150 spoken words a minute). Every visible slide should be shown at least once.
5. **Write the narration** following the style below. Each module starts with `# Module title` and `[SLIDE n]`. Put `[SLIDE n]` exactly where the slide should appear, and `## Section` for each topic, since these become chapters. For more than about 30 slides, write a style brief file and split the modules between parallel subagents. Then check that every slide marker is present and in order.
6. **Check.** Run `bash ck.sh check DIR` and fix everything it reports.
7. **Proofreading.**
   - Give the user a short list of the `<!-- check: ... -->` notes and any choices made.
   - Revise the script after their answers.
   - Have them listen to `voicetest` before the full render.
8. **Render.** `bash ck.sh all DIR` writes:
   - `out/audio`: MP3 and M4B with chapters, plus timing
   - `out/video`: MP4 at 1920x1080, plus `.youtube.txt` chapter timestamps
   - `out/subtitles/srt`
9. **Subtitles in other languages.**
   - After `subs`, `out/subtitles/src/NAME.json` holds the text block by block.
   - Translate into `out/subtitles/tr/LANG/NAME.txt` in this format, every id exactly once, one paragraph per entry:
     ```
     @@ 0
     translated text
     @@ 1
     ...
     ```
   - Long modules can be split into `NAME.part1.txt`, `NAME.part2.txt` and so on, continuing the ids.
   - For large courses, give each language (or language and module group) its own subagent, with a brief that holds a fixed terminology table and the form of address (Swedish du, German du or Sie as agreed, French vous, Spanish tú).
   - Run `subs` again. It reports missing ids and writes `NAME.LANG.srt`. If a script changed after translating, re-translate the changed paragraphs.
10. **Deliver.**
    - Say where the files are. For YouTube: upload the MP4, paste the `.youtube.txt` into the description, and upload each SRT under Subtitles with "With timing".
    - Remind the user that client material is confidential and should not be published without the client's permission.

## Narration style

- **Voice and tone.** A warm, clear, encouraging teacher talking to one learner. Use second person, short sentences and concrete examples. Explain what each slide shows and why it matters, rather than reading the bullet points aloud.
- **Faithfulness.** Stay faithful to the slides, the notes and the guide. Never invent facts, figures, names, quotes or references. Where the material is unclear or seems wrong, follow it and add `<!-- check: ... -->` for the proofreader.
- **Paragraphs.** One paragraph is one breath group of 1-4 sentences. Use `[PAUSE 3]` sparingly, where the learner should think or try something.
- **Writing for the ear.** Spell out whatever the voice must say:
  - numbers under a hundred, percentages, currencies and units in words
  - dates and times in words
  - no symbols, slashes, arrows or parentheses
  - abbreviations expanded (Swedish: "t.ex." becomes "till exempel", "bl.a." becomes "bland annat")
  - acronyms the way they are said
- **Foreign names and titles** are marked `{xx|text}`. With Kokoro they get that language's pronunciation; with Piper they keep the narrator's pronunciation. Don't mark everyday loanwords.
- **Slide references.** Mention what the learner sees ("On this slide, the chart on the left..."), but never rely on colour alone.
- **Length.** Roughly 80-200 words per content slide, 40-80 for title and section slides. Add a short welcome at the start of the course and a recap at the end of each module.
- **Spelling.** British spelling for English. Swedish follows the Swedish Language Council's style guide (Språkrådet).
- **No formatting in spoken text.** No lists, tables, bold or links.
