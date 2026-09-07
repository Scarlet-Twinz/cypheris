import re


def detect_intent(message: str):

    text = message.lower().strip()

    # Greetings
    if re.search(r"\b(hi|hello|hey|good morning|good afternoon|good evening)\b", text):
        return "greeting"

    # Enterprise / Cypheris
    enterprise_keywords = [
        "company",
        "companies",
        "organization",
        "organizations",
        "dashboard",
        "threat",
        "threats",
        "user",
        "users",
        "subscription",
        "invoice",
        "network",
        "sensor",
        "traffic",
        "cpu",
        "memory",
        "disk",
        "security",
        "cypheris",
        "lyromi",
        "pnstap"
    ]

    if any(word in text for word in enterprise_keywords):
        return "enterprise"

    # Programming
    coding_keywords = [
        "python",
        "javascript",
        "react",
        "vite",
        "fastapi",
        "sql",
        "html",
        "css",
        "api",
        "code",
        "bug",
        "error",
        "program"
    ]

    if any(word in text for word in coding_keywords):
        return "coding"

    # Cybersecurity
    cyber_keywords = [
        "malware",
        "virus",
        "ransomware",
        "firewall",
        "exploit",
        "vulnerability",
        "attack",
        "ddos",
        "phishing",
        "cve"
    ]

    if any(word in text for word in cyber_keywords):
        return "cybersecurity"

    # Mathematics
    math_keywords = [
        "solve",
        "calculate",
        "equation",
        "integral",
        "derivative",
        "matrix",
        "probability",
        "statistics",
        "math"
    ]

    if any(word in text for word in math_keywords):
        return "math"

    return "general"