# ⚡ LocalReach AI — Lead Discovery & Cold Outreach Agent

LocalReach AI is an autonomous, production-ready AI agent built specifically to:
1. **Discover Nearby Businesses**: Automatically scan any city or neighborhood for local **restaurants, cafes, dental clinics, healthcare practices, and small enterprises**.
2. **Audit Digital Presence**: Check whether each business has a website, whether it is mobile-responsive, and whether it has a digital menu or online booking system.
3. **Calculate Opportunity Scores**: Identify high-converting prospects (e.g., businesses with **no website** or **restaurants lacking an interactive QR digital menu**).
4. **Generate Hyper-Personalized Outreach**: AI creates compelling, non-spammy cold emails tailored specifically to their niche offering:
   - **Restaurants / Cafes**: Website Creation + Zero-Commission QR Code Digital Menu & Online Ordering.
   - **Dental Clinics**: Modern Patient Acquisition Website + 24/7 Online Appointment Booking Portal.
   - **Small Enterprises**: First-ever modern responsive website to convert local Google searchers into clients.
5. **Direct Email Outreach**: Send emails directly via SMTP (Gmail App Passwords, Outlook, Custom SMTP) with built-in anti-spam safety delays and a **Safe Simulation / Dry-Run Mode** enabled by default.

---

## 🚀 Quick Start

### 1. Launch the Agent Dashboard
In the project directory:
```bash
./.venv/bin/python main.py
```
Open your browser and navigate to:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 🛠️ Features & Workflow

### 1. Discovery Studio
- Search by any **City, Locality, or Postal Code** (e.g. *"Downtown Austin, Texas"*, *"London"*, *"Miami, FL"*).
- Filter by target category:
  - 🍽️ **Restaurants, Cafes & Bakeries**
  - 🦷 **Dental & Healthcare Clinics**
  - 💼 **Small Enterprises & Salons**
- Adjustable scan radius (3km to 20km).
- Includes one-click instant demo leads for immediate testing.

### 2. Leads & Digital Audit Matrix
- Real-time table view showing discovered businesses, address, contact phone, website status badge, and email.
- **Opportunity Meter (0-100%)**:
  - `95%` = No website found (Prime prospect for first site creation).
  - `88%` = Restaurant website without modern digital menu / ordering.
  - `85%` = Dental clinic website without 24/7 online booking.
- Inline email editor to easily verify or add contact emails.
- **Deep Audit Button (`🔎 Audit`)**: Crawls business homepage & contact pages to extract emails and verify responsive design.
- Export leads to **CSV** at any time.

### 3. AI Pitch Studio
- Live split-view email composer.
- Choose tone:
  - 🤝 **Friendly & Helpful**: Warm, relationship-focused.
  - ⚡ **Direct & Punchy**: Under 100 words, high conversion rate for busy owners.
  - 🎨 **Free Mockup Pitch**: Leads with an irresistible offer of a free draft preview mockup.
- One-click copy or direct dispatch.

### 4. Campaign Dispatcher & Console
- **Simulation Mode (Active by default)**: Safely simulates email dispatching and records logs without sending real emails.
- **Live SMTP Mode**: Toggle on when ready to send live emails.
- Anti-spam jitter delay control (3 to 10 seconds between emails) to protect domain reputation.
- Live real-time terminal log showing dispatch status, timestamps, and error diagnostics.

### 5. Settings & SMTP Setup
- **Sender Profile**: Configure your name and sender email.
- **Gmail Setup**:
  1. Go to your Google Account -> Security -> 2-Step Verification -> **App Passwords**.
  2. Generate a 16-character App Password (e.g. `abcd efgh ijkl mnop`).
  3. Enter host `smtp.gmail.com`, port `587`, your Gmail address, and the App Password.
  4. Click **⚡ Test Connection** in the settings modal to verify instantly!
- **Optional Gemini API Key**: Can be added for custom creative prompts, or leave empty to use the built-in AI copywriting engine at zero cost.

---

## 📂 Project Architecture
```
.
├── config.py                 # Core configurations & defaults
├── server.py                 # FastAPI REST API & static server
├── main.py                   # Application entrypoint
├── agent_core/
│   ├── discovery.py          # Geocoding & OpenStreetMap Overpass scanner
│   ├── scraper.py            # Deep web scraper & presence auditor
│   ├── ai_generator.py       # Tailored email copywriter (Built-in + LLM)
│   ├── mailer.py             # SMTP dispatcher with simulation mode
│   └── storage.py            # SQLite database manager
├── data/
│   └── localreach.db         # Persistent leads, settings, and logs
└── static/
    ├── index.html            # UI dashboard structure
    ├── style.css             # Glassmorphism dark theme & animations
    └── app.js                # Frontend state & async handlers
```
