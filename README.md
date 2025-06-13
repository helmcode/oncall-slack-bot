# On-Call Slack Bot

A Slack bot that manages on-call rotations for the SRE team.

## Quick start

```bash
uv venv .venv && source .venv/bin/activate
uv pip install -r requirements.txt  # asegúrate de que existen las deps

# Export env vars (adapt .env or your own secrets manager)
export SLACK_APP_TOKEN="xapp-..."
export SLACK_BOT_TOKEN="xoxb-..."
export SUPPORT_CHANNEL="#oncall"
export LOG_LEVEL="DEBUG" # DEBUG, INFO, WARNING, ERROR
export DATABASE_URL="postgresql://user:password@localhost:5432/postgres"

uv run main.py
```

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
