import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration settings
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
# Default spend cap if not set in environment
SPEND_CAP = int(os.getenv("SPEND_CAP", 5000))

def get_config():
    """Returns a dictionary containing all configuration settings."""
    return {
        "razorpay_key_id": RAZORPAY_KEY_ID,
        "razorpay_key_secret": RAZORPAY_KEY_SECRET,
        "spend_cap": SPEND_CAP
    }

# Example of how to use the config:
# config = get_config()
# print(f"Razorpay Key ID: {config['razorpay_key_id']}")