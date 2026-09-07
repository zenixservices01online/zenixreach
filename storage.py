import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from config import DB_PATH, DEFAULT_SETTINGS

def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Leads table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                osm_id TEXT UNIQUE,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT,
                address TEXT,
                city TEXT,
                phone TEXT,
                website TEXT,
                email TEXT,
                has_website INTEGER DEFAULT 0,
                has_digital_menu INTEGER DEFAULT 0,
                has_booking_system INTEGER DEFAULT 0,
                opportunity_score INTEGER DEFAULT 50,
                primary_angle TEXT,
                audit_summary TEXT,
                email_subject TEXT,
                email_body TEXT,
                status TEXT DEFAULT 'discovered', -- discovered, enriched, pitched, sent, simulated, failed
                last_contacted TEXT,
                created_at TEXT NOT NULL
            )
        """)
        
        # Settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        
        # Email logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_id INTEGER,
                recipient_email TEXT NOT NULL,
                business_name TEXT NOT NULL,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                status TEXT NOT NULL, -- simulated, sent, failed
                error_message TEXT,
                sent_at TEXT NOT NULL,
                FOREIGN KEY (lead_id) REFERENCES leads(id)
            )
        """)
        
        # Seed settings if empty
        for key, val in DEFAULT_SETTINGS.items():
            cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, str(val)))
            
        conn.commit()

# Settings Helpers
def get_all_settings() -> Dict[str, Any]:
    with get_db() as conn:
        cursor = conn.cursor()
        rows = cursor.execute("SELECT key, value FROM settings").fetchall()
        settings = dict(DEFAULT_SETTINGS)
        for row in rows:
            val = row["value"]
            if val.lower() == "true":
                val = True
            elif val.lower() == "false":
                val = False
            elif val.isdigit():
                val = int(val)
            settings[row["key"]] = val
        return settings

def update_setting(key: str, value: Any):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
        conn.commit()

# Leads Helpers
def save_leads(leads_data: List[Dict[str, Any]]) -> int:
    inserted = 0
    now = datetime.now().isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        for lead in leads_data:
            try:
                cursor.execute("""
                    INSERT INTO leads (
                        osm_id, name, category, subcategory, address, city, phone, website, email,
                        has_website, has_digital_menu, has_booking_system, opportunity_score,
                        primary_angle, audit_summary, status, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'discovered', ?)
                    ON CONFLICT(osm_id) DO UPDATE SET
                        address = CASE WHEN excluded.address IS NOT NULL AND excluded.address != '' THEN excluded.address ELSE leads.address END,
                        phone = CASE WHEN excluded.phone IS NOT NULL AND excluded.phone != '' THEN excluded.phone ELSE leads.phone END,
                        website = CASE WHEN excluded.website IS NOT NULL AND excluded.website != '' THEN excluded.website ELSE leads.website END,
                        email = CASE WHEN excluded.email IS NOT NULL AND excluded.email != '' THEN excluded.email ELSE leads.email END
                """, (
                    lead.get("osm_id", f"gen_{lead.get('name')}_{now}"),
                    lead.get("name", "Unknown Business"),
                    lead.get("category", "General"),
                    lead.get("subcategory", ""),
                    lead.get("address", ""),
                    lead.get("city", ""),
                    lead.get("phone", ""),
                    lead.get("website", ""),
                    lead.get("email", ""),
                    1 if lead.get("website") else 0,
                    1 if lead.get("has_digital_menu") else 0,
                    1 if lead.get("has_booking_system") else 0,
                    lead.get("opportunity_score", 60),
                    lead.get("primary_angle", "website_creation"),
                    lead.get("audit_summary", ""),
                    now
                ))
                inserted += 1
            except Exception as e:
                print(f"Error inserting lead: {e}")
        conn.commit()
    return inserted

def get_leads(category: Optional[str] = None, status: Optional[str] = None, search: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
    with get_db() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM leads WHERE 1=1"
        params = []
        
        if category and category.lower() != "all":
            c_low = category.lower()
            if any(w in c_low for w in ["restaurant", "cafe", "food", "dining", "bakery"]):
                query += " AND (category LIKE '%Restaurant%' OR category LIKE '%Cafe%' OR subcategory LIKE '%Restaurant%' OR subcategory LIKE '%Cafe%' OR subcategory LIKE '%Dining%')"
            elif any(w in c_low for w in ["physio", "rehab"]):
                query += " AND (category LIKE '%Physio%' OR subcategory LIKE '%Physio%' OR subcategory LIKE '%Rehab%' OR name LIKE '%Physio%')"
            elif any(w in c_low for w in ["dental"]):
                query += " AND (category LIKE '%Dental%' OR subcategory LIKE '%Dental%')"
            elif any(w in c_low for w in ["clinic", "healthcare", "small_clinic", "doctor", "hospital"]):
                query += " AND (category LIKE '%Clinic%' OR category LIKE '%Healthcare%' OR subcategory LIKE '%Clinic%' OR subcategory LIKE '%Healthcare%')"
            elif any(w in c_low for w in ["small_enterprise", "enterprise", "salon", "spa", "retail"]):
                query += " AND (category LIKE '%Small Enterprise%' OR category LIKE '%Enterprise%' OR category LIKE '%Salon%' OR subcategory LIKE '%Salon%' OR subcategory LIKE '%Spa%' OR subcategory LIKE '%Retail%')"
            else:
                query += " AND (category = ? OR category LIKE ?)"
                params.extend([category, f"%{category}%"])
            
        if status and status != "all":
            query += " AND status = ?"
            params.append(status)
            
        if search:
            query += " AND (name LIKE ? OR address LIKE ? OR email LIKE ? OR category LIKE ? OR subcategory LIKE ?)"
            term = f"%{search}%"
            params.extend([term, term, term, term, term])
            
        query += " ORDER BY opportunity_score DESC, id DESC LIMIT ?"
        params.append(limit)
        
        rows = cursor.execute(query, params).fetchall()
        return [dict(row) for row in rows]

def get_lead_by_id(lead_id: int) -> Optional[Dict[str, Any]]:
    with get_db() as conn:
        cursor = conn.cursor()
        row = cursor.execute("SELECT * FROM leads WHERE id = ?", (lead_id,)).fetchone()
        return dict(row) if row else None

def update_lead(lead_id: int, updates: Dict[str, Any]):
    fields = []
    values = []
    for k, v in updates.items():
        fields.append(f"{k} = ?")
        values.append(v)
    values.append(lead_id)
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE leads SET {', '.join(fields)} WHERE id = ?", values)
        conn.commit()

def delete_lead(lead_id: int):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM leads WHERE id = ?", (lead_id,))
        conn.commit()

def clear_all_leads():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM leads")
        conn.commit()

# Logs Helpers
def log_email_sent(lead_id: Optional[int], recipient: str, business_name: str, subject: str, body: str, status: str, error_message: Optional[str] = None):
    now = datetime.now().isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO email_logs (lead_id, recipient_email, business_name, subject, body, status, error_message, sent_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (lead_id, recipient, business_name, subject, body, status, error_message, now))
        
        if lead_id:
            cursor.execute("UPDATE leads SET status = ?, last_contacted = ? WHERE id = ?", (status, now, lead_id))
            
        conn.commit()

def get_email_logs(limit: int = 100) -> List[Dict[str, Any]]:
    with get_db() as conn:
        cursor = conn.cursor()
        rows = cursor.execute("SELECT * FROM email_logs ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [dict(row) for row in rows]
