---
name: translate-srt
description: Translate SRT subtitle files into other languages
argument-hint: <language> [file-or-glob]
disable-model-invocation: true
---

# Translate SRT Subtitle Files

Translate SRT subtitle files into the target language specified by the user.

## Arguments

- `$0` — **Required.** Target language (e.g. `Chinese`, `Japanese`, `Spanish`, `French`).
- `$1` — Optional. A specific `.srt` file path or glob pattern. If omitted, translate **all** `.srt` files in the `downloads/` directory.

## Instructions

1. **Identify files to translate.** If `$1` is provided, use it (resolve as a path or glob). Otherwise, glob for `downloads/*.srt`.

2. **Skip already-translated files.** For each source file, the translated output is saved alongside it with a language suffix before the extension:
   - `downloads/01_Introduction.srt` → `downloads/01_Introduction.<lang>.srt`
   - The `<lang>` tag should be a short lowercase language code (e.g. `zh` for Chinese, `ja` for Japanese, `es` for Spanish, `fr` for French, `ko` for Korean, `de` for German).
   - If the translated file already exists, **skip it** and print a message.
   - Also skip files that are themselves translations (filenames matching `*.<lang>.srt`).

3. **Translate each file.** For each SRT file:
   - Read the entire file content.
   - Translate **only the subtitle text lines** into `$0`. Preserve all sequence numbers, timestamps, and blank lines exactly as-is.
   - Keep the translation natural and fluent — not word-for-word. Match the tone and register of the original.
   - Technical terms, proper nouns, and product names (e.g. "Claude Code", "GitHub", "MCP") should be kept in their original form or use their widely-accepted translated form.
   - Write the translated content to the output file.

4. **Report progress.** Print a summary line for each file processed (translated or skipped).
