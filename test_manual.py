import sys
from dotenv import load_dotenv

load_dotenv()

from tracking import fetch_tracking
from formatter import format_status_for_voice

def test_manual():
    print("Testing imports and function execution (this will likely fail on network if credentials are bad/missing)...")
    try:
        raw_data = fetch_tracking("DUMMY_AWB_12345")
        summary = format_status_for_voice(raw_data)
        print("Success! Summary:")
        print(summary)
    except Exception as e:
        print(f"Network or Auth Failed (Expected if credentials are not set): {type(e).__name__} - {e}")

if __name__ == "__main__":
    test_manual()
