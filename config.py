import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("DATA_DIR", BASE_DIR / "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = Path(os.environ.get("DB_PATH", DATA_DIR / "localreach.db"))

DEFAULT_SETTINGS = {
    "sender_name": "Vishal Kumar Tiwari",
    "company_name": "Zenix Services",
    "sender_title": "Co-Founder, Zenix Services",
    "sender_email": "zenixservices67@gmail.com",
    "website_url": "https://zenixservices.online",
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_user": "zenixservices67@gmail.com",
    "smtp_pass": "",
    "use_tls": True,
    "dry_run_mode": True,  # Safe default until Gmail App password is provided
    "send_delay_seconds": 3,
    "gemini_api_key": "",
    "default_offer_restaurant": "Modern Website + Digital QR Menu System",
    "default_offer_dental": "Modern Patient Website + 24/7 Online Appointment Booking",
    "default_offer_physio": "Modern Patient Website + 24/7 Therapy Appointment Booking",
    "default_offer_small_clinic": "Modern Patient Website + Online Appointment Scheduling & OPD Timings",
    "default_offer_general": "High-Converting Mobile-Friendly Website Redesign"
}
