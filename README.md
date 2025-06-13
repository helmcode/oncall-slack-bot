# On-Call Slack Bot

A Slack bot that manages on-call rotations for the SRE team.

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt  # asegúrate de que existen las deps

# Export env vars (adapt .env or your own secrets manager)
export SLACK_APP_TOKEN="xapp-..."
export SLACK_BOT_TOKEN="xoxb-..."
export REDIS_URL="redis://localhost:6379/0"

python main.py
```

## Architecture

```
services/
  storage.py     # RedisStorage – high-level API for Redis
  slack_api.py   # SlackAPI – wraps Web & Socket clients
handlers/
  commands.py    # Business logic for Slack commands
utils/
  helpers.py     # Small pure-logic helpers
main.py          # Application wiring & entry point
```

Legacy `bot.py` remains for reference and now exits with a deprecation message.

## Available commands

Inside Slack (mention the bot or DM):

* `who` – shows current on-call
* `status` – shows rotation status
* `rotate` – forces rotation (admin)
* `test` – executes a test rotation
* `help` – shows help text

## Scheduler jobs

* Automatic rotation: Sunday 18:00 Europe/Madrid
* Handoff reminder:   Monday 06:00 Europe/Madrid

These are registered in `main.py` via APScheduler.
