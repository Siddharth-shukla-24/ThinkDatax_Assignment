"""Standalone evaluation script for the reply classifier.
Run with: python -m scripts.eval_classifier
"""
from app.services.reply_classifier import classify_reply

EXAMPLES = [
    ("Hey, this actually sounds really useful - can we grab 15 minutes this week to talk it through?", "Interested"),
    ("Thanks for reaching out but we're not interested at the moment, we just signed with another vendor.", "Not Interested"),
    ("Please remove me from your mailing list, I don't want any more emails from StyleSense.", "Unsubscribe Request"),
    ("Bad timing right now, we're mid-quarter. Maybe circle back to me in a couple months?", "Needs Follow-up"),
    ("Who gave you my email? I don't know what StyleSense AI is.", "Other"),
    ("Sounds interesting, tell me more about the pricing and let's set up a call.", "Interested"),
    ("No thanks, we already use a different forecasting tool and it's working fine for us.", "Not Interested"),
    ("Not right now but check back with me next quarter, budget's already allocated for this year.", "Needs Follow-up"),
]


def main() -> None:
    correct = 0
    for text, expected in EXAMPLES:
        result = classify_reply("Alex", text)
        predicted = result["label"]
        is_correct = predicted == expected
        correct += int(is_correct)
        mark = "PASS" if is_correct else "FAIL"
        print(f"[{mark}] expected={expected:<20} predicted={predicted:<20} | {text[:60]}")

    print(f"\nAccuracy: {correct}/{len(EXAMPLES)} correct")


if __name__ == "__main__":
    main()