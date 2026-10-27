# Configure the AI narrator

Use this guide to connect the game to OpenAI and to choose a model.

## Set your API key

1. Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

2. Set your key in `.env`:

   ```bash
   OPENAI_API_KEY=sk-...
   ```

3. Start the game without `--offline`:

   ```bash
   python main.py
   ```

`main.py` loads `.env` automatically. Variables that are already exported in your shell take precedence over `.env`.

## Choose a model

The default model is `gpt-4o-mini`. To change it, set `DND_MODEL` in `.env`, or pass `--model` for one run:

```bash
python main.py --model gpt-4o
```

The model must support the Chat Completions API with `response_format={"type": "json_object"}`. The narrator uses JSON mode for actions, NPC dialogue and quest text.

## Tune the narrator's memory

The narrator sends the last `DND_HISTORY_TURNS` exchanges (default `8`) with each request. Each request also includes a snapshot of the scene and the last 8 journal entries. A larger value gives more continuity but uses more tokens per request:

```bash
DND_HISTORY_TURNS=4
```

## What happens when the API fails

If a request fails, or the model returns invalid JSON, the game shows one warning and uses the offline narrator for that turn:

```text
AI narrator unavailable (Error code: 401 ...). Using offline narration.
```

The game shows the warning again only after a request succeeds and a later one fails. Check your key, network and model name.

## Play fully offline

```bash
python main.py --offline
```

If `OPENAI_API_KEY` is empty, the game also falls back to the offline narrator and shows a warning.
