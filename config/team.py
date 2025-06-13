from dataclasses import dataclass

@dataclass
class SREMember:
    name: str
    slack_id: str
    region: str
    timezone: str

# =============================================================================
# ======================= TEAM CONFIGURATION ============================
# =============================================================================
# IDs of the SRE team members
# To get a user's ID in Slack:
# 1. Go to their profile.
# 2. Click on the three dots (...).
# 3. Select "Copy member ID".
# =============================================================================

SRE_MEMBERS = [
    SREMember("Sebas", "U082JG9JXJS", "LATAM", "America/Bogota"),
    SREMember("Deivid", "U089K1AF42H", "LATAM", "America/Bogota"),
    SREMember("Cristian", "U047YAB5QAC", "EU", "Europe/Madrid"),
    SREMember("Pau", "U05BPAFRWRK", "EU", "Europe/Madrid"),
    SREMember("Mariano", "U08UY2ML22W", "EU", "Europe/Madrid")
]

REGIONS = {
    "LATAM": [m for m in SRE_MEMBERS if m.region == "LATAM"],
    "EU": [m for m in SRE_MEMBERS if m.region == "EU"]
}
