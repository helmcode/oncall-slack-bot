import json
from datetime import datetime
from utils.logger import get_logger
from utils.helpers import get_current_oncall_text
from config.env_vars import config
from config.team import SRE_MEMBERS, REGIONS
from services.postgres_storage import PostgresStorage as Storage
from services.slack_api import SlackAPI

logger = get_logger(__name__, level=config.LOG_LEVEL)

# ========================= COMMANDS ===========================

def show_current_oncall(slack: SlackAPI, storage: Storage, channel: str):
    """Shows who is currently on call"""
    try:
        logger.info("Showing current oncall")
        text = get_current_oncall_text(storage, "👋 Hi! Who is oncall:")
        slack.send(channel, text)
    except Exception as e:
        logger.error(f"Error showing oncall: {e}")
        slack.send(channel, f"❌ Error showing oncall: {str(e)}")

def show_rotation_status(slack: SlackAPI, storage: Storage, channel: str):
    """Shows the rotation status and history"""
    try:
        logger.info("Showing rotation status")
        status_text = "📊 *System On-Call Status*\n\n"

        for region in ["LATAM", "EU"]:
            current_member_id = storage.get_oncall(region)
            current_idx = storage.get_rotation_idx(region)

            if current_member_id:
                member = next(m for m in SRE_MEMBERS if m.slack_id == current_member_id)
                status_text += f"🔄 *{region}*: {member.name} (position {current_idx})\n"

            history = storage.lrange(region, limit=1)
            if history:
                last_change = json.loads(history[0])
                last_date = datetime.fromisoformat(last_change["timestamp"]).strftime("%d/%m %H:%M")
                status_text += f"   Last change: {last_date}\n\n"

        status_text += "📅 *Next in rotation*:\n"
        for region, members in REGIONS.items():
            current_idx = storage.get_rotation_idx(region)
            next_idx = (current_idx + 1) % len(members)
            next_member = members[next_idx]
            status_text += f"• {region}: {next_member.name}\n"

        slack.send(channel, status_text)

    except Exception as e:
        logger.error(f"Error showing rotation status: {e}")
        slack.send(channel, f"❌ Error showing rotation status: {str(e)}")

def rotate_oncall(storage: Storage):
    """Executes the automatic rotation"""
    logger.info("🔄 Executing rotation")
    for region, members in REGIONS.items():
        try:
            current_idx = storage.get_rotation_idx(region)
            next_idx = (current_idx + 1) % len(members)
            next_member = members[next_idx]

            storage.set_oncall(region, next_member.slack_id)
            storage.set_rotation_idx(region, next_idx)

            history_entry = {
                "member_id": next_member.slack_id,
                "timestamp": datetime.now().isoformat()
            }
            storage.push_history(region, next_member.slack_id)

            logger.info(f"Rotating to {next_member.name} in {region}")

        except Exception as e:
            logger.error(f"Error rotating for {region}: {e}")

def test_rotation(slack: SlackAPI, storage: Storage, channel: str):
    """Executes a test rotation"""
    logger.info("🧪 Executing test rotation")
    rotate_oncall(storage)
    slack.send(channel, "🧪 *Test rotation executed!*\n\nNew state:")
    text = get_current_oncall_text(storage, "")
    slack.send(channel, text)

def show_help(slack: SlackAPI, channel: str):
    """Shows available commands"""
    help_text = """* 🤖Available commands:*\n\n\n• *@Bender who*: Shows who is on call.\n• *@Bender status*: Shows the rotation status.\n• *@Bender rotate*: Forces a rotation in both regions.\n• *@Bender swap @user*: Lets the current on-call pass the shift to @user.\n• *@Bender test*: Executes a test rotation.\n• *@Bender help*: Shows this help message."""
    slack.send(channel, help_text)

def send_handoff_reminder(slack: SlackAPI, storage: Storage):
    """Sends handoff reminder on Sunday"""
    try:
        current_latam = storage.get_oncall("LATAM")
        current_eu = storage.get_oncall("EU")

        if not current_latam or not current_eu:
            logger.error("Could not get information for handoff reminder")
            return

        message = f"""⏰ *Handoff reminder*

<@{current_latam}> <@{current_eu}>

📋 *For Monday*:
• Automatic rotation at 8:00 AM
• Prepare summary of incidents from this week
• Document Support Changelog

💡 *Tip*: Use this thread for the handoff: https://doc.helmcode.com/s/helmcode/p/soporte-cH4gDGPkc4"""


        slack.send(config.SUPPORT_CHANNEL, message)

    except Exception as e:
        logger.error(f"❌ Error sending handoff reminder: {e}")
        slack.send(config.SUPPORT_CHANNEL, f"❌ Error sending handoff reminder: {e}")

# ---------------- Swap on-call -----------------

def swap_oncall(slack: SlackAPI, storage: Storage, channel: str, requester_id: str, dest_id: str):
    """Allows current on-call to hand over the shift to another member in same region."""
    try:
        # Find region where requester is on-call
        region = None
        for reg in REGIONS.keys():
            if storage.get_oncall(reg) == requester_id:
                region = reg
                break

        if not region:
            slack.send(channel, "❌ Only the current on-call can initiate a swap.")
            return

        # Validate dest is in rotation list for that region
        dest_id = dest_id.upper()
        members = REGIONS[region]
        if not any(m.slack_id.upper() == dest_id for m in members):
            slack.send(channel, f"❌ <@{dest_id}> is not part of {region} rotation.")
            return

        # Execute swap
        storage.set_oncall(region, dest_id)
        storage.push_history(region, dest_id)

        slack.send(channel, f"✅ Shift for *{region}* transferred to <@{dest_id}>.")

    except Exception as e:
        logger.error(f"Error swapping oncall: {e}")
        slack.send(channel, f"❌ Error swapping oncall: {e}")
