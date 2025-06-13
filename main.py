from threading import Event
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from utils.logger import get_logger
from config.env_vars import config
from handlers import commands as cmd
from services.postgres_storage import PostgresStorage
from services.slack_api import SlackAPI


logger = get_logger(__name__, level=config.LOG_LEVEL)


def main():
    # Instantiate services
    storage = PostgresStorage()
    slack = SlackAPI()

    # ---------------- Scheduler -----------------
    scheduler = BackgroundScheduler()
    # Automatic rotation every Sunday 18:00
    scheduler.add_job(cmd.rotate_oncall, CronTrigger(day_of_week="sun", hour=18, minute=0, timezone="Europe/Madrid"), args=[storage])
    # Handoff reminder Monday 06:00
    scheduler.add_job(
        cmd.send_handoff_reminder,
        CronTrigger(day_of_week="mon", hour=6, minute=0, timezone="Europe/Madrid"),
        args=[slack, storage],
    )
    scheduler.start()
    logger.info("✅ Scheduler started")

    # ---------------- Event routing -------------
    def handle_events(client, req):
        # Ack
        from slack_sdk.socket_mode.response import SocketModeResponse
        response = SocketModeResponse(envelope_id=req.envelope_id)
        client.send_socket_mode_response(response)

        if req.type != "events_api":
            return
        event = req.payload.get("event", {})
        ev_type = event.get("type")
        if ev_type == "app_mention":
            handle_mention(event)
        elif ev_type == "message" and event.get("subtype") != "bot_message" and event.get("channel_type") == "im":
            handle_dm(event)

    def handle_mention(event):
        text = event.get("text", "").lower()
        channel = event["channel"]
        user = event.get("user")
        logger.info(f"Mention from {user}: {text}")
        try:
            if "who" in text or "hola" in text or "hello" in text:
                cmd.show_current_oncall(slack, storage, channel)
            elif "rotate" in text:
                cmd.rotate_oncall(storage)
                cmd.show_current_oncall(slack, storage, channel)
            elif "status" in text:
                cmd.show_rotation_status(slack, storage, channel)
            elif "swap" in text:
                import re
                # extract all user mentions
                user_ids = [m.upper() for m in re.findall(r"<@([A-Za-z0-9]+)(?:\|[^>]+)?>", text)]
                # first mention is bot itself => remove
                if user_ids and user_ids[0] == slack.web_client.auth_test()["user_id"]:
                    user_ids = user_ids[1:]
                if user_ids:
                    dest_id = user_ids[0]
                    cmd.swap_oncall(slack, storage, channel, user, dest_id)
                else:
                    slack.send(channel, "❌ Usage: swap @user")
            elif "test" in text:
                cmd.test_rotation(slack, storage, channel)
            else:
                cmd.show_help(slack, channel)
        except Exception as e:
            logger.error(f"Error processing mention: {e}")
            slack.send(channel, f"❌ Error processing command: {e}")

    def handle_dm(event):
        text = event.get("text", "")
        handle_mention({"text": text, "channel": event["channel"]})

    slack.add_request_listener(handle_events)

    # ---------------- Connect -------------------
    logger.info("🚀 Connecting to Slack Socket Mode…")
    slack.connect()
    logger.info("✅ Bot connected and running")

    Event().wait()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by user")
