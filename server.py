import csv
import io
import time
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, Response
from pydantic import BaseModel

from config import BASE_DIR
from agent_core.storage import (
    init_db, get_leads, get_lead_by_id, save_leads, update_lead, delete_lead,
    clear_all_leads, get_all_settings, update_setting, log_email_sent, get_email_logs
)
from agent_core.discovery import discover_businesses, enrich_place_online
from agent_core.scraper import audit_business_website
from agent_core.ai_generator import generate_cold_pitch
from agent_core.mailer import send_email_message, test_smtp_connection

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="LocalReach AI Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db()

# Mount static folder
static_dir = BASE_DIR / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    index_file = static_dir / "index.html"
    if index_file.exists():
        resp = FileResponse(str(index_file))
        resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        resp.headers["Pragma"] = "no-cache"
        resp.headers["Expires"] = "0"
        return resp
    return HTMLResponse("<h1>LocalReach AI Agent Backend Running</h1>")

@app.api_route("/style.css", methods=["GET", "HEAD"])
async def get_root_style():
    f = static_dir / "style.css"
    if f.exists():
        return FileResponse(str(f), media_type="text/css")
    raise HTTPException(status_code=404, detail="File not found")

@app.api_route("/app.js", methods=["GET", "HEAD"])
async def get_root_app():
    f = static_dir / "app.js"
    if f.exists():
        return FileResponse(str(f), media_type="application/javascript")
    raise HTTPException(status_code=404, detail="File not found")

@app.api_route("/initial_leads.json", methods=["GET", "HEAD"])
async def get_root_initial_leads():
    f = static_dir / "initial_leads.json"
    if f.exists():
        return FileResponse(str(f), media_type="application/json")
    raise HTTPException(status_code=404, detail="File not found")

# Request Models
class DiscoverRequest(BaseModel):
    location: str
    category: str = "all"
    radius_meters: int = 5000

class LeadUpdateRequest(BaseModel):
    lead_id: int
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    email_subject: Optional[str] = None
    email_body: Optional[str] = None

class PitchGenerateRequest(BaseModel):
    lead_id: int
    tone: str = "friendly"

class BatchGenerateRequest(BaseModel):
    lead_ids: Optional[List[int]] = None
    tone: str = "friendly"

class SendEmailRequest(BaseModel):
    lead_id: int
    subject: str
    body: str

class BatchSendRequest(BaseModel):
    lead_ids: List[int]

class SettingsUpdateRequest(BaseModel):
    settings: Dict[str, Any]

class EnrichRequest(BaseModel):
    lead_id: int

class BatchEnrichRequest(BaseModel):
    lead_ids: Optional[List[int]] = None

# API Endpoints
@app.get("/api/status")
def get_system_status():
    settings = get_all_settings()
    leads = get_leads(limit=1000)
    logs = get_email_logs(limit=1000)
    
    with_email = sum(1 for l in leads if l.get("email"))
    needs_website = sum(1 for l in leads if not l.get("has_website"))
    sent_count = sum(1 for log in logs if log.get("status") in ["sent", "simulated"])
    
    return {
        "total_leads": len(leads),
        "leads_with_email": with_email,
        "leads_needing_website": needs_website,
        "emails_dispatched": sent_count,
        "dry_run_mode": settings.get("dry_run_mode", True),
        "sender_name": settings.get("sender_name", "")
    }

@app.post("/api/discover")
def api_discover(req: DiscoverRequest):
    if not req.location.strip():
        raise HTTPException(status_code=400, detail="Location query cannot be empty.")
        
    result = discover_businesses(
        location_query=req.location.strip(),
        category=req.category,
        radius_meters=req.radius_meters
    )
    
    leads = result.get("leads", [])
    inserted = save_leads(leads)
    
    cat_filter = req.category if req.category and req.category.lower() != "all" else None
    returned_leads = get_leads(category=cat_filter, limit=100)
    if not returned_leads:
        returned_leads = get_leads(limit=100)
        
    return {
        "success": True,
        "count": len(leads),
        "inserted": inserted,
        "location": result.get("location"),
        "source": result.get("source"),
        "leads": returned_leads
    }

@app.get("/api/leads")
def api_get_leads(category: Optional[str] = None, status: Optional[str] = None, search: Optional[str] = None):
    leads = get_leads(category=category, status=status, search=search, limit=200)
    return {"leads": leads, "count": len(leads)}

@app.post("/api/leads/update")
def api_update_lead(req: LeadUpdateRequest):
    updates = {}
    if req.name is not None: updates["name"] = req.name
    if req.email is not None: updates["email"] = req.email
    if req.phone is not None: updates["phone"] = req.phone
    if req.website is not None: updates["website"] = req.website
    if req.email_subject is not None: updates["email_subject"] = req.email_subject
    if req.email_body is not None: updates["email_body"] = req.email_body
    
    update_lead(req.lead_id, updates)
    return {"success": True, "lead": get_lead_by_id(req.lead_id)}

@app.delete("/api/leads/{lead_id}")
def api_delete_lead(lead_id: int):
    delete_lead(lead_id)
    return {"success": True}

@app.post("/api/leads/clear")
def api_clear_leads():
    clear_all_leads()
    return {"success": True}

@app.post("/api/leads/enrich")
def api_enrich_lead(req: EnrichRequest):
    lead = get_lead_by_id(req.lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    website = lead.get("website") or ""
    phone = lead.get("phone") or ""
    email = lead.get("email") or ""

    # If missing contact details or website, run live web search
    if not website or not email or not phone:
        online_data = enrich_place_online(lead["name"], lead.get("city") or "")
        if online_data.get("phone") and not phone:
            phone = online_data["phone"]
        if online_data.get("website") and not website:
            website = online_data["website"]
        if online_data.get("email") and not email:
            email = online_data["email"]

    audit_res = audit_business_website(
        url=website,
        business_name=lead["name"],
        category=lead["category"]
    )

    if audit_res.get("emails") and not email:
        email = audit_res["emails"][0]
    
    updates = {
        "website": website,
        "phone": phone,
        "email": email,
        "has_website": 1 if website else 0,
        "has_digital_menu": 1 if audit_res["has_digital_menu"] else 0,
        "has_booking_system": 1 if audit_res["has_booking_system"] else 0,
        "opportunity_score": audit_res["opportunity_score"] if website else 95,
        "primary_angle": audit_res["primary_angle"] if website else "website_creation",
        "audit_summary": audit_res["audit_summary"] if website else "No official website found on public search. Prime prospect for a new website setup.",
        "status": "enriched" if email else lead["status"]
    }
        
    update_lead(req.lead_id, updates)
    return {"success": True, "audit": audit_res, "lead": get_lead_by_id(req.lead_id)}

@app.post("/api/leads/auto-find-email")
def api_auto_find_email(req: EnrichRequest):
    lead = get_lead_by_id(req.lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    online_data = enrich_place_online(lead["name"], lead.get("city") or "")
    website = online_data.get("website") or lead.get("website") or ""
    phone = online_data.get("phone") or lead.get("phone") or ""
    email = online_data.get("email") or lead.get("email") or ""
    
    if website and not email:
        audit_res = audit_business_website(website, lead["name"], lead["category"])
        if audit_res.get("emails"):
            email = audit_res["emails"][0]
            
    updates = {
        "website": website,
        "phone": phone,
        "email": email,
        "has_website": 1 if website else 0,
        "status": "enriched" if email else lead["status"]
    }
    update_lead(req.lead_id, updates)
    return {"success": True, "found": bool(email), "lead": get_lead_by_id(req.lead_id)}

@app.post("/api/batch-enrich")
def api_batch_enrich(req: BatchEnrichRequest):
    leads = get_leads(limit=200)
    target_leads = [l for l in leads if (not req.lead_ids or l["id"] in req.lead_ids)]
    
    enriched_count = 0
    for lead in target_leads:
        website = lead.get("website") or ""
        phone = lead.get("phone") or ""
        email = lead.get("email") or ""
        
        if not website or not email or not phone:
            online_data = enrich_place_online(lead["name"], lead.get("city") or "")
            if online_data.get("phone") and not phone:
                phone = online_data["phone"]
            if online_data.get("website") and not website:
                website = online_data["website"]
            if online_data.get("email") and not email:
                email = online_data["email"]

        if website and not email:
            audit_res = audit_business_website(website, lead["name"], lead["category"])
            if audit_res.get("emails"):
                email = audit_res["emails"][0]
                
        update_lead(lead["id"], {
            "website": website,
            "phone": phone,
            "email": email,
            "has_website": 1 if website else 0,
            "status": "enriched" if email else lead["status"]
        })
        enriched_count += 1
        
    return {"success": True, "count": enriched_count}

@app.post("/api/generate-pitch")
def api_generate_pitch(req: PitchGenerateRequest):
    lead = get_lead_by_id(req.lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    settings = get_all_settings()
    pitch = generate_cold_pitch(
        business_name=lead["name"],
        category=lead["category"],
        city=lead.get("city") or "your area",
        website=lead.get("website", ""),
        primary_angle=lead.get("primary_angle", "website_creation"),
        sender_name=settings.get("sender_name", "Vishal Kumar Tiwari"),
        sender_title=settings.get("sender_title", "Co-Founder, Zenix Services"),
        sender_email=settings.get("sender_email", "zenixservices67@gmail.com"),
        website_url=settings.get("website_url", "https://zenixservices.online"),
        tone=req.tone,
        api_key=settings.get("gemini_api_key")
    )
    
    update_lead(req.lead_id, {
        "email_subject": pitch["subject"],
        "email_body": pitch["body"],
        "status": "pitched" if lead["status"] == "discovered" else lead["status"]
    })
    
    return {"success": True, "pitch": pitch, "lead": get_lead_by_id(req.lead_id)}

@app.post("/api/batch-generate")
def api_batch_generate(req: BatchGenerateRequest):
    settings = get_all_settings()
    leads = get_leads(limit=100)
    target_leads = [l for l in leads if (not req.lead_ids or l["id"] in req.lead_ids)]
    
    generated_count = 0
    for lead in target_leads:
        pitch = generate_cold_pitch(
            business_name=lead["name"],
            category=lead["category"],
            city=lead.get("city") or "your area",
            website=lead.get("website", ""),
            primary_angle=lead.get("primary_angle", "website_creation"),
            sender_name=settings.get("sender_name", "Vishal Kumar Tiwari"),
            sender_title=settings.get("sender_title", "Co-Founder, Zenix Services"),
            sender_email=settings.get("sender_email", "zenixservices67@gmail.com"),
            website_url=settings.get("website_url", "https://zenixservices.online"),
            tone=req.tone,
            api_key=settings.get("gemini_api_key")
        )
        update_lead(lead["id"], {
            "email_subject": pitch["subject"],
            "email_body": pitch["body"],
            "status": "pitched" if lead["status"] == "discovered" else lead["status"]
        })
        generated_count += 1
        
    return {"success": True, "count": generated_count}

@app.post("/api/send-email")
def api_send_email(req: SendEmailRequest):
    lead = get_lead_by_id(req.lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    if not lead.get("email"):
        raise HTTPException(status_code=400, detail="Lead does not have an email address configured.")
        
    settings = get_all_settings()
    subject = req.subject.strip()
    body = req.body.strip()

    if not subject or not body:
        pitch = generate_cold_pitch(
            business_name=lead["name"],
            category=lead["category"],
            city=lead.get("city") or "your area",
            website=lead.get("website", ""),
            primary_angle=lead.get("primary_angle", "website_creation"),
            sender_name=settings.get("sender_name", "Vishal Kumar Tiwari"),
            sender_title=settings.get("sender_title", "Co-Founder, Zenix Services"),
            sender_email=settings.get("sender_email", "zenixservices67@gmail.com"),
            website_url=settings.get("website_url", "https://zenixservices.online"),
            tone="friendly",
            api_key=settings.get("gemini_api_key")
        )
        subject = subject or pitch["subject"]
        body = body or pitch["body"]
        update_lead(req.lead_id, {"email_subject": subject, "email_body": body})

    res = send_email_message(
        to_email=lead["email"],
        business_name=lead["name"],
        subject=subject,
        body=body,
        smtp_settings=settings
    )
    
    status = "simulated" if res.get("simulated") else ("sent" if res.get("success") else "failed")
    error = res.get("error")
    
    log_email_sent(
        lead_id=req.lead_id,
        recipient=lead["email"],
        business_name=lead["name"],
        subject=subject,
        body=body,
        status=status,
        error_message=error
    )
    
    return {"success": res.get("success", False), "result": res}

@app.post("/api/batch-send")
def api_batch_send(req: BatchSendRequest):
    settings = get_all_settings()
    delay = settings.get("send_delay_seconds", 2)
    
    success_count = 0
    fail_count = 0
    results = []
    
    for idx, lead_id in enumerate(req.lead_ids):
        lead = get_lead_by_id(lead_id)
        if not lead or not lead.get("email"):
            fail_count += 1
            results.append({"lead_id": lead_id, "success": False, "error": "Missing email address"})
            continue

        subj = lead.get("email_subject") or ""
        body_text = lead.get("email_body") or ""

        if not subj or not body_text:
            pitch = generate_cold_pitch(
                business_name=lead["name"],
                category=lead["category"],
                city=lead.get("city") or "your area",
                website=lead.get("website", ""),
                primary_angle=lead.get("primary_angle", "website_creation"),
                sender_name=settings.get("sender_name", "Vishal Kumar Tiwari"),
                sender_title=settings.get("sender_title", "Co-Founder, Zenix Services"),
                sender_email=settings.get("sender_email", "zenixservices67@gmail.com"),
                website_url=settings.get("website_url", "https://zenixservices.online"),
                tone="friendly",
                api_key=settings.get("gemini_api_key")
            )
            subj = subj or pitch["subject"]
            body_text = body_text or pitch["body"]
            update_lead(lead_id, {"email_subject": subj, "email_body": body_text})
            
        res = send_email_message(
            to_email=lead["email"],
            business_name=lead["name"],
            subject=subj,
            body=body_text,
            smtp_settings=settings
        )
        
        status = "simulated" if res.get("simulated") else ("sent" if res.get("success") else "failed")
        error = res.get("error")
        
        log_email_sent(
            lead_id=lead_id,
            recipient=lead["email"],
            business_name=lead["name"],
            subject=subj,
            body=body_text,
            status=status,
            error_message=error
        )
        
        if res.get("success"):
            success_count += 1
        else:
            fail_count += 1
            
        results.append({"lead_id": lead_id, "name": lead["name"], "res": res})
        
        # Rate limit delay between sends
        if idx < len(req.lead_ids) - 1:
            time.sleep(delay)
            
    return {
        "success": True,
        "total": len(req.lead_ids),
        "successful": success_count,
        "failed": fail_count,
        "results": results
    }

@app.get("/api/logs")
def api_get_logs():
    return {"logs": get_email_logs(limit=150)}

@app.get("/api/settings")
def api_get_settings():
    s = get_all_settings()
    # Mask password for safety in UI
    masked = dict(s)
    if masked.get("smtp_pass"):
        masked["smtp_pass_set"] = True
        masked["smtp_pass"] = "••••••••••••"
    else:
        masked["smtp_pass_set"] = False
    return {"settings": masked}

@app.post("/api/settings")
def api_save_settings(req: SettingsUpdateRequest):
    # If smtp_user is provided, synchronize sender_email automatically if not given
    if "smtp_user" in req.settings and req.settings["smtp_user"]:
        user_val = str(req.settings["smtp_user"]).strip()
        if "@" in user_val and "sender_email" not in req.settings:
            req.settings["sender_email"] = user_val
    elif "sender_email" in req.settings and req.settings["sender_email"]:
        email_val = str(req.settings["sender_email"]).strip()
        if "@" in email_val and "smtp_user" not in req.settings:
            req.settings["smtp_user"] = email_val

    for k, v in req.settings.items():
        if k == "smtp_pass":
            if not v or v == "••••••••••••":
                continue  # Don't overwrite with empty or masked placeholder
            v = str(v).strip().replace(" ", "")
        update_setting(k, v)
    return {"success": True}

@app.post("/api/test-smtp")
def api_test_smtp(payload: Optional[Dict[str, Any]] = None):
    settings = get_all_settings()
    if payload:
        if payload.get("smtp_user"):
            u = payload["smtp_user"].strip()
            settings["smtp_user"] = u
            settings["sender_email"] = u
        if payload.get("smtp_pass") and payload.get("smtp_pass") != "••••••••••••":
            settings["smtp_pass"] = payload["smtp_pass"].strip().replace(" ", "")
    return test_smtp_connection(settings)

@app.post("/api/send-test-email")
def api_send_test_email(payload: Optional[Dict[str, Any]] = None):
    settings = get_all_settings()
    if payload:
        if payload.get("smtp_user"):
            u = payload["smtp_user"].strip()
            settings["smtp_user"] = u
            settings["sender_email"] = u
        if payload.get("smtp_pass") and payload.get("smtp_pass") != "••••••••••••":
            settings["smtp_pass"] = payload["smtp_pass"].strip().replace(" ", "")
        
    user = (settings.get("smtp_user") or settings.get("sender_email") or "").strip()
    raw_pass = settings.get("smtp_pass", "")
    clean_pass = (raw_pass or "").strip().replace(" ", "")
    sender_name = settings.get("sender_name", "LocalReach Agent").strip()
    
    if not user or "@" not in user:
        return {
            "success": False,
            "message": "Please enter a valid Gmail address in Settings first."
        }

    if not clean_pass or clean_pass == "••••••••••••":
        return {
            "success": False,
            "message": "Please enter your 16-character Google App Password in Settings before sending a test email."
        }
        
    live_settings = dict(settings)
    live_settings["dry_run_mode"] = False
    
    res = send_email_message(
        to_email=user,
        business_name="LocalReach Verification",
        subject="✅ Gmail Connected & Verified - Real Email Delivery Working!",
        body=(
            f"Hello {sender_name},\n\n"
            f"Congratulations! Your Google App Password has been verified and live email delivery is working perfectly.\n\n"
            f"Outgoing emails will land directly in client inboxes, and a full copy is saved right here in your Gmail Sent folder.\n\n"
            f"Sender Account: {user}\n"
            f"Host: smtp.gmail.com (TLS/SSL)\n\n"
            f"Best regards,\n"
            f"LocalReach AI Agent (https://zenixservices.online)"
        ),
        smtp_settings=live_settings
    )
    
    if res.get("success"):
        log_email_sent(
            lead_id=None,
            recipient=user,
            business_name="Gmail Self-Test",
            subject="✅ Gmail Connected & Verified - Real Email Delivery Working!",
            body="Self-test verification email",
            status="sent",
            error_message=None
        )
        return {
            "success": True,
            "message": f"Real test email delivered to {user}! Check your inbox and your Gmail Sent folder right now."
        }
    else:
        return {
            "success": False,
            "message": res.get("error") or "Failed to send live test email."
        }

@app.post("/api/settings/toggle-mode")
def api_toggle_mode():
    settings = get_all_settings()
    current = bool(settings.get("dry_run_mode", True))
    new_mode = not current
    update_setting("dry_run_mode", new_mode)
    return {"success": True, "dry_run_mode": new_mode}

@app.get("/api/export")
def api_export_leads():
    leads = get_leads(limit=1000)
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        "ID", "Name", "Category", "Subcategory", "Address", "City",
        "Phone", "Website", "Email", "Has Website", "Has Digital Menu",
        "Opportunity Score", "Primary Angle", "Email Subject", "Status", "Last Contacted"
    ])
    
    for l in leads:
        writer.writerow([
            l.get("id"), l.get("name"), l.get("category"), l.get("subcategory"),
            l.get("address"), l.get("city"), l.get("phone"), l.get("website"),
            l.get("email"), l.get("has_website"), l.get("has_digital_menu"),
            l.get("opportunity_score"), l.get("primary_angle"),
            l.get("email_subject"), l.get("status"), l.get("last_contacted")
        ])
        
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=localreach_leads.csv"}
    )
