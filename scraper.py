import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Dict, Any, List, Set, Optional

EMAIL_REGEX = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')

IGNORE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.css', '.js', '.woff', '.woff2', '.mp4'}
IGNORE_DOMAINS = {
    'sentry.io', 'wixpress.com', 'schema.org', 'w3.org', 'google.com', 'googleapis.com',
    'facebook.com', 'instagram.com', 'contactout.com', 'rocketreach.co', 'apollo.io',
    'lusha.com', 'signalhire.com', 'zoominfo.com', 'dnb.com', 'nic.in', 'gov.in',
    'cloudflare.com', 'domain.com', 'example.com'
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

def clean_email(email: str) -> Optional[str]:
    email = email.strip().lower()
    for ext in IGNORE_EXTENSIONS:
        if email.endswith(ext):
            return None
    domain = email.split('@')[-1]
    if domain in IGNORE_DOMAINS:
        return None
    return email

def extract_emails_from_html(html_content: str) -> Set[str]:
    found = set()
    matches = EMAIL_REGEX.findall(html_content)
    for m in matches:
        cleaned = clean_email(m)
        if cleaned:
            found.add(cleaned)
    return found

def audit_business_website(url: str, business_name: str, category: str) -> Dict[str, Any]:
    """
    Crawls homepage and contact page of a business website to extract emails
    and audit capabilities (digital menu, online booking, mobile responsiveness).
    """
    if not url:
        return {
            "has_website": False,
            "has_digital_menu": False,
            "has_booking_system": False,
            "opportunity_score": 95,
            "primary_angle": "website_creation",
            "audit_summary": "No website found. High priority prospect for a complete digital setup.",
            "emails": []
        }

    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    emails: Set[str] = set()
    has_digital_menu = False
    has_booking_system = False
    is_mobile_responsive = False
    site_alive = False

    try:
        resp = requests.get(url, headers=HEADERS, timeout=8, allow_redirects=True)
        if resp.status_code == 200:
            site_alive = True
            soup = BeautifulSoup(resp.text, "html.parser")
            
            # Check viewport
            viewport = soup.find("meta", attrs={"name": "viewport"})
            if viewport:
                is_mobile_responsive = True
                
            # Extract emails from homepage
            emails.update(extract_emails_from_html(resp.text))
            
            # Extract mailto links
            for a in soup.find_all("a", href=True):
                href = a["href"].strip()
                if href.startswith("mailto:"):
                    raw = href.split("mailto:")[-1].split("?")[0]
                    c = clean_email(raw)
                    if c:
                        emails.add(c)
                        
            # Analyze page text
            page_text = soup.get_text().lower()
            
            # Menu keywords
            menu_keywords = ["digital menu", "online menu", "order online", "qr code menu", "our menu", "view menu", "takeout menu"]
            if any(kw in page_text for kw in menu_keywords):
                has_digital_menu = True
                
            # Booking keywords
            booking_keywords = ["book appointment", "schedule appointment", "book online", "reserve table", "online booking", "calendly", "zocdoc"]
            if any(kw in page_text for kw in booking_keywords):
                has_booking_system = True

            # If no email yet, check contact / about pages
            contact_links = []
            for a in soup.find_all("a", href=True):
                href = a["href"]
                text = a.get_text().lower()
                if any(k in text or k in href.lower() for k in ["contact", "about", "reach"]):
                    full_link = urljoin(url, href)
                    if urlparse(full_link).netloc == urlparse(url).netloc:
                        contact_links.append(full_link)

            for cl in contact_links[:2]:
                try:
                    c_resp = requests.get(cl, headers=HEADERS, timeout=6)
                    if c_resp.status_code == 200:
                        emails.update(extract_emails_from_html(c_resp.text))
                except Exception:
                    pass

    except Exception as e:
        # Site unreachable
        return {
            "has_website": False,
            "has_digital_menu": False,
            "has_booking_system": False,
            "opportunity_score": 90,
            "primary_angle": "website_redesign",
            "audit_summary": f"Website ({url}) was unreachable or inactive. Great opportunity to offer modern hosting and design.",
            "emails": []
        }

    # Opportunity scoring and angle decision
    score = 50
    audit_notes = []
    
    if "restaurant" in category.lower() or "cafe" in category.lower():
        if not has_digital_menu:
            score = 88
            angle = "digital_menu_system"
            audit_notes.append("Lacks an interactive digital QR menu and direct online ordering.")
        else:
            score = 65
            angle = "website_redesign"
            audit_notes.append("Has existing menu features; pitch website modernization or faster mobile UX.")
    elif "physio" in category.lower() or "rehab" in category.lower():
        if not has_booking_system:
            score = 90
            angle = "online_booking"
            audit_notes.append("No automated 24/7 patient therapy consultation booking detected.")
        else:
            score = 65
            angle = "website_redesign"
            audit_notes.append("Has booking system; pitch modern therapy service showcase and mobile UX.")
    elif "dental" in category.lower() or "clinic" in category.lower() or "doctor" in category.lower():
        if not has_booking_system:
            score = 85
            angle = "online_booking"
            audit_notes.append("No automated 24/7 patient booking system detected.")
        else:
            score = 60
            angle = "website_redesign"
            audit_notes.append("Has booking system; pitch modern patient experience and search visibility.")
    else:
        if not is_mobile_responsive:
            score = 85
            angle = "website_redesign"
            audit_notes.append("Website is not optimized for modern mobile smartphone screens.")
        else:
            score = 65
            angle = "website_redesign"
            audit_notes.append("Modern mobile site detected; pitch conversion rate optimization.")

    return {
        "has_website": site_alive,
        "has_digital_menu": has_digital_menu,
        "has_booking_system": has_booking_system,
        "is_mobile_responsive": is_mobile_responsive,
        "opportunity_score": score,
        "primary_angle": angle,
        "audit_summary": " ".join(audit_notes) if audit_notes else "Ready for digital upgrade pitch.",
        "emails": list(emails)
    }
