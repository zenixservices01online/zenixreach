import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional

OPT_OUT_FOOTER = """

---
You are receiving this one-time message because {business_name} was listed in public business directories. If you prefer not to receive digital suggestions from Zenix Services (https://zenixservices.online), simply reply 'unsub' and you will not be contacted again.
"""

def send_email_message(
    to_email: str,
    business_name: str,
    subject: str,
    body: str,
    smtp_settings: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Dispatches or simulates email sending based on dry_run_mode.
    """
    to_email_clean = (to_email or "").strip()
    if not to_email_clean or "@" not in to_email_clean:
        return {
            "success": False,
            "simulated": False,
            "error": "Invalid recipient email address"
        }

    is_dry_run = smtp_settings.get("dry_run_mode", True)
    sender_email = (smtp_settings.get("sender_email") or "zenixservices67@gmail.com").strip()
    sender_name = (smtp_settings.get("sender_name") or "Vishal Kumar Tiwari").strip()

    full_body = body + OPT_OUT_FOOTER.format(business_name=business_name)

    if is_dry_run:
        time.sleep(0.5)
        return {
            "success": True,
            "simulated": True,
            "recipient": to_email_clean,
            "sender": f"{sender_name} <{sender_email}>",
            "subject": subject,
            "message": f"[SIMULATION MODE] Simulated delivery from {sender_name} <{sender_email}> to {to_email_clean}. (To send REAL live email directly to inbox, uncheck Simulation Mode and add your 16-character Gmail App Password in Settings)."
        }

    # Live SMTP Send
    host = smtp_settings.get("smtp_host", "smtp.gmail.com")
    primary_port = int(smtp_settings.get("smtp_port", 587))
    user = (smtp_settings.get("smtp_user") or sender_email).strip()
    raw_pass = smtp_settings.get("smtp_pass", "")
    password = (raw_pass or "").strip().replace(" ", "")

    if not user or not password:
        return {
            "success": False,
            "simulated": False,
            "error": f"SMTP password is not set for {sender_email}. Please enter your 16-character Google App Password in Settings (⚙️ Settings -> Link Gmail) or re-enable Simulation Mode."
        }

    # Ensure sender matches authenticated Gmail account to avoid Google SPF/relay rejection
    actual_sender_email = user if ("@" in user and "gmail.com" in user.lower()) else sender_email

    msg = MIMEMultipart()
    msg["From"] = f"{sender_name} <{actual_sender_email}>"
    msg["To"] = to_email_clean
    msg["Reply-To"] = actual_sender_email
    msg["Subject"] = subject
    msg.attach(MIMEText(full_body, "plain", "utf-8"))

    # Try primary port first, fallback to alternate port (587 <-> 465)
    ports_to_try = [primary_port, 465 if primary_port != 465 else 587]
    last_error = None

    for p in ports_to_try:
        try:
            if p == 465:
                server = smtplib.SMTP_SSL(host, p, timeout=12)
            else:
                server = smtplib.SMTP(host, p, timeout=12)
                server.starttls()

            server.login(user, password)
            server.send_message(msg)
            server.quit()

            return {
                "success": True,
                "simulated": False,
                "recipient": to_email_clean,
                "sender": f"{sender_name} <{actual_sender_email}>",
                "subject": subject,
                "message": f"Successfully sent live email from {sender_name} <{actual_sender_email}> to {to_email_clean} via {host}:{p}"
            }
        except smtplib.SMTPAuthenticationError as auth_err:
            err_str = str(auth_err)
            if "534" in err_str:
                diag = f"Google requires a 16-character App Password (not your standard Google password). Turn ON 2-Step Verification and generate one at myaccount.google.com/apppasswords."
            else:
                diag = f"Gmail rejected credentials for {user}. Please ensure 2-Step Verification is ON and you generated a 16-character App Password at myaccount.google.com/apppasswords (not your standard login password)."
            return {
                "success": False,
                "simulated": False,
                "error": diag
            }
        except Exception as e:
            last_error = e
            continue

    return {
        "success": False,
        "simulated": False,
        "error": f"Failed to connect to {host} on ports 587/465: {str(last_error)}"
    }

def test_smtp_connection(smtp_settings: Dict[str, Any]) -> Dict[str, Any]:
    host = smtp_settings.get("smtp_host", "smtp.gmail.com")
    primary_port = int(smtp_settings.get("smtp_port", 587))
    user = (smtp_settings.get("smtp_user") or smtp_settings.get("sender_email") or "").strip()
    raw_pass = smtp_settings.get("smtp_pass", "")
    password = (raw_pass or "").strip().replace(" ", "")

    if not user:
        return {"success": False, "message": "Gmail address cannot be blank. Please enter your Gmail address."}

    if not password:
        return {"success": False, "message": "App Password cannot be blank. Enter your 16-character Google App Password."}

    ports_to_try = [primary_port, 465 if primary_port != 465 else 587]
    last_error = None

    for p in ports_to_try:
        try:
            if p == 465:
                server = smtplib.SMTP_SSL(host, p, timeout=10)
            else:
                server = smtplib.SMTP(host, p, timeout=10)
                server.starttls()
            server.login(user, password)
            server.quit()
            return {"success": True, "message": f"✓ Connected & authenticated with {host}:{p} for {user} successfully!"}
        except smtplib.SMTPAuthenticationError as auth_err:
            err_str = str(auth_err)
            if "534" in err_str:
                return {
                    "success": False,
                    "message": f"Google requires a 16-character App Password (not your standard Google password). Enable 2-Step Verification and generate an App Password at myaccount.google.com/apppasswords."
                }
            return {
                "success": False,
                "message": f"Gmail rejected credentials for {user}. Make sure 2-Step Verification is ON and you generated a 16-character App Password at myaccount.google.com/apppasswords (not your normal login password)."
            }
        except Exception as e:
            last_error = e
            continue

    return {"success": False, "message": f"Connection to {host} failed on ports 587/465: {str(last_error)}"}
