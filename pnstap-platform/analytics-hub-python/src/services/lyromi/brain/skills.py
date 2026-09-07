ENTERPRISE_KEYWORDS = {

    "company",
    "companies",
    "organization",
    "organizations",
    "dashboard",
    "cypheris",
    "lyromi",
    "pnstap",
    "user",
    "users",
    "subscription",
    "invoice",
    "security",
    "threat",
    "threats",
    "sensor",
    "network",
    "traffic",
    "cpu",
    "memory",
    "disk",
    "health",
    "alert",
    "alerts",
    "activity",
    "analysis"

}


def requires_enterprise_context(message: str):

    message = message.lower()

    return any(
        keyword in message
        for keyword in ENTERPRISE_KEYWORDS
    )