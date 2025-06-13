from slack_sdk.web import WebClient
from slack_sdk.socket_mode import SocketModeClient
from config.env_vars import config

class SlackAPI:
    """Wrapper around Slack Web & Socket clients"""

    def __init__(self):
        self.web_client = WebClient(token=config.SLACK_BOT_TOKEN)
        self.socket_client = SocketModeClient(
            app_token=config.SLACK_APP_TOKEN,
            web_client=self.web_client,
        )

    # --------------- messaging helpers ----------------
    def send(self, channel: str, text: str, **kwargs):
        self.web_client.chat_postMessage(channel=channel, text=text, **kwargs)

    # --------------- listeners ------------------------
    def add_request_listener(self, fn):
        self.socket_client.socket_mode_request_listeners.append(fn)

    def connect(self):
        self.socket_client.connect()
