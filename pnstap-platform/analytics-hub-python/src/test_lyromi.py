from services.lyromi.engine import LyromiEngine


tests = [
    "Hi",
    "How many companies do we have?",
    "List our companies.",
    "Which companies are active?",
    "How many inactive companies do we have?",
    "How many users do we have?",
    "List our users.",
    "How many active users do we have?",
    "How many inactive users do we have?",
    "How many admins do we have?",
    "Which company does Cypheris Administrator belong to?",
    "Tell me about Cypheris.",
    "How many users does Cypheris have?",
    "What threats does Cypheris have?",
    "How many critical threats are there?",
    "Show recent alerts.",
    "What is happening on the network?",
    "What is our security posture?",
    "What is Cypheris subscription plan?",
    "Are any companies over their user limit?",
    "What is the dashboard status?",
]


for question in tests:

    print("\n" + "=" * 70)
    print("QUESTION:", question)
    print("=" * 70)

    try:

        answer = LyromiEngine.process(question)

        print("ANSWER:", answer)

    except Exception as error:

        print("ERROR:", error)
