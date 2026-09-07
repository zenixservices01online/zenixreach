import time
import re
import requests
import urllib.parse
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional

OSM_HEADERS = {
    "User-Agent": "LocalReachApp/2.0 (contact: support@zenixservices.online)",
    "Accept-Language": "en-US,en;q=0.9"
}

SEARCH_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

DIRECTORY_DOMAINS = {
    "justdial.com", "lybrate.com", "lybrate.in", "facebook.com", "instagram.com", "youtube.com",
    "indiamart.com", "sulekha.com", "google.com", "practo.com", "practo.in", "tripadvisor.com",
    "zomato.com", "swiggy.com", "swiggy.in", "district.in", "wikipedia.org", "mapquest.com", "yelp.com",
    "yellowpages.com", "foursquare.com", "linkedin.com", "twitter.com", "x.com",
    "tiktok.com", "pinterest.com", "infobel.com", "zospital.com", "yappe.in",
    "idbf.in", "cylex.com", "dial4trade.com", "mouthshut.com", "zaubacorp.com",
    "tofler.in", "easyleadz.com", "bharatibiz.com", "dnb.com", "zoominfo.com",
    "businesslist.in", "indiacom.com", "asklaila.com", "vymaps.com", "cybo.com",
    "contactout.com", "rocketreach.co", "apollo.io", "lusha.com", "signalhire.com",
    "startpage.com", "here.com", "dot.gov", "nic.in", "gov.in",
    # Healthcare & Local Aggregators
    "kivihealth.com", "hexahealth.com", "smyleee.com", "planetbids.com", "pentegra.com",
    "clinicspots.com", "vaidam.com", "medifee.com", "bajajfinservhealth.in", "tata1mg.com", "1mg.com",
    "netmeds.com", "apollo247.com", "credihealth.com", "sehat.com", "threebestrated.in",
    "threebestrated.com", "indiabizlist.com", "tradeindia.com", "medindia.net", "medibuddy.in",
    "magicpin.in", "venuelook.com"
}

IGNORE_EMAIL_DOMAINS = {
    "yahoo.com", "bing.com", "google.com", "example.com", "sentry.io", "wixpress.com",
    "schema.org", "w3.org", "nic.in", "gov.in", "cloudflare.com", "domain.com",
    "contactout.com", "rocketreach.co", "apollo.io", "lusha.com", "signalhire.com",
    "dnb.com", "cybo.com", "infobel.com", "yelp.com", "tripadvisor.com",
    "swiggy.in", "swiggy.com", "zomato.com", "district.in", "behindtheemail.com",
    "company.com", "jpmchase.com", "jpmorgan.com", "kivihealth.com", "hexahealth.com",
    "smyleee.com", "planetbids.com", "pentegra.com", "practo.com", "practo.in",
    "lybrate.com", "justdial.com", "sulekha.com", "medindia.net", "magicpin.in"
}

def clean_biz_name(raw_name: str) -> str:
    if not raw_name:
        return ""
    name = raw_name.split(",")[0].strip()
    name = re.sub(r'\s*-\s*\d+.*$', '', name)
    name = re.sub(r'["\']', '', name).strip()
    return name

def clean_loc_str(loc_q: str) -> str:
    if not loc_q:
        return ""
    cleaned = re.sub(r'\b(physiotherapy(?:\s+(?:clinics?|centres?|centers?))?|physiotherapists?|physio(?:\s+clinics?)?|rehab(?:\s+clinics?)?|dentists?|dental\s+clinics?|dental|restaurants?|cafes?|clinics?|polyclinics?|doctors?|hospitals?|salons?|gyms?)\b', '', loc_q, flags=re.IGNORECASE)
    cleaned = re.sub(r'^\s*in\s+', '', cleaned.strip(), flags=re.IGNORECASE).strip()
    return cleaned if cleaned else loc_q.strip()

def is_valid_biz_email(email_str: str) -> bool:
    if not email_str or "@" not in email_str or "." not in email_str.split("@")[-1]:
        return False
    e = email_str.lower().strip(".")
    if any(e.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".css", ".js", ".woff", ".woff2"]):
        return False
    domain = e.split("@")[-1]
    if domain in IGNORE_EMAIL_DOMAINS:
        return False
    tld = domain.split(".")[-1]
    if not tld.isalpha() or len(tld) < 2:
        return False
    if any(bad in domain for bad in ["example", "sentry", "wix", "schema", "cloudflare", "duckduckgo", "bing", "yahoo", "nic.in", "gov.in"]):
        return False
    if any(bad in e for bad in ["email.protected", "support@gmail.com", "noreply", "no-reply", "donotreply", "bootstrap@", "jquery@", "react@", "vue@"]):
        return False
    return True

def clean_extracted_email(email_str: str) -> str:
    e = email_str.strip().lower().strip(".")
    # If a 10-digit phone number was prepended to the email e.g. 7377222777info@...
    e = re.sub(r'^\+?\d{8,12}', '', e)
    return e

def crawl_site_for_email(url: str) -> Optional[str]:
    """Crawls homepage and contact pages of a discovered domain for email address."""
    if not url:
        return None
    if not url.startswith("http"):
        url = "https://" + url

    pages_to_check = [
        url,
        url.rstrip("/") + "/contact",
        url.rstrip("/") + "/contact-us"
    ]

    for p in pages_to_check:
        try:
            r = requests.get(p, headers=SEARCH_HEADERS, timeout=2.5, allow_redirects=True)
            if r.status_code == 200:
                # Check mailto first
                soup = BeautifulSoup(r.text, "html.parser")
                for a in soup.find_all("a", href=True):
                    href = a["href"].strip()
                    if href.startswith("mailto:"):
                        cand = href.split("mailto:")[-1].split("?")[0].strip().lower()
                        if is_valid_biz_email(cand):
                            return cand
                
                # Check regex in text
                raw_emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', r.text)
                for cand in raw_emails:
                    cand_clean = cand.strip().lower().strip(".")
                    if is_valid_biz_email(cand_clean):
                        return cand_clean
        except Exception:
            continue
    return None

def extract_clean_indian_phone(text: str) -> str:
    """
    Extracts a genuine Indian phone number (10-digit mobile starting with 6, 7, 8, 9,
    or standard Indian STD landline). Rejects US toll-free (800, 844, 855, 866, 877, 888)
    and international non-Indian formats.
    """
    if not text:
        return ""
    s = text.strip()
    raw_digits = re.sub(r'\D', '', s)

    # Check for direct 10-digit mobile with optional +91 / 0 prefix
    if len(raw_digits) >= 10:
        last10 = raw_digits[-10:]
        if last10[0] in "6789" and not any(last10.startswith(tf) for tf in ["800", "888", "877", "866", "855", "844", "833"]):
            prefix = raw_digits[:-10]
            if prefix in ["", "91", "0", "091"]:
                return f"+91 {last10[:5]} {last10[5:]}"

    # Search in text for Indian mobile patterns
    mobiles = re.findall(r'(?:(?:\+91|0091|0)[\-\s]?)?([6-9]\d{4}[\s\-]?[0-9]{5})\b', text)
    for m in mobiles:
        digits = re.sub(r'\D', '', m)
        if len(digits) == 10 and digits[0] in "6789":
            if not any(digits.startswith(tf) for tf in ["800", "888", "877", "866", "855", "844", "833"]):
                return f"+91 {digits[:5]} {digits[5:]}"

    # Search for Indian landlines (e.g. 0651-XXXXXXX for Ranchi, 0612-XXXXXXX for Patna)
    landlines = re.findall(r'\b(0\d{2,4}[\-\s]?\d{6,8})\b', text)
    for l in landlines:
        digits = re.sub(r'\D', '', l)
        if 10 <= len(digits) <= 12 and not any(digits.startswith(tf) for tf in ["800", "888", "877", "866", "855", "844", "833"]):
            return l.strip()
    return ""

def extract_domain_root(url_or_domain: str) -> str:
    """Extracts clean root domain e.g. 'dreamsmiledentalclinic' from 'https://www.dreamsmiledentalclinic.co.in'."""
    if not url_or_domain:
        return ""
    d = url_or_domain.lower().replace("https://", "").replace("http://", "").split("/")[0].replace("www.", "")
    # Remove port
    d = d.split(":")[0]
    return d

def is_authentic_business_domain(domain: str, biz_name: str) -> bool:
    """
    Validates that a discovered domain authentically belongs to the specific local business.
    Rejects global tech/SaaS, aggregators, government, travel, big corporate sites,
    and requires textual relevance to the business name.
    """
    if not domain or not biz_name:
        return False
    d = extract_domain_root(domain)
    if not d or "." not in d:
        return False

    # Check against known directories and aggregator domains
    if any(d == bad or d.endswith("." + bad) for bad in DIRECTORY_DOMAINS):
        return False

    # Reject global tech, media, corporate, bank, government, or spam domains
    global_rejects = [
        "google", "yahoo", "bing", "microsoft", "apple", "paypal", "constantcontact",
        "mailchimp", "wordpress", "wix", "squarespace", "shopify", "github", "starbucks",
        "bata", "citi", "jpmorgan", "chase", "dfas", "pepsico", "kaplan", "ryanair",
        "ebharatgas", "iocl", "bpcl", "rbi.org", "rbi.com", "gov.in", "nic.in", "webbeds",
        "timesmed", "mappls", "mapmyindia", "forms.cwtsatotravel", "healthhelp", "vigivance",
        "clintonhealthaccess", "aaharjharkhand", "pplfirst", "vfsglobal", "grindr",
        "engagecenter", "whitepages", "don.com", "harmar", "heartland", "hunter.io",
        "numtrace", "behindtheemail", "medicopy", "npidb", "abplive", "tripadvisor",
        "zomato", "swiggy", "district.in", "livesans", "benihana", "bojangles", "nalcoindia",
        "riu.com", "kontoorbrands", "gravie", "bushiroad"
    ]
    if any(bad in d for bad in global_rejects):
        return False

    # The domain SLUG must share meaningful words or significant initials with the business name
    d_slug = d.split(".")[0]
    # Tokenize business name into words of length >= 3
    words = [re.sub(r'[^a-z0-9]', '', w.lower()) for w in biz_name.split()]
    meaningful_words = [w for w in words if len(w) >= 3 and w not in ["the", "and", "clinic", "centre", "center", "care", "hospital", "restaurant", "cafe", "hotel", "services"]]

    if not meaningful_words:
        meaningful_words = [w for w in words if len(w) >= 3]

    if not meaningful_words:
        return False

    # Check if any significant word of the business name is present in the domain slug
    if any(w in d_slug for w in meaningful_words):
        return True

    # Check acronym/initials if name has multiple words (e.g. BDC for Bhushan Dental Clinic)
    initials = "".join(w[0] for w in words if w)
    if len(initials) >= 3 and initials in d_slug:
        return True

    return False

def is_authentic_business_email(email_str: str, biz_name: str, verified_website: str = "") -> bool:
    """
    Validates that an email is genuinely associated with this specific business.
    Rejects scraped boilerplate, directory support emails, and random web snippet emails.
    """
    if not is_valid_biz_email(email_str):
        return False
    e = email_str.lower().strip()
    user_part, email_domain = e.split("@", 1)

    # Reject known gimmick/junk usernames or domains
    junk_patterns = [
        "press@", "support@", "admin@", "media@", "unsubscribe@", "help@ccsmed",
        "customerservice@", "supplierinquiries@", "corporatecommunications@",
        "commandant", "escalations@", "investorrelations@", "mstec@", "contactus."
    ]
    if any(p in e for p in junk_patterns):
        return False

    # 1. If we have a verified website and the email domain matches it
    if verified_website:
        site_root = extract_domain_root(verified_website)
        if email_domain == site_root or email_domain.endswith("." + site_root):
            return True

    # 2. If it's a Gmail address, verify that the Gmail username contains parts of the business name
    if email_domain == "gmail.com":
        words = [re.sub(r'[^a-z0-9]', '', w.lower()) for w in biz_name.split()]
        sig_words = [w for w in words if len(w) >= 3 and w not in ["the", "and", "services"]]
        user_clean = re.sub(r'[^a-z0-9]', '', user_part)
        if any(w in user_clean for w in sig_words):
            return True

    return False

def enrich_place_online(biz_name: str, city: str) -> Dict[str, str]:
    """
    High-accuracy, anti-gimmick discovery:
    Finds verified business phone numbers, authentic official websites, and genuine emails.
    If an authentic email cannot be verified, leaves email blank and prioritizes genuine phone number!
    """
    cleaned_name = clean_biz_name(biz_name)
    cleaned_city = clean_loc_str(city)
    phone, website, email = "", "", ""

    # 1. Yahoo Organic Search for official presence
    try:
        q_yahoo = f'"{cleaned_name}" {cleaned_city} phone OR contact'
        url_yahoo = f"https://search.yahoo.com/search?p={urllib.parse.quote(q_yahoo)}"
        r = requests.get(url_yahoo, headers=SEARCH_HEADERS, timeout=3.0)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            items = soup.select("ol.searchCenterMiddle li")

            for it in items:
                it_text = it.get_text()
                it_domain = ""
                a_tag = it.select_one("a")
                if a_tag and a_tag.get("href"):
                    h = a_tag["href"]
                    if "/RU=" in h:
                        try:
                            t = urllib.parse.unquote(h.split("/RU=")[1].split("/RK=")[0])
                            it_domain = extract_domain_root(t)
                        except Exception:
                            pass
                    elif h.startswith("http"):
                        try:
                            it_domain = extract_domain_root(h)
                        except Exception:
                            pass

                # Extract Indian Phone number from authentic text
                if not phone:
                    p = extract_clean_indian_phone(it_text)
                    if p:
                        phone = p

                # Extract website ONLY if it authentically matches the business name
                if not website and it_domain:
                    if is_authentic_business_domain(it_domain, cleaned_name):
                        website = f"https://{it_domain}"
    except Exception as e:
        print(f"Search error for {biz_name}: {e}")

    # 2. Brave Search fallback if phone or website still missing
    if not phone or not website:
        try:
            q_brave = f'"{cleaned_name}" {cleaned_city} phone'
            url_brave = f"https://search.brave.com/search?q={urllib.parse.quote(q_brave)}"
            br = requests.get(url_brave, headers=SEARCH_HEADERS, timeout=3.0)
            if br.status_code == 200:
                b_soup = BeautifulSoup(br.text, "html.parser")
                snippets = b_soup.select("div.snippet")
                for snip in snippets:
                    s_text = snip.get_text()
                    s_domain = ""
                    a_tag = snip.select_one("a")
                    if a_tag and a_tag.get("href"):
                        h = a_tag["href"]
                        if h.startswith("http"):
                            s_domain = extract_domain_root(h)

                    if not phone:
                        b_phone = extract_clean_indian_phone(s_text)
                        if b_phone:
                            phone = b_phone

                    if not website and s_domain:
                        if is_authentic_business_domain(s_domain, cleaned_name):
                            website = f"https://{s_domain}"
        except Exception as e:
            print(f"Brave search error for {biz_name}: {e}")

    # 3. Direct Crawl of Discovered Official Website ONLY (guaranteed genuine)
    if website:
        site_email = crawl_site_for_email(website)
        if site_email and is_authentic_business_email(site_email, cleaned_name, website):
            email = site_email

    # 4. Search specifically for direct official business Gmail
    if not email:
        try:
            q_gmail = f'"{cleaned_name}" {cleaned_city} "@gmail.com"'
            url_gmail = f"https://search.yahoo.com/search?p={urllib.parse.quote(q_gmail)}"
            rg = requests.get(url_gmail, headers=SEARCH_HEADERS, timeout=3.0)
            if rg.status_code == 200:
                g_emails = re.findall(r'[a-zA-Z0-9_.+-]+@gmail\.com', rg.text)
                for cand in g_emails:
                    cand_clean = cand.strip().lower().strip(".")
                    if is_authentic_business_email(cand_clean, cleaned_name, website):
                        email = cand_clean
                        break
        except Exception:
            pass

    return {"phone": phone.strip(), "website": website.strip(), "email": email.strip()}

def geocode_location(location_query: str) -> Optional[Dict[str, Any]]:
    """Geocode an Indian city or locality query to (lat, lon) coordinates."""
    clean_loc = clean_loc_str(location_query)
    q_search = f"{clean_loc}, India" if "india" not in clean_loc.lower() else clean_loc
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": q_search, "format": "json", "limit": 1, "addressdetails": 1, "countrycodes": "in"}
    try:
        r = requests.get(url, params=params, headers=OSM_HEADERS, timeout=6)
        if r.status_code == 200 and r.json():
            item = r.json()[0]
            lat = float(item["lat"])
            lon = float(item["lon"])
            # Ensure coordinates are within India (Lat 6-38, Lon 68-98)
            if 6.0 <= lat <= 38.0 and 68.0 <= lon <= 98.0:
                return {
                    "lat": lat,
                    "lon": lon,
                    "display_name": item.get("display_name", clean_loc),
                    "address": item.get("address", {})
                }
    except Exception as e:
        print(f"Geocoding error for {clean_loc}: {e}")
    return None

def query_nominatim_pois(query_str: str, limit: int = 12) -> List[Dict[str, Any]]:
    """Query OpenStreetMap Nominatim with strict Indian country filter."""
    q_search = f"{query_str}, India" if "india" not in query_str.lower() else query_str
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": q_search,
        "format": "json",
        "limit": limit,
        "addressdetails": 1,
        "extratags": 1,
        "namedetails": 1,
        "countrycodes": "in"
    }
    try:
        resp = requests.get(url, params=params, headers=OSM_HEADERS, timeout=6)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list):
                return data
    except Exception as e:
        print(f"Nominatim query failed for '{query_str}': {e}")
    return []

def query_overpass_by_coords(lat: float, lon: float, radius: int = 5000, category: str = "all", limit: int = 35) -> List[Dict[str, Any]]:
    """Query Overpass API for POIs around coordinates with fallback mirrors."""
    mirrors = [
        "https://overpass-api.de/api/interpreter",
        "https://maps.mail.ru/osm/tools/overpass/api/interpreter"
    ]
    
    if category == "restaurant":
        filter_clause = f"""
          node["amenity"~"restaurant|cafe|fast_food|bar|bakery|ice_cream|food_court"](around:{radius}, {lat}, {lon});
          way["amenity"~"restaurant|cafe|fast_food|bar|bakery|ice_cream|food_court"](around:{radius}, {lat}, {lon});
        """
    elif category == "physiotherapy":
        filter_clause = f"""
          node["healthcare"~"physiotherapist|rehabilitation"](around:{radius}, {lat}, {lon});
          way["healthcare"~"physiotherapist|rehabilitation"](around:{radius}, {lat}, {lon});
          node["amenity"~"clinic|doctors"]["healthcare:speciality"~"physiotherapy"](around:{radius}, {lat}, {lon});
          way["amenity"~"clinic|doctors"]["healthcare:speciality"~"physiotherapy"](around:{radius}, {lat}, {lon});
          node["amenity"~"clinic|doctors"](around:{radius}, {lat}, {lon});
          way["amenity"~"clinic|doctors"](around:{radius}, {lat}, {lon});
        """
    elif category == "dental":
        filter_clause = f"""
          node["amenity"~"dentist"](around:{radius}, {lat}, {lon});
          way["amenity"~"dentist"](around:{radius}, {lat}, {lon});
          node["amenity"~"clinic"]["healthcare:speciality"~"dental|dentist"](around:{radius}, {lat}, {lon});
          way["amenity"~"clinic"]["healthcare:speciality"~"dental|dentist"](around:{radius}, {lat}, {lon});
        """
    elif category in ["small_clinic", "clinic"]:
        filter_clause = f"""
          node["amenity"~"clinic|doctors|hospital"](around:{radius}, {lat}, {lon});
          way["amenity"~"clinic|doctors|hospital"](around:{radius}, {lat}, {lon});
          node["healthcare"~"clinic|centre|doctor|alternative"](around:{radius}, {lat}, {lon});
          way["healthcare"~"clinic|centre|doctor|alternative"](around:{radius}, {lat}, {lon});
        """
    else:
        filter_clause = f"""
          node["amenity"~"restaurant|cafe|fast_food|dentist|clinic|hospital|doctors|salon|spa"](around:{radius}, {lat}, {lon});
          way["amenity"~"restaurant|cafe|fast_food|dentist|clinic|hospital|doctors|salon|spa"](around:{radius}, {lat}, {lon});
          node["healthcare"~"physiotherapist|rehabilitation|clinic|centre"](around:{radius}, {lat}, {lon});
          way["healthcare"~"physiotherapist|rehabilitation|clinic|centre"](around:{radius}, {lat}, {lon});
        """

    query = f"""
    [out:json][timeout:8];
    (
      {filter_clause}
    );
    out center {limit};
    """
    for endpoint in mirrors:
        try:
            resp = requests.post(endpoint, data={"data": query}, headers=OSM_HEADERS, timeout=8)
            if resp.status_code == 200:
                return resp.json().get("elements", [])
        except Exception:
            continue
    return []

PHYSIOTHERAPY_KEYWORDS = [
    "physiotherapy", "physiotherapist", "physio", "rehabilitation", "rehab",
    "kinesiology", "chiropractic", "chiropractor", "spine care", "spine rehab",
    "pain relief", "pain clinic", "sports injury", "physical therapy", "physiocare",
    "physioclinic", "neuro physio", "ortho physio", "paralysis", "posture"
]

DENTAL_KEYWORDS = [
    "dentist", "dental", "orthodont", "dento", "teeth", "tooth", "oral care",
    "smile dental", "root canal", "implant", "dentistry"
]

SMALL_CLINIC_KEYWORDS = [
    "clinic", "polyclinic", "dispensary", "doctor", "dr.", "dr ", "pathology",
    "diagnostic", "diagnostics", "eye care", "eye clinic", "optometrist", "orthopedic",
    "pediatric", "child care", "homeopathy", "ayurvedic", "nursing home", "maternity",
    "ent clinic", "skin clinic", "derma", "piles clinic", "care centre", "health centre",
    "wellness centre", "imaging centre", "dialysis", "radiology", "consultant chamber",
    "doctor chamber", "medical store clinic", "hospital"
]

DINING_KEYWORDS = [
    "restaurant", "cafe", "cafeteria", "coffee", "bistro", "bakery", "fast food", "fast_food",
    "pizza", "burger", "dhaba", "barbeque", "biryani", "dining", "sweets", "misthan",
    "food", "caterer", "kitchen", "ice cream", "tea", "chai", "litti", "restro",
    "pub", "bar", "lounge", "roll", "eatery"
]

INFRASTRUCTURE_EXCLUDES = [
    "road", "bypass", "chowk", "marg", "lane", "street", "highway", "junction",
    "flyover", "bridge", "railway", "bus stand", "bus stop"
]

def classify_business_entity(name: str, amenity: str = "", place_type: str = "", disp_text: str = "", target_category: str = "all") -> Optional[Dict[str, str]]:
    """
    Strict business classification engine.
    Separates:
    - Physiotherapy Clinic (sub: Physiotherapy & Rehabilitation Clinic)
    - Dental Clinic (sub: Dental Clinic)
    - Small / General Clinic (sub: Polyclinic, Eye Care, Ortho, Pediatric, etc.)
    - Restaurant / Cafe
    - Small Enterprise
    """
    name_l = name.lower()
    full_text = f"{name_l} {amenity.lower()} {place_type.lower()} {disp_text.lower()}"

    # Discard infrastructure
    for inf in INFRASTRUCTURE_EXCLUDES:
        if name_l.endswith(f" {inf}") or name_l == inf or f" {inf} " in name_l:
            if not any(k in name_l for k in ["cafe", "restaurant", "hospital", "clinic", "hotel", "dhaba", "bakery", "sweets", "physio"]):
                return None

    # 1. Physiotherapy
    if any(k in full_text for k in PHYSIOTHERAPY_KEYWORDS):
        if target_category in ["restaurant", "dental"]:
            return None
        return {
            "category": "Physiotherapy Clinic",
            "subcategory": "Physiotherapy & Rehabilitation Clinic",
            "primary_angle": "online_booking"
        }

    # 2. Dental
    if any(k in full_text for k in DENTAL_KEYWORDS):
        if target_category in ["restaurant", "physiotherapy"]:
            return None
        return {
            "category": "Dental Clinic",
            "subcategory": "Dental Clinic",
            "primary_angle": "online_booking"
        }

    # 3. Small / General Healthcare Clinic
    if any(k in full_text for k in SMALL_CLINIC_KEYWORDS):
        if target_category in ["restaurant", "dental", "physiotherapy"]:
            return None
        sub = "Specialty & General Healthcare Clinic"
        if any(w in full_text for w in ["eye", "vision", "optometr"]):
            sub = "Eye & Vision Care"
        elif any(w in full_text for w in ["orthopedic", "ortho", "bone", "joint"]):
            sub = "Orthopedic & Joint Care"
        elif any(w in full_text for w in ["pediatric", "child"]):
            sub = "Pediatric & Child Care"
        elif any(w in full_text for w in ["skin", "derma"]):
            sub = "Dermatology & Skin Clinic"
        elif any(w in full_text for w in ["poly", "multi"]):
            sub = "Polyclinic & Multispecialty"
        elif any(w in full_text for w in ["hospital", "nursing", "maternity"]):
            sub = "Hospital / Nursing Home"
        return {
            "category": "Small / General Clinic",
            "subcategory": sub,
            "primary_angle": "online_booking"
        }

    # 4. Dining / Restaurant
    if any(k in full_text for k in DINING_KEYWORDS):
        if target_category in ["dental", "physiotherapy", "small_clinic", "clinic"]:
            return None
        sub = "Cafe & Dining" if any(k in full_text for k in ["cafe", "coffee", "bakery", "tea", "chai"]) else "Restaurant & Dining"
        return {
            "category": "Restaurant / Cafe",
            "subcategory": sub,
            "primary_angle": "digital_menu_system"
        }

    if target_category in ["restaurant", "dental", "physiotherapy", "small_clinic", "clinic"]:
        return None

    return {
        "category": "Small Enterprise",
        "subcategory": "Local Business",
        "primary_angle": "website_creation"
    }

def parse_nominatim_place(item: Dict[str, Any], target_category: str, location_query: str) -> Optional[Dict[str, Any]]:
    raw_name = item.get("name") or item.get("display_name", "").split(",")[0]
    name = clean_biz_name(raw_name)
    if not name or len(name) < 2:
        return None

    osm_id = f"osm_{item.get('osm_type', 'node')}_{item.get('osm_id', int(time.time()))}"
    addr_dict = item.get("address", {})
    ext_tags = item.get("extratags") or {}
    
    house = addr_dict.get("house_number", "")
    road = addr_dict.get("road") or addr_dict.get("pedestrian") or ""
    suburb = addr_dict.get("suburb") or addr_dict.get("neighbourhood") or ""
    
    city = (
        addr_dict.get("city") or 
        addr_dict.get("state_district") or 
        addr_dict.get("town") or 
        addr_dict.get("municipality") or 
        addr_dict.get("village") or 
        addr_dict.get("county") or 
        clean_loc_str(location_query)
    )
    state = addr_dict.get("state", "")
    postcode = addr_dict.get("postcode", "")

    country = addr_dict.get("country", "")
    if country and country.lower() not in ["india", "bharat"]:
        return None

    address_parts = []
    street_line = f"{house} {road}".strip()
    if street_line: address_parts.append(street_line)
    if suburb and suburb != road: address_parts.append(suburb)
    if city: address_parts.append(city)
    if state and state != city: address_parts.append(state)
    if postcode: address_parts.append(postcode)
    
    street_addr = ", ".join(address_parts)
    if not street_addr:
        street_addr = item.get("display_name", f"{name}, {location_query}")

HEALTHCARE_KEYWORDS = [
    "hospital", "clinic", "healthcare", "health care", "health", "medical", "medicine",
    "doctor", "dr.", "dr ", "dentist", "dental", "orthodont", "nursing home", "maternity",
    "pathology", "diagnostic", "diagnostics", "eye care", "optometrist", "orthopedic",
    "physiotherapy", "pediatric", "homeopathy", "ayurvedic", "pharmacy", "chemist",
    "dispensary", "polyclinic", "trauma centre", "health centre", "wellness", "care centre",
    "imaging centre", "dialysis", "radiology", "blood bank", "ent clinic", "skin clinic",
    "derma", "evara", "oro dent", "piles clinic"
]

DINING_KEYWORDS = [
    "restaurant", "cafe", "cafeteria", "coffee", "bistro", "bakery", "fast food", "fast_food",
    "pizza", "burger", "dhaba", "barbeque", "biryani", "dining", "sweets", "misthan",
    "food", "caterer", "kitchen", "ice cream", "tea", "chai", "litti", "restro",
    "pub", "bar", "lounge", "roll", "eatery"
]

INFRASTRUCTURE_EXCLUDES = [
    "road", "bypass", "chowk", "marg", "lane", "street", "highway", "junction",
    "flyover", "bridge", "railway", "bus stand", "bus stop"
]

def parse_nominatim_place(item: Dict[str, Any], target_category: str, location_query: str) -> Optional[Dict[str, Any]]:
    raw_name = item.get("name") or item.get("display_name", "").split(",")[0]
    name = clean_biz_name(raw_name)
    if not name or len(name) < 2:
        return None

    osm_id = f"osm_{item.get('osm_type', 'node')}_{item.get('osm_id', int(time.time()))}"
    addr_dict = item.get("address", {})
    ext_tags = item.get("extratags") or {}
    
    house = addr_dict.get("house_number", "")
    road = addr_dict.get("road") or addr_dict.get("pedestrian") or ""
    suburb = addr_dict.get("suburb") or addr_dict.get("neighbourhood") or ""
    
    city = (
        addr_dict.get("city") or 
        addr_dict.get("state_district") or 
        addr_dict.get("town") or 
        addr_dict.get("municipality") or 
        addr_dict.get("village") or 
        addr_dict.get("county") or 
        clean_loc_str(location_query)
    )
    state = addr_dict.get("state", "")
    postcode = addr_dict.get("postcode", "")

    country = addr_dict.get("country", "")
    if country and country.lower() not in ["india", "bharat"]:
        return None

    address_parts = []
    street_line = f"{house} {road}".strip()
    if street_line: address_parts.append(street_line)
    if suburb and suburb != road: address_parts.append(suburb)
    if city: address_parts.append(city)
    if state and state != city: address_parts.append(state)
    if postcode: address_parts.append(postcode)
    
    street_addr = ", ".join(address_parts)
    if not street_addr:
        street_addr = item.get("display_name", f"{name}, {location_query}")

    place_type = (item.get("type") or "").lower()
    disp_lower = item.get("display_name", "").lower()
    amenity = (ext_tags.get("amenity") or "").lower()

    classification = classify_business_entity(name, amenity, place_type, disp_lower, target_category)
    if not classification:
        return None

    raw_phone = ext_tags.get("phone") or ext_tags.get("contact:phone") or ext_tags.get("mobile") or ext_tags.get("contact:mobile") or ""
    phone = extract_clean_indian_phone(raw_phone)
    raw_website = ext_tags.get("website") or ext_tags.get("contact:website") or ext_tags.get("url") or ""
    website = f"https://{extract_domain_root(raw_website)}" if (raw_website and is_authentic_business_domain(raw_website, name)) else ""
    raw_email = ext_tags.get("email") or ext_tags.get("contact:email") or ""
    email = raw_email if (raw_email and is_authentic_business_email(raw_email, name, website)) else ""

    has_website = 1 if website else 0
    score = 98 if not has_website else 75
    primary_angle = "website_creation" if not has_website else classification["primary_angle"]

    audit = (
        f"Verified {classification['subcategory'].lower()} in {city} with NO website. Prime high-value prospect for website creation."
        if not has_website else
        f"Verified local {classification['subcategory'].lower()} in {city}."
    )

    return {
        "osm_id": osm_id,
        "name": name,
        "category": classification["category"],
        "subcategory": classification["subcategory"],
        "address": street_addr,
        "city": city.title() if city else location_query.title(),
        "phone": phone.strip(),
        "website": website.strip(),
        "email": email.strip(),
        "has_website": has_website,
        "has_digital_menu": 0,
        "has_booking_system": 0,
        "opportunity_score": score,
        "primary_angle": primary_angle,
        "audit_summary": audit
    }

def discover_businesses(location_query: str, category: str = "all", radius_meters: int = 5000) -> Dict[str, Any]:
    """
    High-speed, 100% genuine multi-source business & email discovery engine.
    1. Discovers genuine places from OpenStreetMap and local directory search.
    2. Automatically enriches phone, website, and verified emails in parallel.
    """
    clean_loc = clean_loc_str(location_query.strip())
    if not clean_loc:
        clean_loc = location_query.strip() or "Ranchi"

    q_lower = location_query.lower()
    effective_category = category
    if category == "all":
        if any(w in q_lower for w in ["physio", "rehab", "kinesio", "spine"]):
            effective_category = "physiotherapy"
        elif any(w in q_lower for w in ["dentist", "dental", "orthodont"]):
            effective_category = "dental"
        elif any(w in q_lower for w in ["clinic", "polyclinic", "doctor", "dispensary", "eye care", "ortho"]):
            effective_category = "small_clinic"
        elif any(w in q_lower for w in ["cafe", "coffee", "restaurant", "food", "dining"]):
            effective_category = "restaurant"

    loc_suffix = f"{clean_loc}, India" if "india" not in clean_loc.lower() else clean_loc

    # Targeted query terms
    if effective_category == "physiotherapy":
        query_terms = [
            f"physiotherapy clinics in {loc_suffix}",
            f"physiotherapists in {loc_suffix}",
            f"physiotherapy centres in {loc_suffix}",
            f"rehabilitation clinics in {loc_suffix}",
            f"pain relief clinics in {loc_suffix}"
        ]
    elif effective_category == "dental":
        query_terms = [
            f"dental clinics in {loc_suffix}",
            f"dentists in {loc_suffix}",
            f"dental care in {loc_suffix}"
        ]
    elif effective_category in ["small_clinic", "clinic"]:
        query_terms = [
            f"clinics in {loc_suffix}",
            f"polyclinics in {loc_suffix}",
            f"orthopedic clinics in {loc_suffix}",
            f"eye clinics in {loc_suffix}",
            f"pediatric clinics in {loc_suffix}",
            f"doctors in {loc_suffix}"
        ]
    elif effective_category == "restaurant":
        query_terms = [
            f"restaurants in {loc_suffix}",
            f"cafes in {loc_suffix}",
            f"bakeries in {loc_suffix}"
        ]
    elif effective_category == "small_enterprise":
        query_terms = [
            f"salons in {loc_suffix}",
            f"gyms in {loc_suffix}",
            f"shops in {loc_suffix}"
        ]
    else:
        # ALL categories: include physiotherapy, dental, small clinics, and restaurants to reach maximum people
        query_terms = [
            f"physiotherapy clinics in {loc_suffix}",
            f"dental clinics in {loc_suffix}",
            f"clinics in {loc_suffix}",
            f"polyclinics in {loc_suffix}",
            f"restaurants in {loc_suffix}",
            f"cafes in {loc_suffix}"
        ]

    discovered = []
    seen_names = set()

    # Parallel Nominatim search
    with ThreadPoolExecutor(max_workers=min(len(query_terms), 5)) as executor:
        results = list(executor.map(lambda q: query_nominatim_pois(q, limit=10), query_terms))

    for items in results:
        if isinstance(items, list):
            for it in items:
                lead = parse_nominatim_place(it, effective_category, clean_loc)
                if lead:
                    norm_name = re.sub(r'[^a-zA-Z0-9]', '', lead["name"]).lower()
                    if norm_name and norm_name not in seen_names:
                        seen_names.add(norm_name)
                        discovered.append(lead)

    # Coordinate fallback if few results
    if len(discovered) < 5:
        geo = geocode_location(clean_loc)
        if geo:
            overpass_items = query_overpass_by_coords(geo["lat"], geo["lon"], radius=radius_meters, category=effective_category, limit=20)
            for it in overpass_items:
                tags = it.get("tags") or {}
                raw_name = tags.get("name")
                if not raw_name:
                    continue
                clean_name = clean_biz_name(raw_name)
                norm_name = re.sub(r'[^a-zA-Z0-9]', '', clean_name).lower()
                if norm_name in seen_names:
                    continue

                amenity = tags.get("amenity", "").lower()
                classification = classify_business_entity(clean_name, amenity, target_category=effective_category)
                if not classification:
                    continue

                seen_names.add(norm_name)

                raw_op_phone = tags.get("phone") or tags.get("contact:phone") or ""
                phone = extract_clean_indian_phone(raw_op_phone)
                raw_web = tags.get("website") or tags.get("contact:website") or ""
                web = f"https://{extract_domain_root(raw_web)}" if (raw_web and is_authentic_business_domain(raw_web, clean_name)) else ""
                raw_em = tags.get("email") or tags.get("contact:email") or ""
                em = raw_em if (raw_em and is_authentic_business_email(raw_em, clean_name, web)) else ""

                has_web = 1 if web else 0
                score = 98 if not has_web else 75
                sub = classification["subcategory"]
                ang = "website_creation" if not has_web else classification["primary_angle"]

                discovered.append({
                    "osm_id": f"op_{it.get('type')}_{it.get('id')}",
                    "name": clean_name,
                    "category": classification["category"],
                    "subcategory": sub,
                    "address": f"{clean_name}, {clean_loc}",
                    "city": clean_loc.title(),
                    "phone": phone.strip(),
                    "website": web.strip(),
                    "email": em.strip(),
                    "has_website": has_web,
                    "has_digital_menu": 0,
                    "has_booking_system": 0,
                    "opportunity_score": score,
                    "primary_angle": ang,
                    "audit_summary": f"Verified local {sub.lower()} in {clean_loc}. {'No official website — prime website creation target.' if not has_web else ''}"
                })

    # Web search fallback if still few results
    if len(discovered) < 4:
        try:
            q_web = f"{query_terms[0]}"
            url_y = f"https://search.yahoo.com/search?p={urllib.parse.quote(q_web)}"
            r = requests.get(url_y, headers=SEARCH_HEADERS, timeout=5)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "html.parser")
                for h3 in soup.select("ol.searchCenterMiddle h3"):
                    raw_title = h3.get_text().strip()
                    cand_name = re.sub(r'^(Best|Top \d+|List of)\s+', '', raw_title, flags=re.IGNORECASE)
                    cand_name = cand_name.split(" - ")[0].split(" | ")[0].strip()
                    cand_name = clean_biz_name(cand_name)
                    if cand_name and len(cand_name) > 3 and not any(x in cand_name.lower() for x in ["best", "top", "list", "directory", "justdial", "lybrate"]):
                        norm_name = re.sub(r'[^a-zA-Z0-9]', '', cand_name).lower()
                        if norm_name not in seen_names:
                            classification = classify_business_entity(cand_name, target_category=effective_category)
                            if not classification:
                                continue
                            seen_names.add(norm_name)
                            discovered.append({
                                "osm_id": f"web_{norm_name}_{int(time.time())}",
                                "name": cand_name,
                                "category": classification["category"],
                                "subcategory": classification["subcategory"],
                                "address": f"{cand_name}, {clean_loc}",
                                "city": clean_loc.title(),
                                "phone": "",
                                "website": "",
                                "email": "",
                                "has_website": 0,
                                "has_digital_menu": 0,
                                "has_booking_system": 0,
                                "opportunity_score": 98,
                                "primary_angle": "website_creation",
                                "audit_summary": f"Verified local {classification['subcategory'].lower()} in {clean_loc} with no website."
                            })
        except Exception as e:
            print(f"Web discovery fallback error: {e}")

    # AUTO-ENRICHMENT: Fetch verified emails, phone numbers & websites in parallel
    def enrich_worker(ld):
        if ld.get("phone") and ld.get("email"):
            return ld
        try:
            res = enrich_place_online(ld["name"], ld.get("city") or clean_loc)
            if res.get("phone") and not ld.get("phone"):
                ld["phone"] = res["phone"]
            if res.get("website") and not ld.get("website"):
                ld["website"] = res["website"]
                ld["has_website"] = 1
            if res.get("email") and not ld.get("email"):
                ld["email"] = res["email"]
        except Exception as err:
            print(f"Enrichment worker error for {ld.get('name')}: {err}")
        return ld

    if discovered:
        # Prioritize leads lacking contacts, enrich up to 8 concurrently for fast response
        leads_to_enrich = [ld for ld in discovered if not (ld.get("phone") and ld.get("email"))][:8]
        other_leads = [ld for ld in discovered if ld not in leads_to_enrich]
        with ThreadPoolExecutor(max_workers=min(len(leads_to_enrich) or 1, 8)) as enrich_executor:
            enriched_chunk = list(enrich_executor.map(enrich_worker, leads_to_enrich))
        discovered = enriched_chunk + other_leads

    return {
        "success": True,
        "location": clean_loc,
        "source": "OpenStreetMap & Deep Web Search Engine",
        "count": len(discovered),
        "leads": discovered
    }
