import json
import requests
from typing import Dict, Any, Optional

def generate_cold_pitch(
    business_name: str,
    category: str,
    city: str,
    website: str,
    primary_angle: str,
    sender_name: str = "Vishal Kumar Tiwari",
    sender_title: str = "Co-Founder, Zenix Services",
    sender_email: str = "zenixservices67@gmail.com",
    website_url: str = "https://zenixservices.online",
    tone: str = "friendly",
    api_key: Optional[str] = None
) -> Dict[str, str]:
    """
    Generates a personalized cold email pitch from Vishal Kumar Tiwari (Co-Founder, Zenix Services)
    tailored specifically for:
    - Restaurants / Cafes: Digital QR menu systems, contactless ordering, mobile optimization.
    - Physiotherapy & Rehab Clinics: Patient booking, therapy showcase, pain relief & posture care.
    - Dental Clinics: Modern patient-generating websites, 24/7 online appointment booking.
    - Small & General Clinics: Doctor profiles, OPD hours, online consultation scheduling.
    - Small Enterprises: High-converting websites for businesses with no web presence.
    
    Always includes link to zenixservices.online and mentions relevant client portfolio experience.
    """
    
    # Try LLM if Gemini API key provided
    if api_key and api_key.strip():
        try:
            llm_result = generate_pitch_with_gemini(
                api_key=api_key.strip(),
                business_name=business_name,
                category=category,
                city=city,
                website=website,
                primary_angle=primary_angle,
                sender_name=sender_name,
                sender_title=sender_title,
                sender_email=sender_email,
                website_url=website_url,
                tone=tone
            )
            if llm_result:
                return llm_result
        except Exception as e:
            print(f"Gemini generation fallback: {e}")

    # Built-in High-Converting Smart AI Copy Engine
    cat_lower = category.lower()
    is_restaurant = any(w in cat_lower for w in ["restaurant", "cafe", "coffee", "bistro", "bakery", "bar", "dining", "pizza", "food"])
    is_physio = any(w in cat_lower for w in ["physio", "rehab", "kinesio", "chiropractic", "spine", "physical therapy"])
    is_dental = not is_physio and any(w in cat_lower for w in ["dental", "dentist", "orthodont", "teeth", "tooth", "oral"])
    is_small_clinic = not is_physio and not is_dental and any(w in cat_lower for w in ["clinic", "doctor", "health", "medical", "hospital", "eye", "skin", "ortho", "poly", "pediatric", "homeopathy", "ayurvedic", "dispensary"])
    has_site = bool(website)

    signature = f"""{sender_name}
{sender_title}
Website: {website_url}
Email: {sender_email}"""

    if is_restaurant:
        rest_gap_direct = "you do not currently have a dedicated mobile-friendly site with an interactive digital menu" if not has_site else "your website could benefit from a dedicated contactless QR menu and zero-commission direct ordering system"
        rest_gap_friendly = "you do not currently have an official website set up" if not has_site else "your website could be upgraded with a modern interactive QR menu and mobile ordering"

        if tone == "direct":
            subject = f"Quick question regarding {business_name}'s online menu & ordering"
            body = f"""Hi {business_name} team,

I came across {business_name} while searching for great dining spots in {city}.

I noticed {rest_gap_direct}.

At Zenix Services, we specialize in building sleek, modern websites and lightning-fast digital menu systems for local cafes and restaurants. It helps you:
• Showcase daily specials & mouthwatering food photos
• Allow guests to scan a table QR code and browse your menu instantly on their phone
• Capture direct takeaway and delivery orders without giving away 20-30% in third-party aggregator commissions

We have worked with multiple cafes and restaurants to launch interactive digital QR menus and direct ordering systems, as you can see on our website: {website_url}

I already put together a quick interactive draft preview of what a modern site & menu for {business_name} could look like.

Would you be open to seeing a 60-second preview or screenshot of it this week?

Best regards,
{signature}"""

        elif tone == "creative_mockup":
            subject = f"Idea for {business_name}'s new digital menu & website (free preview)"
            body = f"""Hello {business_name} team,

My name is {sender_name}, Co-Founder of Zenix Services. I love finding standout cafes and dining spots in {city}.

I was looking at {business_name}'s digital presence and was inspired to sketch out a modern interactive digital menu & website prototype for you. 

Many restaurants and cafes are switching from bulky paper menus or clunky PDF files to dynamic mobile QR menus. Customers love browsing appetizing dish pictures, and it makes updating prices or sold-out items take just 5 seconds from your phone.

We have worked with multiple cafes and restaurants to modernize their dining experiences, as you can see on our website: {website_url}

I would love to share the free preview mockup my team at Zenix Services created for {business_name} — completely complimentary, no strings attached.

Would it be okay if I sent over a link or quick screenshot?

Warm regards,
{signature}"""

        else:  # friendly default
            subject = f"Website & Digital Menu concept for {business_name} 🍽️"
            body = f"""Hi there,

I hope you are having a wonderful week at {business_name}!

I was browsing local favorites in {city} and love the concept of {business_name}. I noticed {rest_gap_friendly}.

In today's dining scene, over 80% of guests check a restaurant's food menu on their smartphone before deciding where to eat. 

At Zenix Services, we help local restaurants and cafes create beautiful, mobile-first websites with:
1. Instant QR Code digital menus that look great on any phone
2. One-tap table reservations & Google Maps integration
3. Zero-commission online ordering so you keep 100% of your food sales

We have worked with multiple cafes and restaurants to launch high-converting digital menus and direct ordering, as you can see on our website: {website_url}

I would love to put together a complimentary mockup of your new website and menu system so you can see it in action.

Could I send that over for you to take a quick look?

Best wishes,
{signature}"""

    elif is_physio:
        physio_gap_direct = "you do not currently have a modern mobile website for patients in pain to find and book therapy sessions" if not has_site else "your current site does not offer instant 24/7 online consultation booking"
        physio_gap_friendly = "there is currently no official website linked to your physiotherapy practice" if not has_site else "your clinic could be upgraded with a modern, patient-friendly booking and rehab showcase experience"

        if tone == "direct":
            subject = f"Patient acquisition & 24/7 consultation booking for {business_name}"
            body = f"""Hi Dr. and team at {business_name},

I hope your clinic is having a productive week in {city}.

I was researching top physiotherapy and rehabilitation providers in {city} and noticed {physio_gap_direct}.

When patients suffer from severe back pain, joint stiffness, or sports injuries, over 75% search on their smartphone and want to book a consultation immediately without waiting for phone callbacks.

At Zenix Services, we build high-converting websites specifically for physiotherapy clinics and rehab centres to:
• Fill therapy and consultation slots automatically 24/7
• Clearly showcase specialized treatments (spine rehab, post-surgery recovery, sports therapy, pain relief)
• Free your front desk from routine scheduling calls while boosting Google Maps visibility

We have worked with multiple physiotherapy clinics and healthcare practices to modernize patient intake, as you can see on our website: {website_url}

I have already put together a sample design preview tailored for {business_name}. Would you be open to taking a quick peek?

Best regards,
{signature}"""

        elif tone == "creative_mockup":
            subject = f"Patient booking portal & website concept for {business_name}"
            body = f"""Hello Dr. and team at {business_name},

My name is {sender_name}, Co-Founder of Zenix Services.

I was looking at physiotherapy and pain rehabilitation services in {city} and noticed {physio_gap_friendly}.

Our design team put together a quick prototype concept demonstrating how {business_name} could allow patients to schedule therapy sessions online in 30 seconds, view therapy packages, and review doctor credentials.

We have worked with multiple physiotherapy clinics and healthcare providers to modernize patient booking and online reputation, as you can see on our website: {website_url}

I would love to share a free preview mockup of this patient intake portal with your clinic — zero obligation.

Would you be open to checking out a quick 60-second preview this week?

Warm regards,
{signature}"""

        else:  # friendly default
            subject = f"Modern patient website & appointment booking for {business_name} 🩺🏃"
            body = f"""Hello Dr. and team at {business_name},

I hope you are having a great week!

I came across {business_name} while researching top physiotherapy and pain relief clinics in {city}.

I noticed {physio_gap_friendly}.

Most patients seeking physiotherapy look for three critical things on their phone before visiting:
1. Clear details on treatment specialties (spine care, sports rehab, post-op physiotherapy, joint pain)
2. The ability to book an appointment or consultation online 24/7
3. Clear clinic location, doctor credentials, and direct WhatsApp contact

At Zenix Services, we design sleek, trustworthy websites for physiotherapy clinics that make patient onboarding effortless and keep therapy calendars consistently full.

We have worked with multiple physiotherapy clinics and healthcare practices to streamline patient booking, as you can see on our website: {website_url}

I would love to send you a complimentary preview of how a new website & booking portal for {business_name} would look.

Could I send that over for you to take a quick look?

Kind regards,
{signature}"""

    elif is_dental:
        dental_gap_direct = "you do not have an active website for new patients to find and book you" if not has_site else "your current site does not offer instant 24/7 online appointment booking"
        dental_gap_friendly = "there is currently no official website linked to your practice" if not has_site else "your website could be upgraded with a modern, patient-friendly booking experience"

        if tone == "direct":
            subject = f"Patient acquisition & 24/7 online booking for {business_name}"
            body = f"""Hi {business_name} team,

I hope your practice is having a productive week.

I was looking up dental and healthcare practices in {city} and noticed {dental_gap_direct}.

When patients search for care in {city} after hours, over 65% choose whichever clinic lets them book an appointment directly from their smartphone.

At Zenix Services, we build clean, trustworthy dental websites with built-in online scheduling that helps clinics:
• Fill empty calendar slots automatically 24/7
• Free up your front-desk staff from answering routine booking calls
• Rank higher on Google Maps for local searches like 'dentist near me'

We have worked with multiple dental clinics and healthcare practices to streamline patient booking and modern web design, as you can see on our website: {website_url}

I have already prepared a sample design tailored for {business_name}. Would you be open to taking a quick peek?

Best regards,
{signature}"""

        elif tone == "creative_mockup":
            subject = f"Patient booking portal & website concept for {business_name}"
            body = f"""Hello Dr. and team at {business_name},

My name is {sender_name}, Co-Founder of Zenix Services.

I was researching top dental providers in {city} and noticed {dental_gap_friendly}. 

Our design team put together a quick prototype concept demonstrating how {business_name} could allow new and existing patients to schedule consultations online in 30 seconds, view insurance details, and review doctor credentials.

We have worked with multiple dental clinics to modernize their patient intake and web presence, as you can see on our website: {website_url}

I would love to share a free preview mockup of this patient booking portal with your practice.

Would you be open to taking a quick look this week?

Warm regards,
{signature}"""

        else:  # friendly default
            subject = f"Modern patient website & appointment booking for {business_name} 🦷"
            body = f"""Hello Dr. and team at {business_name},

I hope you are having a great day.

I came across {business_name} while researching top dental and healthcare providers in {city}.

I noticed {dental_gap_friendly}. 

Most prospective patients today look for three things when choosing a dentist or clinic:
1. A fast, modern mobile site with clear treatment information & patient reviews
2. The ability to schedule an appointment online 24/7 directly from their phone
3. Direct insurance acceptance details and easy clinic directions

At Zenix Services, we design high-converting websites for dental clinics that make patient onboarding effortless and boost new monthly patient appointments.

We have worked with multiple dental clinics and healthcare practices to streamline patient booking and web design, as you can see on our website: {website_url}

I would love to send you a complimentary preview of how a new site & booking portal for {business_name} would look.

Would you be open to taking a quick look this week?

Kind regards,
{signature}"""

    elif is_small_clinic:
        clinic_gap_direct = "you do not currently have a dedicated website for local patients to check doctor OPD hours and book consultations" if not has_site else "your website could be upgraded with an automated online appointment scheduling system"
        clinic_gap_friendly = "there is currently no official website set up for your practice" if not has_site else "your clinic website could be modernized with instant appointment booking and doctor profiles"

        if tone == "direct":
            subject = f"Streamlining patient appointments & website presence for {business_name}"
            body = f"""Hi Dr. and team at {business_name},

I hope your clinic is having a great week in {city}.

I came across {business_name} while looking up medical and healthcare clinics in {city}.

I noticed {clinic_gap_direct}.

Today, when patients and families look for trusted local doctors in {city}, having an easily accessible mobile site with clear consulting hours and online appointment requests significantly boosts patient attendance.

At Zenix Services, we specialize in building fast, patient-friendly websites for clinics and doctor chambers that:
• Highlight doctor credentials, consulting timings & specialty services
• Allow patients to request appointments online or connect instantly on WhatsApp
• Establish a strong, trusted presence on Google Maps

We have worked with multiple clinics and healthcare providers across India, as you can see on our website: {website_url}

I put together a quick draft concept of how {business_name}'s modern clinic portal could look. Would you be open to seeing a 60-second preview?

Best regards,
{signature}"""

        elif tone == "creative_mockup":
            subject = f"New patient portal & website draft for {business_name} (free preview)"
            body = f"""Hello Dr. and team at {business_name},

My name is {sender_name}, Co-Founder of Zenix Services.

I was researching local healthcare practices in {city} and was inspired to sketch out a modern clinic website concept for {business_name}.

Our prototype allows patients to view doctor schedules, browse specialty treatments, and submit appointment requests right from their phone without calling your front desk multiple times.

We have worked with multiple medical clinics to modernize their patient communication, as you can see on our website: {website_url}

I would love to share this free mockup with your clinic — zero strings attached.

Would it be okay if I sent over a quick link or screenshot?

Warm regards,
{signature}"""

        else:  # friendly default
            subject = f"Modern patient website & appointment booking for {business_name} 🏥"
            body = f"""Hello Dr. and team at {business_name},

I hope you are having a wonderful week!

I came across {business_name} while researching healthcare practices in {city}.

I noticed {clinic_gap_friendly}.

In today's digital era, patients prefer visiting clinics where they can verify consulting hours, doctor qualifications, and book appointments directly from their smartphone.

At Zenix Services, we help small clinics and doctor practices build clean, trustworthy websites that:
1. Clearly showcase doctor profiles, OPD schedules, and treatment services
2. Provide seamless online appointment requests and WhatsApp integration
3. Help your clinic rank higher when local patients search for care in {city}

We have worked with multiple clinics and healthcare practices to streamline patient booking, as you can see on our website: {website_url}

I would love to send you a complimentary design preview of what a modern site for {business_name} could look like.

Could I share that with you for a quick look?

Best wishes,
{signature}"""

    else:
        # Small enterprise / general local business
        if not has_site:
            subject = f"Website concept for {business_name} in {city}"
            body = f"""Hi {business_name} team,

I was looking for {category.lower()} in {city} and noticed that {business_name} does not seem to have an official website up yet.

Right now, when potential customers search for services like yours on Google or Apple Maps, they expect to see a fast, professional website with your services, hours, and direct contact options.

At Zenix Services, we help local businesses in {city} get modern, high-converting websites up and running without any headache or technical jargon.

We have worked with multiple local businesses to design high-converting websites and grow their online presence, as you can see on our website: {website_url}

I actually put together a free draft mockup of what {business_name}'s new website could look like.

Would you mind if I shared a quick screenshot or link with you?

Best regards,
{signature}"""
        else:
            subject = f"Modern website upgrade & client growth for {business_name}"
            body = f"""Hi {business_name} team,

I came across {business_name} online and wanted to reach out regarding your current digital presence.

Your business does great work in {city}, but your website could be generating significantly more customer inquiries if optimized with modern mobile design, faster load speeds, and clear calls to action.

At Zenix Services, we specialize in modernizing websites for growing enterprises to turn casual website visitors into paying customers.

We have worked with multiple businesses to build high-converting web experiences, as you can see on our website: {website_url}

I have put together a few quick observations and a sample redesign idea for {business_name}. 

Would you be open to reviewing a quick preview?

Warm regards,
{signature}"""

    return {
        "subject": subject,
        "body": body
    }

def generate_pitch_with_gemini(
    api_key: str,
    business_name: str,
    category: str,
    city: str,
    website: str,
    primary_angle: str,
    sender_name: str,
    sender_title: str,
    sender_email: str,
    website_url: str,
    tone: str
) -> Optional[Dict[str, str]]:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    prompt = f"""You are an elite B2B cold outreach copywriter for Zenix Services. Write a non-spammy, highly personalized, polite, and persuasive cold email to a local small business owner.

Sender Details:
- Name: {sender_name}
- Title: {sender_title}
- Company: Zenix Services
- Website: {website_url}
- Email: {sender_email}

Target Business:
- Name: {business_name}
- Category: {category}
- City: {city}
- Website: {website if website else 'NO WEBSITE (Prime opportunity to pitch their very first modern site)'}
- Angle: {primary_angle}
- Desired Tone: {tone}

CRITICAL REQUIREMENTS:
1. If the business is a Cafe / Restaurant: focus on interactive mobile QR digital menus, food photography showcase, and zero-commission direct ordering.
2. If the business is a Physiotherapy / Rehab Clinic: focus on 24/7 patient consultation booking, pain relief & sports rehab therapy showcase, therapist credentials, and recovery testimonials (DO NOT mention dental or teeth!).
3. If the business is a Dental Clinic: focus on 24/7 automated online patient booking, dental treatment showcase, and filling chair slots.
4. If the business is a Small / General Healthcare Clinic (polyclinic, eye, skin, orthopedic, doctor chamber): focus on doctor credentials, consulting hours, online appointment requests, and patient trust.
5. In the body of the email, you MUST include social proof stating:
   "We have worked with multiple physiotherapy clinics [or dental clinics / healthcare practices / cafes / restaurants] as you can see on our website: {website_url}"
6. End with sender's full signature:
   {sender_name}
   {sender_title}
   Website: {website_url}
   Email: {sender_email}

Respond ONLY in valid JSON format with exactly two keys: "subject" and "body".
Do not wrap with backticks other than raw JSON.
"""
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 600}
    }
    
    resp = requests.post(url, headers=headers, json=payload, timeout=12)
    if resp.status_code == 200:
        data = resp.json()
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        if raw_text.startswith("json")[-1].split(""):
            raw_text = raw_text.split("")[0].strip()
        parsed = json.loads(raw_text)
        return {"subject": parsed.get("subject", ""), "body": parsed.get("body", "")}
    return None
