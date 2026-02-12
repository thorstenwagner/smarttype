# SmartType

**AI-powered text completion for anyone who needs to type less.**

SmartType uses Claude AI to turn abbreviated, incomplete, or shorthand text into fully formed, grammatically correct sentences — in any text field, in any application.

## Why SmartType exists

This software was written by an ALS patient, for ALS patients.

When you live with ALS, you rely on eye tracking and on-screen keyboards to communicate. Every single character costs effort and time. If you were once a fast touch typist, the difference is devastating. A message that used to take seconds now takes minutes. Conversations move on without you. The frustration builds up, especially in daily communication — messaging friends, writing emails, or using voice synthesis systems.

SmartType changes that. Instead of painstakingly typing out every word, you type just enough for the AI to understand what you mean:

```
ih mss mrgn zm arzt ghn
→ Ich muss morgen zum Arzt gehen.
```

```
cn yu pls hlp me wth ths
→ Can you please help me with this?
```

```
wnt we actly go swmmng
→ Do we actually want to go swimming?
```

Type less. Say more. Stay in the conversation.

## Features

- **Optimized for eye tracking** — all shortcuts are designed for the on-screen keyboard of the [Tobii PCEye 5](https://www.tobii.com/products/assistive-technology), so everything can be triggered without closing the on-screen keyboard
- **Works in any text field** — Signal, Word, Element, browsers, email, voice synthesis software
- **Understands heavily abbreviated text** — skip vowels, shorten words, leave out grammar
- **Multi-language** — German and English, switchable with a hotkey
- **Two modes**:
  - **Full line mode** (default): Completes everything from cursor backward
  - **Marker mode**: Place `...` before the text you want completed
- **Audio & visual feedback** — beep sounds and on-screen toast notifications
- **Zero setup** — API key is asked on first run and saved automatically
- **Customizable** — hotkeys, language, AI model, and prompts are all configurable

## Installation

### From PyPI

```bash
pip install smarttype-ai
```

### From source

```bash
git clone https://github.com/twagner/smarttype.git
cd smarttype
pip install .
```

### With Conda

```bash
conda env create -f environment.yml
conda activate smarttype
pip install .
```

## Getting started

1. Get a free Claude API key from [console.anthropic.com](https://console.anthropic.com/)
2. Run SmartType:

```bash
smarttype
```

On first launch, it will ask for your API key and save it automatically.

You can also provide the key in a `.env` file:

```env
CLAUDE_API_KEY=sk-ant-...
```

## Usage

```bash
smarttype          # start SmartType
python -m smarttype  # alternative
```

### Hotkeys

| Hotkey | Action |
|---|---|
| `Ctrl+Shift+J` | Complete text at cursor |
| `Ctrl+Shift+G` | Toggle language (DE/EN) |
| `Ctrl+Shift+H` | Toggle marker mode on/off |
| `Ctrl+C` | Exit SmartType |

### How it works

1. Type your abbreviated text in any text field
2. Place the cursor at the end
3. Press `Ctrl+Shift+J`
4. SmartType selects the text, sends it to Claude, and replaces it with the completed version

### Examples

**Abbreviated German:**

```
ih hbe sps bei vln din abr bsors brtsple
→ Ich habe Spaß bei vielen Dingen, aber besonders bei Brettspielen.
```

**Abbreviated English:**

```
i hve fun mny thngs but espcly bord gmes
→ I have fun with many things, but especially with board games.
```

**Minimal input, full output:**

```
me feeling good. no pain
→ I'm feeling good. I have no pain.
```

**Marker mode** — when you only want part of a line completed:

```
Dear Dr. Smith, ...i wntd to ask abt my nxt appntmnt
→ Dear Dr. Smith, I wanted to ask about my next appointment.
```

## Configuration

All settings via environment variables or `.env` file:

| Variable | Default | Description |
|---|---|---|
| `CLAUDE_API_KEY` | *(required)* | Your Anthropic API key |
| `SMARTTYPE_HOTKEY` | `ctrl+shift+j` | Completion hotkey |
| `SMARTTYPE_LANG_HOTKEY` | `ctrl+shift+g` | Language toggle hotkey |
| `SMARTTYPE_MARKER_HOTKEY` | `ctrl+shift+h` | Marker mode toggle hotkey |
| `SMARTTYPE_MODEL` | `claude-sonnet-4-5-20250929` | Claude model |
| `SMARTTYPE_LANGUAGE` | `de` | Starting language (`de` or `en`) |

## Custom prompts

Place a `prompt_de.txt` or `prompt_en.txt` in your working directory to override the built-in prompts. This lets you fine-tune how the AI interprets and completes your text.

## Requirements

- Windows 10/11
- Python 3.10+
- Claude API key ([get one here](https://console.anthropic.com/))

## License

MIT
