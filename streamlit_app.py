import os
import streamlit as st
import pandas as pd
from typing import Dict, Any

from config import DEFAULT_SETTINGS
from agent_core.storage import (
    init_db, get_leads, get_lead_by_id, save_leads, update_lead,
    get_all_settings, update_setting, get_email_logs
)
from agent_core.discovery import discover_businesses, enrich_place_online
from agent_core.ai_generator import generate_cold_pitch
from agent_core.mailer import send_email_message, test_smtp_connection

# Initialize SQLite database
init_db()

st.set_page_config(
    page_title="Zenix Reach AI | Local Lead Discovery & Outreach",
    page_icon="🚀",
    layout="wide"
)

# Custom Styling for Streamlit
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #94a3b8;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    .metric-badge {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# App Header
st.markdown('<div class="main-header">🚀 Zenix Reach AI Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Automated local business discovery, smart website audit, and personalized AI cold outreach engine for Vishal Kumar Tiwari (Zenix Services).</div>', unsafe_allow_html=True)

# Sidebar: Outreach Settings & SMTP Configuration
st.sidebar.header("⚙️ Outreach Settings")

settings = get_all_settings()

sender_name = st.sidebar.text_input("Sender Name", value=settings.get("sender_name", "Vishal Kumar Tiwari"))
sender_title = st.sidebar.text_input("Title", value=settings.get("sender_title", "Co-Founder, Zenix Services"))
sender_email = st.sidebar.text_input("Sender Email", value=settings.get("sender_email", "zenixservices67@gmail.com"))
website_url = st.sidebar.text_input("Portfolio Website", value=settings.get("website_url", "https://zenixservices.online"))
smtp_pass = st.sidebar.text_input("Gmail App Password", value=settings.get("smtp_pass", ""), type="password", help="16-character Google App Password from myaccount.google.com/apppasswords")
gemini_api_key = st.sidebar.text_input("Gemini API Key (Optional)", value=settings.get("gemini_api_key", ""), type="password")

dry_run = st.sidebar.checkbox("Simulation / Dry Run Mode (Safe)", value=bool(settings.get("dry_run_mode", True)))

if st.sidebar.button("💾 Save Settings", use_container_width=True):
    update_setting("sender_name", sender_name)
    update_setting("sender_title", sender_title)
    update_setting("sender_email", sender_email)
    update_setting("smtp_user", sender_email)
    update_setting("website_url", website_url)
    update_setting("smtp_pass", smtp_pass)
    update_setting("gemini_api_key", gemini_api_key)
    update_setting("dry_run_mode", dry_run)
    st.sidebar.success("Settings saved successfully!")

if st.sidebar.button("🔌 Test Gmail SMTP", use_container_width=True):
    if not smtp_pass.strip():
        st.sidebar.warning("Enter Gmail App Password first.")
    else:
        test_settings = dict(settings)
        test_settings.update({
            "smtp_user": sender_email,
            "smtp_pass": smtp_pass,
            "sender_email": sender_email
        })
        res = test_smtp_connection(test_settings)
        if res.get("success"):
            st.sidebar.success("✅ Gmail SMTP Connected!")
        else:
            st.sidebar.error(f"❌ Connection Failed: {res.get('message')}")

# Navigation Tabs
tab_discover, tab_leads, tab_outreach, tab_logs = st.tabs([
    "📍 1. Discover Businesses",
    "📋 2. Leads Pipeline",
    "✍️ 3. AI Pitch & Send",
    "📊 4. Email Activity Logs"
])

# ----------------- TAB 1: DISCOVER BUSINESSES -----------------
with tab_discover:
    st.subheader("🔍 Discover Local Small Businesses & Clinics")
    col1, col2, col3 = st.columns([3, 2, 1])

    with col1:
        location_input = st.text_input("City or Locality (India)", value="Ranchi", placeholder="e.g. Ranchi, Patna, Delhi, Pune")
    with col2:
        category_choice = st.selectbox("Target Niche", [
            ("⚡ All Categories", "all"),
            ("🏃‍♂️ Physiotherapy & Rehab Clinics", "physiotherapy"),
            ("🦷 Dental Clinics", "dental"),
            ("🏥 Small & General Healthcare Clinics", "small_clinic"),
            ("🍽️ Restaurants & Cafes", "restaurant"),
            ("💼 Small Enterprises & Salons", "small_enterprise")
        ], format_func=lambda x: x[0])
    with col3:
        st.write("")
        st.write("")
        discover_clicked = st.button("🚀 Discover Leads", type="primary", use_container_width=True)

    if discover_clicked:
        if not location_input.strip():
            st.warning("Please enter a city or locality name.")
        else:
            with st.spinner(f"Scanning OpenStreetMap & deep web for {category_choice[0]} in {location_input}..."):
                res = discover_businesses(
                    location_query=location_input.strip(),
                    category=category_choice[1],
                    radius_meters=5000
                )
                leads_found = res.get("leads", [])
                inserted = save_leads(leads_found)
                st.success(f"✅ Discovered {len(leads_found)} businesses! ({inserted} new/updated in database)")
                
                if leads_found:
                    df_preview = pd.DataFrame(leads_found)[[
                        "name", "category", "subcategory", "phone", "email", "has_website", "opportunity_score"
                    ]]
                    st.dataframe(df_preview, use_container_width=True)

# ----------------- TAB 2: LEADS PIPELINE -----------------
with tab_leads:
    st.subheader("📋 Discovered Leads Database")
    
    col_f1, col_f2, col_f3 = st.columns([2, 2, 2])
    with col_f1:
        cat_filter = st.selectbox("Filter by Category", [
            "All Categories",
            "Physiotherapy Clinic",
            "Dental Clinic",
            "Small / General Clinic",
            "Restaurant / Cafe",
            "Small Enterprise"
        ])
    with col_f2:
        status_filter = st.selectbox("Status", ["all", "discovered", "pitched", "sent", "simulated"])
    with col_f3:
        search_query = st.text_input("Search Name / Phone / Address", "")

    effective_cat = None if cat_filter == "All Categories" else cat_filter
    all_leads = get_leads(category=effective_cat, status=status_filter if status_filter != "all" else None, search=search_query if search_query.strip() else None, limit=200)

    # Metrics Summary
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Leads", len(all_leads))
    m2.metric("With Phone", len([l for l in all_leads if l.get("phone")]))
    m3.metric("With Email", len([l for l in all_leads if l.get("email")]))
    m4.metric("No Website (Prime Leads)", len([l for l in all_leads if not l.get("has_website")]))

    if all_leads:
        df_leads = pd.DataFrame(all_leads)[[
            "id", "name", "category", "subcategory", "city", "phone", "email", "opportunity_score", "status"
        ]]
        st.dataframe(df_leads, use_container_width=True)
    else:
        st.info("No leads found matching current filter. Run a discovery in Tab 1!")

# ----------------- TAB 3: AI PITCH & SEND -----------------
with tab_outreach:
    st.subheader("✍️ Generate Personalized AI Cold Pitch & Send Outreach")
    
    leads_list = get_leads(limit=150)
    if not leads_list:
        st.warning("No leads available yet. Please run discovery in Tab 1 first.")
    else:
        lead_options = {f"#{l['id']} - {l['name']} ({l.get('category')})": l for l in leads_list}
        selected_label = st.selectbox("Select Target Business", list(lead_options.keys()))
        selected_lead = lead_options[selected_label]

        col_p1, col_p2 = st.columns([1, 1])

        with col_p1:
            st.markdown(f"**Business:** {selected_lead['name']}")
            st.markdown(f"**Category:** `{selected_lead['category']}` | Sub: `{selected_lead.get('subcategory', 'General')}`")
            st.markdown(f"**Location:** {selected_lead.get('address', selected_lead.get('city'))}")
            st.markdown(f"**Phone:** {selected_lead.get('phone') or 'Not found'}")
            st.markdown(f"**Website:** {selected_lead.get('website') or '❌ No Website (High Opportunity)'}")
            
            lead_email = st.text_input("Recipient Email", value=selected_lead.get("email", ""), placeholder="Enter business owner email")
            if lead_email != selected_lead.get("email"):
                update_lead(selected_lead["id"], {"email": lead_email.strip()})

            tone_choice = st.radio("Outreach Copy Tone", [
                ("Friendly & Welcoming (Recommended)", "friendly"),
                ("Direct & ROI-Focused", "direct"),
                ("Complimentary Prototype Mockup", "creative_mockup")
            ], format_func=lambda x: x[0])

            if st.button("🤖 Generate Personalized Pitch", type="primary", use_container_width=True):
                with st.spinner("Generating tailored pitch from Vishal Kumar Tiwari (Zenix Services)..."):
                    pitch = generate_cold_pitch(
                        business_name=selected_lead["name"],
                        category=selected_lead["category"],
                        city=selected_lead.get("city") or "your city",
                        website=selected_lead.get("website", ""),
                        primary_angle=selected_lead.get("primary_angle", "online_booking"),
                        sender_name=settings.get("sender_name", "Vishal Kumar Tiwari"),
                        sender_title=settings.get("sender_title", "Co-Founder, Zenix Services"),
                        sender_email=settings.get("sender_email", "zenixservices67@gmail.com"),
                        website_url=settings.get("website_url", "https://zenixservices.online"),
                        tone=tone_choice[1],
                        api_key=settings.get("gemini_api_key")
                    )
                    st.session_state["pitch_subject"] = pitch["subject"]
                    st.session_state["pitch_body"] = pitch["body"]
                    update_lead(selected_lead["id"], {
                        "email_subject": pitch["subject"],
                        "email_body": pitch["body"],
                        "status": "pitched"
                    })
                    st.success("Pitch generated!")

        with col_p2:
            st.markdown("### ✉️ Email Preview & Dispatch")
            current_subject = st.text_input(
                "Subject Line",
                value=st.session_state.get("pitch_subject", selected_lead.get("email_subject", ""))
            )
            current_body = st.text_area(
                "Email Body",
                value=st.session_state.get("pitch_body", selected_lead.get("email_body", "")),
                height=280
            )

            is_sim = bool(settings.get("dry_run_mode", True))
            st.caption(f"Mode: {'🟡 SIMULATION (Dry Run)' if is_sim else '🟢 LIVE GMAIL SMTP'}")

            if st.button("🚀 Send Email Now", type="primary", use_container_width=True):
                if not lead_email.strip():
                    st.error("Please enter a valid recipient email address.")
                elif not current_subject.strip() or not current_body.strip():
                    st.error("Subject and email body cannot be empty.")
                else:
                    with st.spinner("Dispatching outreach email..."):
                        res = send_email_message(
                            to_email=lead_email.strip(),
                            business_name=selected_lead["name"],
                            subject=current_subject.strip(),
                            body=current_body.strip(),
                            smtp_settings=settings
                        )
                        if res.get("success"):
                            st.success(f"✅ Success! {res.get('message')}")
                        else:
                            st.error(f"❌ Failed: {res.get('message')}")

# ----------------- TAB 4: LOGS -----------------
with tab_logs:
    st.subheader("📊 Outreach Dispatch & Interaction Logs")
    logs = get_email_logs(limit=100)
    if logs:
        df_logs = pd.DataFrame(logs)[[
            "id", "sent_at", "business_name", "recipient_email", "subject", "status", "error_message"
        ]]
        st.dataframe(df_logs, use_container_width=True)
    else:
        st.info("No outreach emails sent yet. Generate and send your first pitch in Tab 3!")
