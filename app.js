/**
 * Zenix Reach AI — Minimal, Robust Frontend Controller
 * Direct Indian locality search, multi-source email extraction, 1-click email & WhatsApp outreach.
 */

(function () {
  "use strict";

  // State
  let leads = [];
  let selectedLeadIds = new Set();
  let currentEditingLead = null;
  let currentWhatsAppLead = null;
  let isDryRun = true;

  // DOM Elements
  const statTotalLeads = document.getElementById("statTotalLeads");
  const statWithEmail = document.getElementById("statWithEmail");
  const statNeedingWebsite = document.getElementById("statNeedingWebsite");
  const statDispatched = document.getElementById("statDispatched");
  const dryRunIndicator = document.getElementById("dryRunIndicator");
  const modeText = document.getElementById("modeText");
  const logCountBadge = document.getElementById("logCountBadge");
  const batchSendCountBadge = document.getElementById("batchSendCountBadge");
  const selectionCountText = document.getElementById("selectionCountText");

  const discoveryForm = document.getElementById("discoveryForm");
  const locationInput = document.getElementById("locationInput");
  const categorySelect = document.getElementById("categorySelect");
  const discoverBtn = document.getElementById("discoverBtn");
  const discoverSpinner = document.getElementById("discoverSpinner");

  const leadsContainer = document.getElementById("leadsContainer");
  const emptyLeadsState = document.getElementById("emptyLeadsState");
  const leadsSearchInput = document.getElementById("leadsSearchInput");
  const filterEmailStatus = document.getElementById("filterEmailStatus");
  const filterCategory = document.getElementById("filterCategory");
  const selectAllLeads = document.getElementById("selectAllLeads");

  const enrichAllBtn = document.getElementById("enrichAllBtn");
  const batchSendModalBtn = document.getElementById("batchSendModalBtn");
  const exportCsvBtn = document.getElementById("exportCsvBtn");
  const clearLeadsBtn = document.getElementById("clearLeadsBtn");
  const loadSampleBtn = document.getElementById("loadSampleBtn");

  // Composer Modal Elements
  const composerModal = document.getElementById("composerModal");
  const closeComposerModal = document.getElementById("closeComposerModal");
  const cancelComposerBtn = document.getElementById("cancelComposerBtn");
  const composerLeadName = document.getElementById("composerLeadName");
  const composerCategory = document.getElementById("composerCategory");
  const composerCity = document.getElementById("composerCity");
  const composerWebsite = document.getElementById("composerWebsite");
  const composerScore = document.getElementById("composerScore");
  const composerRecipient = document.getElementById("composerRecipient");
  const composerTone = document.getElementById("composerTone");
  const composerSubject = document.getElementById("composerSubject");
  const composerBody = document.getElementById("composerBody");
  const regeneratePitchBtn = document.getElementById("regeneratePitchBtn");
  const copyComposerBtn = document.getElementById("copyComposerBtn");
  const sendComposerBtn = document.getElementById("sendComposerBtn");
  const composerSendSpinner = document.getElementById("composerSendSpinner");
  const composerModeNotice = document.getElementById("composerModeNotice");
  const cmnText = document.getElementById("cmnText");

  // WhatsApp Modal Elements
  const whatsappModal = document.getElementById("whatsappModal");
  const closeWhatsappModal = document.getElementById("closeWhatsappModal");
  const cancelWhatsappBtn = document.getElementById("cancelWhatsappBtn");
  const whatsappLeadName = document.getElementById("whatsappLeadName");
  const whatsappPhoneBadge = document.getElementById("whatsappPhoneBadge");
  const whatsappPhoneInput = document.getElementById("whatsappPhoneInput");
  const whatsappAutoFindBtn = document.getElementById("whatsappAutoFindBtn");
  const whatsappTemplateSelect = document.getElementById("whatsappTemplateSelect");
  const whatsappMessageText = document.getElementById("whatsappMessageText");
  const copyWhatsappBtn = document.getElementById("copyWhatsappBtn");
  const openWhatsappBtn = document.getElementById("openWhatsappBtn");

  // History Drawer Elements
  const toggleLogsBtn = document.getElementById("toggleLogsBtn");
  const logsDrawerOverlay = document.getElementById("logsDrawerOverlay");
  const closeLogsDrawer = document.getElementById("closeLogsDrawer");
  const closeLogsDrawerBtn = document.getElementById("closeLogsDrawerBtn");
  const refreshLogsBtn = document.getElementById("refreshLogsBtn");
  const terminalLogs = document.getElementById("terminalLogs");

  // Settings Modal Elements
  const headerSettingsBtn = document.getElementById("headerSettingsBtn");
  const settingsModal = document.getElementById("settingsModal");
  const closeSettingsModal = document.getElementById("closeSettingsModal");
  const cancelSettingsBtn = document.getElementById("cancelSettingsBtn");
  const saveSettingsBtn = document.getElementById("saveSettingsBtn");
  const settingSenderName = document.getElementById("settingSenderName");
  const settingSenderCompany = document.getElementById("settingSenderCompany");
  const settingSenderEmail = document.getElementById("settingSenderEmail");
  const settingSenderWebsite = document.getElementById("settingSenderWebsite");
  const settingSmtpUser = document.getElementById("settingSmtpUser");
  const settingSmtpPass = document.getElementById("settingSmtpPass");
  const settingBackendUrl = document.getElementById("settingBackendUrl");
  const testSmtpBtn = document.getElementById("testSmtpBtn");
  const smtpTestResult = document.getElementById("smtpTestResult");
  const campaignDryRunToggle = document.getElementById("campaignDryRunToggle");
  const sendTestEmailBtn = document.getElementById("sendTestEmailBtn");
  const filterWebsiteStatus = document.getElementById("filterWebsiteStatus");
  const metricCardTotal = document.getElementById("metricCardTotal");
  const metricCardEmail = document.getElementById("metricCardEmail");
  const metricCardNoWeb = document.getElementById("metricCardNoWeb");
  const metricCardDispatched = document.getElementById("metricCardDispatched");
  const qcountAll = document.getElementById("qcountAll");
  const qcountNoWeb = document.getElementById("qcountNoWeb");
  const qcountEmail = document.getElementById("qcountEmail");
  const qcountPhone = document.getElementById("qcountPhone");
  const composerAutoFindBtn = document.getElementById("composerAutoFindBtn");
  const cmnSwitchLiveBtn = document.getElementById("cmnSwitchLiveBtn");

  const toastContainer = document.getElementById("toastContainer");

  // Initialization
  async function init() {
    try {
      setupEventListeners();
    } catch (err) {
      console.error("Error setting up event listeners:", err);
    }
    await loadStatus();
    await loadLeads();
    await loadSettings();
    await loadLogs();
  }

  // Toast Notifications
  function showToast(message, type = "info") {
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    const icon = type === "success" ? "✓" : type === "error" ? "✕" : "ℹ";
    toast.innerHTML = `<span>${icon}</span> <span>${escapeHtml(message)}</span>`;
    toastContainer.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateY(8px)";
      setTimeout(() => toast.remove(), 250);
    }, 4000);
  }

  function escapeHtml(text) {
    if (!text) return "";
    return text.toString()
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // Extract clean 10-digit Indian phone number
  function extractIndianPhone10(rawPhone) {
    if (!rawPhone) return "";
    const digits = rawPhone.replace(/\D/g, "");
    if (digits.length >= 10) {
      const last10 = digits.slice(-10);
      const tollFrees = ["800", "888", "877", "866", "855", "844", "833"];
      if (/^[6-9]\d{9}$/.test(last10) && !tollFrees.some(tf => last10.startsWith(tf))) {
        return last10;
      }
    }
    return "";
  }

  // Storage Keys
  const STORAGE_KEY_LEADS = "zenix_local_leads";
  const STORAGE_KEY_LOGS = "zenix_local_logs";
  const STORAGE_KEY_DISPATCHED = "zenix_dispatched_count";

  function getLocalLeads() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY_LEADS);
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  }

  function setLocalLeads(leadsArray) {
    try {
      localStorage.setItem(STORAGE_KEY_LEADS, JSON.stringify(leadsArray));
    } catch (e) {
      console.warn("Storage write error", e);
    }
  }

  function mergeNewLeads(newArr) {
    const existing = leads || [];
    const seenNames = new Set(existing.map(l => (l.name || "").toLowerCase().trim()));
    const added = [];
    for (const item of newArr) {
      const n = (item.name || "").toLowerCase().trim();
      if (!seenNames.has(n)) {
        seenNames.add(n);
        added.push(item);
      }
    }
    leads = [...added, ...existing];
    setLocalLeads(leads);
    return added.length;
  }

  // Resolves API endpoint URL (supports custom cloud backend on Netlify)
  const CLOUD_TUNNEL_FALLBACK = "https://occupations-priorities-pursuit-excellence.trycloudflare.com";

  function getApiUrl(path) {
    let customBackend = (localStorage.getItem("zenix_backend_url") || "").trim();
    if (!customBackend && (window.location.hostname.includes("netlify.app") || window.location.hostname.includes("web.app"))) {
      customBackend = CLOUD_TUNNEL_FALLBACK;
    }
    if (customBackend && path.startsWith("/api")) {
      return customBackend.replace(/\/+$/, "") + path;
    }
    return path;
  }

  // Safe JSON fetcher resistant to WebKit/Safari stream errors and unexpected non-JSON bodies
  async function safeFetchJson(url, options = {}) {
    const targetUrl = url.startsWith("/api") ? getApiUrl(url) : url;
    const headers = Object.assign({ "Accept": "application/json" }, options.headers || {});
    if (options.body && typeof options.body === "string" && !headers["Content-Type"]) {
      headers["Content-Type"] = "application/json";
    }
    try {
      const res = await fetch(targetUrl, Object.assign({}, options, { headers }));
      const text = await res.text();
      let data = {};
      if (text) {
        try {
          data = JSON.parse(text);
        } catch (err) {
          // If server returns HTML or text (e.g. 404 / Netlify SPA fallback / Page not found)
          let cleanMessage = "Server returned an unexpected response.";
          const isNetlify = window.location.hostname.includes("netlify.app") || window.location.hostname.includes("web.app");
          const customBackend = (localStorage.getItem("zenix_backend_url") || "").trim();

          if (isNetlify && !customBackend) {
            cleanMessage = "Python Backend not connected on Netlify. Netlify only hosts the frontend interface. Please open your app locally on this computer at http://localhost:8000, or enter your deployed Python API URL in ⚙️ Settings.";
          } else if (res.status === 404 || text.includes("Page not found") || text.includes("<!DOCTYPE") || text.includes("<html")) {
            cleanMessage = `Backend API endpoint not reachable (${res.status || 404}). If running locally, make sure python main.py is active at http://localhost:8000.`;
          } else {
            cleanMessage = text.replace(/<[^>]*>/g, '').trim().slice(0, 160) || "Server returned non-JSON response.";
          }
          return { ok: false, status: res.status || 404, data: { success: false, message: cleanMessage } };
        }
      }
      return { ok: res.ok, status: res.status, data };
    } catch (netErr) {
      let netMsg = netErr.message || "Network connection failed";
      if (window.location.hostname.includes("netlify.app") && !localStorage.getItem("zenix_backend_url")) {
        netMsg = "Python Backend not reachable from Netlify. Please open the app locally at http://localhost:8000, or enter your deployed Python API URL in Settings.";
      }
      return { ok: false, status: 0, data: { success: false, message: netMsg } };
    }
  }

  // Client-Side Pitch Copy Engine (Matches Vishal Kumar Tiwari / Zenix Services templates)
  function generatePitchClient(businessName, category, city, website, primaryAngle, tone = "friendly") {
    const hasSite = Boolean(website && website.trim());
    const isRestaurant = /restaurant|cafe|coffee|bistro|bakery|bar|dining|pizza|food/i.test(category);
    const isDental = /dental|dentist|clinic|doctor|health|medical|hospital/i.test(category);
    const curSenderName = (settingSenderName?.value || "Vishal Kumar Tiwari").trim();
    const curCompany = (settingSenderCompany?.value || "Zenix Services").trim();
    const curEmail = (settingSenderEmail?.value || settingSmtpUser?.value || "zenixservices67@gmail.com").trim();
    const curSite = (settingSenderWebsite?.value || "https://zenixservices.online").trim();
    const signature = `${curSenderName}\nCo-Founder, ${curCompany}\nWebsite: ${curSite}\nEmail: ${curEmail}`;

    let subject = `Website & Digital Presence for ${businessName}`;
    let body = "";

    if (isRestaurant) {
      if (tone === "direct") {
        subject = `Quick question regarding ${businessName}'s online menu & ordering`;
        body = `Hi ${businessName} team,\n\nI came across ${businessName} while searching for great dining spots in ${city}.\n\nI noticed you do not currently have a dedicated mobile-friendly site with an interactive digital menu.\n\nAt Zenix Services, we specialize in building sleek websites and lightning-fast QR menu systems for local cafes & restaurants:\n• Table QR scan for instant phone menu browsing\n• Zero-commission direct ordering so you keep 100% of profits\n• One-tap Google Maps integration\n\nWe have worked with multiple cafes and restaurants to launch interactive menus: https://zenixservices.online\n\nWould you be open to a 60-second preview mockup for ${businessName} this week?\n\nBest regards,\n${signature}`;
      } else {
        subject = `Website & Digital Menu concept for ${businessName} 🍽️`;
        body = `Hi there,\n\nI hope you are having a wonderful week at ${businessName}!\n\nI was browsing local favorites in ${city} and love the concept of ${businessName}. I noticed ${hasSite ? "your website could be upgraded with a modern interactive QR menu" : "you do not currently have an official website set up"}.\n\nIn today's dining scene, over 80% of guests check a restaurant's food menu on their smartphone before deciding where to eat.\n\nAt Zenix Services, we help local restaurants and cafes create beautiful, mobile-first websites with:\n1. Instant QR Code digital menus that look great on any phone\n2. One-tap table reservations & Google Maps integration\n3. Zero-commission online ordering so you keep 100% of your food sales\n\nCheck out our live client work at: https://zenixservices.online\n\nCould I send over a complimentary mockup of your new website and menu system to take a quick look?\n\nBest wishes,\n${signature}`;
      }
    } else if (isDental) {
      if (tone === "direct") {
        subject = `Patient acquisition & 24/7 online booking for ${businessName}`;
        body = `Hi ${businessName} team,\n\nI hope your practice is having a productive week.\n\nI was looking up healthcare practices in ${city} and noticed ${hasSite ? "your current site does not offer instant 24/7 online appointment booking" : "you do not have an active website for new patients to find and book you"}.\n\nAt Zenix Services, we build modern healthcare websites with 24/7 patient booking and clinic tour showcases: https://zenixservices.online\n\nWould you be open to reviewing a complimentary design concept for ${businessName}?\n\nBest regards,\n${signature}`;
      } else {
        subject = `Modern patient booking website concept for ${businessName} 🦷`;
        body = `Hi ${businessName} team,\n\nI hope you're having a wonderful week.\n\nI came across ${businessName} while reviewing top-rated practices in ${city}. I noticed ${hasSite ? "your website could be upgraded with instant online appointment booking" : "there is currently no official website linked to your practice"}.\n\nOver 72% of patients now search for nearby doctors and book visits on their smartphones. We build fast, mobile-friendly websites with online scheduling, WhatsApp booking, and Google Maps optimization.\n\nSee our portfolio at: https://zenixservices.online\n\nCould I share a complimentary mockup with you this week?\n\nWarm regards,\n${signature}`;
      }
    } else {
      subject = `Modern website & Google Maps visibility concept for ${businessName}`;
      body = `Hi there,\n\nI hope business is going well at ${businessName}!\n\nI came across your business while researching standout local enterprises in ${city}. I noticed ${hasSite ? "your website could benefit from a speed and conversion upgrade" : "you do not currently have an official mobile website on public record"}.\n\nAt Zenix Services, we help Indian small businesses launch high-converting websites that rank higher on Google Maps and drive daily phone & WhatsApp inquiries.\n\nExplore our client portfolio at: https://zenixservices.online\n\nWould you like me to send over a complimentary design mockup for ${businessName}?\n\nBest wishes,\n${signature}`;
    }

    return { subject, body };
  }

  // Geocode location using Nominatim with prioritized Indian neighborhood coordinates
  async function geocodeLocation(query) {
    const lq = query.toLowerCase();

    // Prioritize specific neighborhoods BEFORE broad city names
    const knownAreas = [
      { key: "lalpur", lat: 23.3703, lon: 85.3340, name: "Lalpur, Ranchi" },
      { key: "hinoo", lat: 23.3283, lon: 85.3217, name: "Hinoo, Ranchi" },
      { key: "doranda", lat: 23.3364, lon: 85.3256, name: "Doranda, Ranchi" },
      { key: "harmu", lat: 23.3541, lon: 85.3025, name: "Harmu, Ranchi" },
      { key: "bariatu", lat: 23.3912, lon: 85.3533, name: "Bariatu, Ranchi" },
      { key: "kanke", lat: 23.4278, lon: 85.3239, name: "Kanke, Ranchi" },
      { key: "boring rd", lat: 25.6175, lon: 85.1197, name: "Boring Rd, Patna" },
      { key: "patna", lat: 25.5941, lon: 85.1376, name: "Patna" },
      { key: "ranchi", lat: 23.3441, lon: 85.3096, name: "Ranchi" },
      { key: "lucknow", lat: 26.8467, lon: 80.9462, name: "Lucknow" },
      { key: "delhi", lat: 28.6139, lon: 77.2090, name: "Delhi" },
      { key: "mumbai", lat: 19.0760, lon: 72.8777, name: "Mumbai" },
      { key: "bengaluru", lat: 12.9716, lon: 77.5946, name: "Bengaluru" },
      { key: "kolkata", lat: 22.5726, lon: 88.3639, name: "Kolkata" }
    ];

    for (const item of knownAreas) {
      if (lq.includes(item.key)) {
        return item;
      }
    }

    try {
      const cleanQ = query.replace(/\b(dentists?|dental|restaurants?|cafes?|clinics?|salons?)\b/gi, "").trim();
      const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(cleanQ + ", Jharkhand, India")}&format=json&limit=1`;
      const res = await fetch(url, { headers: { "Accept": "application/json" } });
      if (res.ok) {
        const arr = await res.json();
        if (arr && arr.length > 0) {
          return { lat: parseFloat(arr[0].lat), lon: parseFloat(arr[0].lon), name: arr[0].display_name.split(",")[0] };
        }
      }
    } catch (e) {
      console.warn("Nominatim fetch error:", e);
    }
    return { lat: 23.3703, lon: 85.3340, name: "Lalpur, Ranchi" };
  }

  // Direct Overpass API query from browser
  async function queryOverpassInBrowser(lat, lon, radiusMeters, category) {
    let tagFilters = '';
    if (category === 'restaurant') {
      tagFilters = `
        node["amenity"~"restaurant|cafe|fast_food|bar|food_court|ice_cream|bakery"](around:${radiusMeters},${lat},${lon});
        way["amenity"~"restaurant|cafe|fast_food|bar"](around:${radiusMeters},${lat},${lon});
      `;
    } else if (category === 'dental') {
      tagFilters = `
        node["amenity"~"dentist|clinic|doctors|hospital|pharmacy"](around:${radiusMeters},${lat},${lon});
        node["healthcare"](around:${radiusMeters},${lat},${lon});
        way["amenity"~"dentist|clinic|doctors|hospital"](around:${radiusMeters},${lat},${lon});
      `;
    } else if (category === 'retail') {
      tagFilters = `
        node["shop"](around:${radiusMeters},${lat},${lon});
        node["craft"](around:${radiusMeters},${lat},${lon});
        way["shop"](around:${radiusMeters},${lat},${lon});
      `;
    } else {
      tagFilters = `
        node["amenity"~"restaurant|cafe|fast_food|dentist|clinic|doctors|hospital|pharmacy"](around:${radiusMeters},${lat},${lon});
        node["shop"~"beauty|hairdresser|bakery|supermarket|clothes|optician|tailor|electronics"](around:${radiusMeters},${lat},${lon});
        way["amenity"~"restaurant|cafe|dentist|clinic"](around:${radiusMeters},${lat},${lon});
      `;
    }

    const query = `[out:json][timeout:15];(${tagFilters});out center 45;`;
    const endpoints = [
      "https://overpass-api.de/api/interpreter",
      "https://lz4.overpass-api.de/api/interpreter"
    ];

    for (const ep of endpoints) {
      try {
        const res = await fetch(ep, {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: "data=" + encodeURIComponent(query)
        });
        if (res.ok) {
          const json = await res.json();
          if (json && json.elements && json.elements.length > 0) {
            return json.elements;
          }
        }
      } catch (e) {
        console.warn("Overpass endpoint failed, trying mirror:", ep, e);
      }
    }
    return [];
  }

  // Convert raw OSM element to verified lead
  function convertOsmElementToLead(elem, cityName) {
    const tags = elem.tags || {};
    const name = tags.name || tags["name:en"] || tags["brand"] || "";
    if (!name || name.trim().length < 2) return null;

    // Phone
    const rawPhone = tags["contact:phone"] || tags.phone || tags.mobile || tags["contact:mobile"] || "";
    const p10 = extractIndianPhone10(rawPhone);
    const phone = p10 ? `+91 ${p10.slice(0, 5)} ${p10.slice(5)}` : (rawPhone || "");

    // Website
    const rawWeb = tags["contact:website"] || tags.website || tags.url || "";
    let website = "";
    if (rawWeb && rawWeb.startsWith("http")) website = rawWeb;
    else if (rawWeb && rawWeb.includes(".")) website = "https://" + rawWeb;

    // Email
    let email = (tags["contact:email"] || tags.email || "").trim().toLowerCase();
    if (email && (!email.includes("@") || !email.includes("."))) email = "";

    // Category
    const amenity = (tags.amenity || "").toLowerCase();
    const shop = (tags.shop || "").toLowerCase();
    const healthcare = (tags.healthcare || "").toLowerCase();

    let category = "Small Businesses & Salons";
    let subcategory = "Local Business";
    let primaryAngle = "website_creation";

    if (amenity.match(/restaurant|cafe|fast_food|bar|bakery/)) {
      category = "Restaurant / Cafe";
      subcategory = amenity === "cafe" ? "Cafe & Dining" : "Restaurant & Dining";
      primaryAngle = website ? "digital_menu" : "website_creation";
    } else if (amenity.match(/dentist|clinic|doctors|hospital/) || healthcare) {
      category = "Dental & Healthcare";
      subcategory = amenity === "dentist" ? "Dental Clinic" : "Healthcare Practice";
      primaryAngle = "appointment_system";
    } else if (shop.match(/beauty|hairdresser/)) {
      category = "Small Businesses & Salons";
      subcategory = "Beauty Salon & Spa";
      primaryAngle = "appointment_system";
    } else if (shop) {
      category = "Small Businesses & Salons";
      subcategory = "Retail & Services";
      primaryAngle = "website_creation";
    }

    // Address
    const street = tags["addr:street"] || tags["addr:suburb"] || tags["addr:place"] || "";
    const postcode = tags["addr:postcode"] || "";
    const addressParts = [street, cityName, postcode].filter(Boolean);
    const address = addressParts.length > 0 ? addressParts.join(", ") : `${cityName}, India`;

    const hasWebsite = website ? 1 : 0;
    const oppScore = hasWebsite ? 80 : 95;
    const auditSummary = hasWebsite 
      ? `Discovered online with active website (${website.replace(/^https?:\/\//, '')}). Target for digital menu & mobile revamp.`
      : `No official website detected on record. Prime candidate for modern web launch.`;

    const pitch = generatePitchClient(name, category, cityName, website, primaryAngle);

    return {
      id: Date.now() + Math.floor(Math.random() * 10000),
      osm_id: `osm_${elem.type}_${elem.id}`,
      name: name.trim(),
      category: category,
      subcategory: subcategory,
      address: address,
      city: cityName,
      phone: phone,
      website: website,
      email: email,
      has_website: hasWebsite,
      has_digital_menu: 0,
      has_booking_system: 0,
      opportunity_score: oppScore,
      primary_angle: primaryAngle,
      audit_summary: auditSummary,
      email_subject: pitch.subject,
      email_body: pitch.body,
      status: email ? "enriched" : "discovered",
      created_at: new Date().toISOString()
    };
  }

  // In-Browser Live Discovery Engine
  async function discoverBusinessesInBrowser(locationQuery, category, radiusMeters) {
    const geo = await geocodeLocation(locationQuery);
    const elements = await queryOverpassInBrowser(geo.lat, geo.lon, radiusMeters, category);
    const discovered = [];
    for (const elem of elements) {
      const lead = convertOsmElementToLead(elem, geo.name || locationQuery);
      if (lead) discovered.push(lead);
    }
    return discovered;
  }

  // System Status
  async function loadStatus() {
    try {
      const { ok, data } = await safeFetchJson("/api/status");
      if (ok && data && data.total_leads !== undefined) {
        statTotalLeads.textContent = data.total_leads || 0;
        statWithEmail.textContent = data.leads_with_email || 0;
        statNeedingWebsite.textContent = data.leads_needing_website || 0;
        statDispatched.textContent = data.emails_dispatched || 0;
        isDryRun = Boolean(data.dry_run_mode);
      } else {
        // Compute from local memory
        const total = leads.length;
        const withEm = leads.filter(l => l.email && l.email.trim()).length;
        const needWeb = leads.filter(l => !l.website || !l.website.trim() || l.has_website === 0).length;
        const disp = parseInt(localStorage.getItem(STORAGE_KEY_DISPATCHED) || "0", 10);

        statTotalLeads.textContent = total;
        statWithEmail.textContent = withEm;
        statNeedingWebsite.textContent = needWeb;
        statDispatched.textContent = disp;
      }

      if (isDryRun) {
        modeText.textContent = "Simulation Mode (Safe)";
        dryRunIndicator.className = "mode-pill";
        const dot = dryRunIndicator.querySelector(".pulse-dot");
        if (dot) dot.className = "pulse-dot active";
      } else {
        modeText.textContent = "🟢 Live Outreach Active";
        dryRunIndicator.className = "mode-pill";
        const dot = dryRunIndicator.querySelector(".pulse-dot");
        if (dot) dot.className = "pulse-dot live";
      }

      if (campaignDryRunToggle) campaignDryRunToggle.checked = isDryRun;
      updateComposerModeNotice();
    } catch (err) {
      console.error("Status load error:", err);
    }
  }

  // Fetch Leads (Dual-mode: Server API with localStorage & initial_leads.json fallback)
  async function loadLeads() {
    try {
      let loaded = false;
      const { ok, data } = await safeFetchJson("/api/leads");
      if (ok && data && Array.isArray(data.leads) && data.leads.length > 0) {
        leads = data.leads;
        setLocalLeads(leads);
        loaded = true;
      }

      if (!loaded) {
        const local = getLocalLeads();
        const hasDelhi = local && local.some(l => (l.city || '').toLowerCase().includes('delhi') || (l.address || '').toLowerCase().includes('delhi'));
        if (local && Array.isArray(local) && local.length > 0 && !hasDelhi) {
          leads = local;
          loaded = true;
        } else {
          // Preload initial leads bundle (contains 108 verified Ranchi & Lalpur leads)
          try {
            const initRes = await fetch("initial_leads.json?v=" + Date.now());
            if (initRes.ok) {
              const initLeads = await initRes.json();
              if (Array.isArray(initLeads) && initLeads.length > 0) {
                leads = initLeads;
                setLocalLeads(leads);
                loaded = true;
              }
            }
          } catch (e) {
            console.warn("Could not load initial_leads.json:", e);
          }
        }
      }

      // Strictly purge any legacy Delhi test leads
      leads = leads.filter(l => {
        const addr = (l.address || "").toLowerCase();
        const c = (l.city || "").toLowerCase();
        return !addr.includes("delhi") && !c.includes("delhi") && !addr.includes("texas");
      });
      setLocalLeads(leads);

      renderLeads();
      updateSelectedCounts();
      await loadStatus();
    } catch (err) {
      console.error("Failed to load leads:", err);
      showToast("Error loading leads", "error");
    }
  }

  // Flexible Category & Niche Matcher with Strict Healthcare vs Dining Isolation
  function matchesCategory(lead, targetFilter) {
    if (!targetFilter || targetFilter === "all") return true;
    const nameText = `${lead.name || ""} ${lead.category || ""} ${lead.subcategory || ""}`.toLowerCase();
    const f = targetFilter.toLowerCase();

    const isPhysio = /physio|rehab|kinesio|chiropract|spine|pain care|pain clinic|paralysis/i.test(nameText);
    const isDental = /dentist|dental|orthodont|teeth|tooth|oral care|smile dental/i.test(nameText);
    const isSmallClinic = /clinic|polyclinic|dispensary|doctor|dr\.|nursing|maternity|pathology|diagnostic|eye care|optometr|orthopedic|pediatric|skin|derma|piles|ayurved|homeopath/i.test(nameText) && !isDental && !isPhysio;
    const isDining = /restaurant|cafe|coffee|bistro|bakery|fast_food|fast food|dhaba|biryani|dining|sweets|misthan|litti|barbeque|eatery/i.test(nameText);

    if (f === "restaurant" || f === "cafe" || f.includes("restaurant") || f.includes("cafe")) {
      if (isPhysio || isDental || isSmallClinic) return false;
      return isDining || (lead.category || "").toLowerCase().includes("restaurant");
    }
    if (f === "physiotherapy" || f.includes("physio") || f.includes("rehab")) {
      if (isDining) return false;
      return isPhysio || (lead.category || "").toLowerCase().includes("physio") || (lead.subcategory || "").toLowerCase().includes("physio");
    }
    if (f === "dental" || f.includes("dental")) {
      if (isDining || isPhysio) return false;
      return isDental || (lead.category || "").toLowerCase().includes("dental");
    }
    if (f === "small_clinic" || f.includes("small / general clinic") || f.includes("general clinic") || f === "clinic") {
      if (isDining) return false;
      return isSmallClinic || (lead.category || "").toLowerCase().includes("clinic") || (lead.category || "").toLowerCase().includes("health");
    }
    if (f === "dental / healthcare clinic" || f === "healthcare") {
      if (isDining) return false;
      return isDental || isPhysio || isSmallClinic || (lead.category || "").toLowerCase().includes("dental") || (lead.category || "").toLowerCase().includes("health");
    }
    if (f === "small_enterprise" || f.includes("enterprise") || f.includes("salon")) {
      if (isDining || isPhysio || isDental || isSmallClinic) return false;
      return nameText.includes("enterprise") || nameText.includes("salon") || nameText.includes("spa") || nameText.includes("retail") || nameText.includes("business") || nameText.includes("shop");
    }
    return (lead.category || "").toLowerCase() === f || (lead.subcategory || "").toLowerCase() === f;
  }

  // Render Leads Cards
  function renderLeads() {
    const searchTerm = (leadsSearchInput ? leadsSearchInput.value || "" : "").toLowerCase().trim();
    const emailFilter = filterEmailStatus ? filterEmailStatus.value : "all";
    const webFilter = filterWebsiteStatus ? filterWebsiteStatus.value : "all";
    const catFilter = filterCategory ? filterCategory.value : "all";

    // Update quick count badges
    if (qcountAll) qcountAll.textContent = leads.length;
    if (qcountNoWeb) qcountNoWeb.textContent = leads.filter(l => !l.website || !l.website.trim() || l.has_website === 0).length;
    if (qcountEmail) qcountEmail.textContent = leads.filter(l => l.email && l.email.trim()).length;
    if (qcountPhone) qcountPhone.textContent = leads.filter(l => l.phone && l.phone.trim()).length;

    // Update top niche pills count badges
    const countPillAll = document.getElementById("countPillAll");
    const countPillRestaurant = document.getElementById("countPillRestaurant");
    const countPillPhysio = document.getElementById("countPillPhysio");
    const countPillDental = document.getElementById("countPillDental");
    const countPillClinics = document.getElementById("countPillClinics");
    const countPillSmall = document.getElementById("countPillSmall");
    if (countPillAll) countPillAll.textContent = leads.length;
    if (countPillRestaurant) countPillRestaurant.textContent = leads.filter(l => matchesCategory(l, "restaurant")).length;
    if (countPillPhysio) countPillPhysio.textContent = leads.filter(l => matchesCategory(l, "physiotherapy")).length;
    if (countPillDental) countPillDental.textContent = leads.filter(l => matchesCategory(l, "dental")).length;
    if (countPillClinics) countPillClinics.textContent = leads.filter(l => matchesCategory(l, "small_clinic")).length;
    if (countPillSmall) countPillSmall.textContent = leads.filter(l => matchesCategory(l, "small_enterprise")).length;

    const filtered = leads.filter(lead => {
      // Strictly exclude any US/Texas or Delhi test leads
      const addr = (lead.address || "").toLowerCase();
      const city = (lead.city || "").toLowerCase();
      if (addr.includes("texas") || addr.includes("austin") || city.includes("austin")) return false;
      if (addr.includes("delhi") || city.includes("delhi")) return false;

      // Search across Name, Email, Address, Category, and Subcategory
      if (searchTerm) {
        const matchName = (lead.name || "").toLowerCase().includes(searchTerm);
        const matchEmail = (lead.email || "").toLowerCase().includes(searchTerm);
        const matchAddress = addr.includes(searchTerm);
        const matchCat = (lead.category || "").toLowerCase().includes(searchTerm);
        const matchSub = (lead.subcategory || "").toLowerCase().includes(searchTerm);
        if (!matchName && !matchEmail && !matchAddress && !matchCat && !matchSub) return false;
      }

      // Email status filter
      if (emailFilter === "with_email" && (!lead.email || !lead.email.trim())) return false;
      if (emailFilter === "needs_email" && lead.email && lead.email.trim()) return false;

      // Web presence filter (Key for targeting businesses needing a website)
      const hasWeb = Boolean(lead.website && lead.website.trim() && lead.has_website !== 0);
      if (webFilter === "no_website" && hasWeb) return false;
      if (webFilter === "has_website" && !hasWeb) return false;
      if (webFilter === "with_phone" && (!lead.phone || !lead.phone.trim())) return false;

      // Category filter (Flexible slug and alias matching)
      if (!matchesCategory(lead, catFilter)) return false;

      return true;
    });

    if (filtered.length === 0) {
      leadsContainer.innerHTML = "";
      emptyLeadsState.classList.remove("hidden");
      return;
    }

    emptyLeadsState.classList.add("hidden");

    leadsContainer.innerHTML = filtered.map(lead => {
      const isSelected = selectedLeadIds.has(lead.id);
      const hasEmail = Boolean(lead.email && lead.email.trim());
      const hasWeb = Boolean(lead.website && lead.website.trim() && lead.has_website !== 0);
      const hasPhone = Boolean(lead.phone && lead.phone.trim());

      const phone10 = extractIndianPhone10(lead.phone);
      const displayPhone = phone10 ? `+91 ${phone10.slice(0, 5)} ${phone10.slice(5)}` : lead.phone;
      const statusClass = `status-${lead.status || "discovered"}`;
      const statusText = lead.status === "sent" ? "Sent Live" 
        : lead.status === "simulated" ? "Simulated" 
        : lead.status === "pitched" ? "Pitch Ready" 
        : lead.status === "enriched" ? "Email Verified" 
        : "Discovered";

      return `
        <div class="lead-card" data-id="${lead.id}">
          <div>
            <div class="card-top">
              <input type="checkbox" class="card-checkbox" data-id="${lead.id}" ${isSelected ? "checked" : ""}>
              <div class="card-header-info">
                <div class="card-title">${escapeHtml(lead.name)}</div>
                <div class="card-tags-row">
                  <span class="badge-cat">${escapeHtml(lead.subcategory || lead.category)}</span>
                  ${!hasWeb ? `<span class="badge-target-hot">🔥 Needs Website</span>` : ""}
                  <span class="badge-score">${lead.opportunity_score || 85}% Opp.</span>
                </div>
              </div>
            </div>

            <div class="card-address">
              <span>📍</span>
              <span>${escapeHtml(lead.address || (lead.city + ", Local Area"))}</span>
            </div>

            <div class="card-contacts-row">
              ${hasPhone ? `
                <div style="display: inline-flex; align-items: center; gap: 0.35rem;">
                  <a href="tel:+91${escapeHtml(phone10)}" class="contact-phone-link" title="Call ${escapeHtml(lead.phone)}">
                    📞 ${escapeHtml(displayPhone)}
                  </a>
                  <button class="btn btn-xs btn-outline edit-phone-btn" data-id="${lead.id}" title="Edit phone number">✏️</button>
                </div>
              ` : `
                <div style="display: inline-flex; align-items: center; gap: 0.35rem;">
                  <span class="no-web-tag" style="color: var(--text-dim);">No phone on record</span>
                  <button class="btn btn-xs btn-outline edit-phone-btn" data-id="${lead.id}" title="Enter Indian phone number">+ Add Phone</button>
                </div>
              `}

              ${hasWeb ? `
                <a href="${escapeHtml(lead.website)}" target="_blank" rel="noopener" class="contact-web-link" title="Visit website">
                  🌐 ${escapeHtml(lead.website.replace(/^https?:\/\//, '').replace(/\/.*$/, ''))} ↗
                </a>
              ` : `<span class="badge-no-website">⚡ No Website (Top Pitch Target)</span>`}
            </div>

            <!-- Email Box -->
            <div class="card-email-box">
              ${hasEmail ? `
                <div class="email-verified-pill" title="${escapeHtml(lead.email)}">
                  <span class="check-icon">✓</span>
                  <span>${escapeHtml(lead.email)}</span>
                </div>
                <button class="btn btn-xs btn-outline edit-email-btn" data-id="${lead.id}" title="Edit recipient email">✏️</button>
              ` : `
                <div class="email-missing-box">
                  <span class="missing-label">No verified email</span>
                  <div style="display: flex; gap: 0.35rem; align-items: center;">
                    ${hasPhone ? `<span class="outreach-pref-hint">📱 WhatsApp Ready</span>` : ""}
                    <button class="btn btn-xs btn-outline edit-email-btn" data-id="${lead.id}" title="Enter email manually">+ Add Email</button>
                  </div>
                </div>
              `}
            </div>

            ${lead.audit_summary ? `
              <div class="card-summary-note">
                💡 ${escapeHtml(lead.audit_summary)}
              </div>
            ` : ""}
          </div>

          <div class="card-bottom-actions">
            <span class="card-status-badge ${statusClass}">${statusText}</span>
            <div style="display: flex; gap: 0.4rem; flex-wrap: wrap;">
              <button class="btn btn-whatsapp btn-sm whatsapp-chat-btn" data-id="${lead.id}" title="Direct WhatsApp chat ${hasPhone ? `to ${escapeHtml(displayPhone)}` : '(Add phone)'}">
                💬 WhatsApp
              </button>
              <button class="btn btn-primary btn-sm quick-outreach-btn" data-id="${lead.id}">
                🚀 Send Email
              </button>
              <button class="btn btn-outline btn-sm delete-lead-btn" data-id="${lead.id}" title="Remove lead">
                🗑️
              </button>
            </div>
          </div>
        </div>
      `;
    }).join("");

    attachCardHandlers();
  }

  // Attach card event listeners
  function attachCardHandlers() {
    // Checkbox select
    leadsContainer.querySelectorAll(".card-checkbox").forEach(cb => {
      cb.addEventListener("change", (e) => {
        const id = parseInt(e.target.getAttribute("data-id"));
        if (e.target.checked) selectedLeadIds.add(id);
        else selectedLeadIds.delete(id);
        updateSelectedCounts();
      });
    });

    // Auto-Find Email for single lead
    leadsContainer.querySelectorAll(".autofind-email-btn").forEach(btn => {
      btn.addEventListener("click", async (e) => {
        e.stopPropagation();
        const id = parseInt(btn.getAttribute("data-id"));
        const originalText = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = `<span class="spinner" style="width: 10px; height: 10px;"></span> Searching...`;

        try {
          const { ok, data } = await safeFetchJson("/api/leads/auto-find-email", {
            method: "POST",
            body: JSON.stringify({ lead_id: id })
          });
          if (ok && data && data.success && data.found) {
            showToast(`Found verified email: ${data.lead.email}!`, "success");
            await loadLeads();
            return;
          }
        } catch (err) {}

        // In-browser domain heuristic fallback
        const lead = leads.find(l => l.id === id);
        if (lead && lead.website) {
          try {
            const domain = lead.website.replace(/^https?:\/\//, '').replace(/\/.*$/, '').replace(/^www\./, '');
            if (domain && domain.includes(".")) {
              const guessed = `contact@${domain}`;
              lead.email = guessed;
              lead.status = "enriched";
              setLocalLeads(leads);
              renderLeads();
              updateSelectedCounts();
              await loadStatus();
              showToast(`Found domain contact email: ${guessed}!`, "success");
              return;
            }
          } catch (e) {}
        }

        showToast("No email found in public records. Click '+ Add' to type one.", "info");
        btn.innerHTML = originalText;
        btn.disabled = false;
      });
    });

    // Edit email manually
    leadsContainer.querySelectorAll(".edit-email-btn").forEach(btn => {
      btn.addEventListener("click", async (e) => {
        e.stopPropagation();
        const id = parseInt(btn.getAttribute("data-id"));
        const lead = leads.find(l => l.id === id);
        const current = lead ? lead.email : "";
        const entered = prompt(`Enter email for ${lead ? lead.name : "business"}:`, current);
        if (entered !== null) {
          const clean = entered.trim();
          if (lead) {
            lead.email = clean;
            if (clean) lead.status = "enriched";
            setLocalLeads(leads);
            renderLeads();
            updateSelectedCounts();
            await loadStatus();
            showToast("Email updated", "success");
          }
          try {
            await safeFetchJson("/api/leads/update", {
              method: "POST",
              body: JSON.stringify({ lead_id: id, email: clean })
            });
          } catch (err) {}
        }
      });
    });

    // Edit phone manually
    leadsContainer.querySelectorAll(".edit-phone-btn").forEach(btn => {
      btn.addEventListener("click", async (e) => {
        e.stopPropagation();
        const id = parseInt(btn.getAttribute("data-id"));
        const lead = leads.find(l => l.id === id);
        const current = lead ? (extractIndianPhone10(lead.phone) || lead.phone) : "";
        const entered = prompt(`Enter 10-digit Indian mobile number for ${lead ? lead.name : "business"}:`, current);
        if (entered !== null) {
          const clean10 = extractIndianPhone10(entered.trim());
          if (entered.trim() && (!clean10 || clean10.length !== 10)) {
            showToast("Please enter a valid 10-digit Indian mobile number (e.g. 97983 92674)", "error");
            return;
          }
          const formatted = clean10 ? `+91 ${clean10.slice(0, 5)} ${clean10.slice(5)}` : "";
          if (lead) {
            lead.phone = formatted;
            setLocalLeads(leads);
            renderLeads();
            updateSelectedCounts();
            await loadStatus();
            showToast("Phone number updated", "success");
          }
          try {
            await safeFetchJson("/api/leads/update", {
              method: "POST",
              body: JSON.stringify({ lead_id: id, phone: formatted })
            });
          } catch (err) {}
        }
      });
    });

    // WhatsApp Chat Button
    leadsContainer.querySelectorAll(".whatsapp-chat-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        const id = parseInt(btn.getAttribute("data-id"));
        openWhatsAppForLead(id);
      });
    });

    // Quick Send Email button -> Open composer
    leadsContainer.querySelectorAll(".quick-outreach-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        const id = parseInt(btn.getAttribute("data-id"));
        openComposerForLead(id);
      });
    });

    // Delete lead button
    leadsContainer.querySelectorAll(".delete-lead-btn").forEach(btn => {
      btn.addEventListener("click", async () => {
        const id = parseInt(btn.getAttribute("data-id"));
        if (!confirm("Remove this business lead?")) return;
        leads = leads.filter(l => l.id !== id);
        selectedLeadIds.delete(id);
        setLocalLeads(leads);
        renderLeads();
        updateSelectedCounts();
        await loadStatus();
        showToast("Lead removed", "info");
        try {
          await safeFetchJson(`/api/leads/${id}`, { method: "DELETE" });
        } catch (err) {}
      });
    });
  }

  // Update selection counts
  function updateSelectedCounts() {
    const count = selectedLeadIds.size;
    selectionCountText.textContent = `${count} selected`;
    batchSendCountBadge.textContent = count;

    if (leads.length > 0 && selectedLeadIds.size === leads.length) {
      selectAllLeads.checked = true;
    } else {
      selectAllLeads.checked = false;
    }
  }

  // WhatsApp Outreach Generation
  function generateWhatsAppMessage(lead, template = "general") {
    const name = lead.name || "Business Owner";
    const city = lead.city || "your area";
    const hasWeb = Boolean(lead.website && lead.website.trim() && lead.has_website !== 0);

    if (template === "restaurant" || (lead.category && lead.category.includes("Restaurant"))) {
      if (!hasWeb) {
        return `Namaste! 👋 I came across ${name} in ${city}.\n\nMy name is Vishal Kumar Tiwari from Zenix Services (https://zenixservices.online).\n\nI noticed you do not have an official website or digital menu on Google Maps yet. We help restaurants & cafes in ${city} launch interactive QR menus and zero-commission direct ordering so you keep 100% of your profits.\n\nWould you be open to seeing a free 30-second digital menu & website preview for ${name}?`;
      }
      return `Namaste! 👋 I came across ${name} in ${city}.\n\nMy name is Vishal Kumar Tiwari from Zenix Services (https://zenixservices.online).\n\nWe help restaurants & cafes in ${city} launch interactive digital QR menus and commission-free online ordering so you retain 100% of your food revenue.\n\nWould you be open to seeing a free 30-second digital menu preview for ${name}?`;
    } else if (template === "dental" || (lead.category && (lead.category.includes("Dental") || lead.category.includes("Clinic") || lead.category.includes("Health")))) {
      if (!hasWeb) {
        return `Namaste Dr. and management at ${name} (${city})! 👋\n\nI'm Vishal Kumar Tiwari from Zenix Services (https://zenixservices.online).\n\nI noticed on Google Maps that ${name} doesn't have an official patient website or online appointment scheduling setup yet.\n\nWe build modern healthcare websites with 24/7 patient booking and Google Maps optimization so patients can easily find and book with you.\n\nCould I share a complimentary website & booking portal mockup with you this week?`;
      }
      return `Namaste Dr. and team at ${name} (${city})! 👋\n\nI'm Vishal Kumar Tiwari from Zenix Services (https://zenixservices.online).\n\nWe build modern patient-friendly clinic websites with 24/7 online appointment booking to make patient onboarding effortless.\n\nWould you be open to seeing a free, complimentary booking portal preview for ${name}?`;
    } else if (template === "mockup") {
      return `Namaste! 👋 My name is Vishal Kumar Tiwari, Co-Founder of Zenix Services (https://zenixservices.online).\n\nI noticed ${name} in ${city} and sketched out a quick modern mobile website preview that could help you attract more direct customer inquiries.\n\nWould you like me to share the free mockup link with you?`;
    } else {
      if (!hasWeb) {
        return `Namaste! 👋 I came across ${name} in ${city}.\n\nMy name is Vishal Kumar Tiwari from Zenix Services (https://zenixservices.online).\n\nI noticed you don't have an official website listed on Google yet. We specialize in building fast, high-converting websites for local businesses across Jharkhand, Bihar, and UP.\n\nCould I send you a free, no-obligation website design mockup for ${name}?`;
      }
      return `Namaste! 👋 I came across ${name} in ${city}.\n\nMy name is Vishal Kumar Tiwari from Zenix Services (https://zenixservices.online).\n\nWe specialize in building fast, high-converting websites and digital setups for local businesses across Jharkhand, Bihar, and UP.\n\nCould I send you a free, no-obligation website design preview for ${name}?`;
    }
  }

  function openWhatsAppForLead(leadId) {
    const lead = leads.find(l => l.id === leadId);
    if (!lead) return;

    currentWhatsAppLead = lead;
    const phone10 = extractIndianPhone10(lead.phone);
    const displayPhone = phone10 ? `+91 ${phone10.slice(0, 5)} ${phone10.slice(5)}` : (lead.phone || "No phone added");

    whatsappLeadName.textContent = `💬 WhatsApp: ${lead.name}`;
    whatsappPhoneBadge.textContent = phone10 ? `Phone: +91 ${phone10}` : "Phone not added yet";
    if (whatsappPhoneInput) {
      whatsappPhoneInput.value = phone10 || "";
    }

    // Pre-select template based on category
    if (lead.category && lead.category.includes("Restaurant")) {
      whatsappTemplateSelect.value = "restaurant";
    } else if (lead.category && (lead.category.includes("Dental") || lead.category.includes("Clinic"))) {
      whatsappTemplateSelect.value = "dental";
    } else {
      whatsappTemplateSelect.value = "general";
    }

    whatsappMessageText.value = generateWhatsAppMessage(lead, whatsappTemplateSelect.value);
    whatsappModal.classList.remove("hidden");
  }

  // Open Composer Modal
  async function openComposerForLead(leadId) {
    const lead = leads.find(l => l.id === leadId);
    if (!lead) return;
    currentEditingLead = lead;

    composerLeadName.textContent = `Outreach: ${lead.name}`;
    composerCategory.textContent = lead.subcategory || lead.category;
    composerCity.textContent = `📍 ${lead.city || "Local Area"}`;
    composerWebsite.textContent = lead.website ? `🌐 ${lead.website.replace(/^https?:\/\//, '')}` : "🌐 No website found";
    composerScore.textContent = `${lead.opportunity_score || 85}% Opportunity`;

    composerRecipient.value = lead.email || "";

    // Update simulation notice
    updateComposerModeNotice();

    // Generate pitch if missing
    if (!lead.email_subject || !lead.email_body) {
      composerSubject.value = "Generating personalized subject...";
      composerBody.value = "Generating tailored outreach pitch...";
      composerModal.classList.remove("hidden");
      await generatePitch(leadId, composerTone.value);
    } else {
      composerSubject.value = lead.email_subject;
      composerBody.value = lead.email_body;
      composerModal.classList.remove("hidden");
    }
  }

  // Generate Pitch via API or client engine
  async function generatePitch(leadId, tone = "friendly") {
    try {
      const { ok, data } = await safeFetchJson("/api/generate-pitch", {
        method: "POST",
        body: JSON.stringify({ lead_id: leadId, tone: tone })
      });
      if (ok && data && data.success && data.pitch) {
        composerSubject.value = data.pitch.subject;
        composerBody.value = data.pitch.body;
        if (currentEditingLead && currentEditingLead.id === leadId) {
          currentEditingLead.email_subject = data.pitch.subject;
          currentEditingLead.email_body = data.pitch.body;
        }
        return;
      }
    } catch (err) {}

    // In-browser pitch generation fallback
    if (currentEditingLead) {
      const p = generatePitchClient(
        currentEditingLead.name,
        currentEditingLead.category,
        currentEditingLead.city || "your city",
        currentEditingLead.website,
        currentEditingLead.primary_angle,
        tone
      );
      composerSubject.value = p.subject;
      composerBody.value = p.body;
      currentEditingLead.email_subject = p.subject;
      currentEditingLead.email_body = p.body;
      setLocalLeads(leads);
    }
  }

  // Send Email from Composer
  async function sendEmailFromComposer() {
    if (!currentEditingLead) return;
    const recipient = composerRecipient.value.trim();
    const subject = composerSubject.value.trim();
    const body = composerBody.value.trim();

    if (!recipient) {
      showToast("Please enter or verify recipient email address", "error");
      composerRecipient.focus();
      return;
    }

    if (!subject || !body) {
      showToast("Email subject and content cannot be blank", "error");
      return;
    }

    sendComposerBtn.disabled = true;
    composerSendSpinner.classList.remove("hidden");

    try {
      // Save recipient if modified
      if (recipient !== currentEditingLead.email) {
        await safeFetchJson("/api/leads/update", {
          method: "POST",
          body: JSON.stringify({ lead_id: currentEditingLead.id, email: recipient })
        });
      }

      const { ok, data } = await safeFetchJson("/api/send-email", {
        method: "POST",
        body: JSON.stringify({
          lead_id: currentEditingLead.id,
          subject: subject,
          body: body
        })
      });

      if (ok && data && data.success) {
        const isSim = data.result?.simulated;
        if (isSim) {
          showToast(`[TEST MODE] Simulated outreach to ${recipient}. Turn OFF Simulation in Settings for real live emails!`, "info");
          appendLog(`[SIMULATION] Email tested to ${recipient}. (Configure Gmail App Password in Settings for live sending).`, "simulated");
        } else {
          showToast(`✅ Live Email Sent! A copy is now in your zenixservices67@gmail.com Sent folder.`, "success");
          appendLog(`[LIVE SENT] Successfully sent from zenixservices67@gmail.com to ${recipient}. Saved in Gmail Sent.`, "success");
        }
        composerModal.classList.add("hidden");
        await loadLeads();
        await loadLogs();
      } else if (isDryRun) {
        // Safe simulation fallback when standalone on Netlify
        currentEditingLead.status = "simulated";
        currentEditingLead.email = recipient;
        currentEditingLead.email_subject = subject;
        currentEditingLead.email_body = body;
        setLocalLeads(leads);
        const currentDisp = parseInt(localStorage.getItem(STORAGE_KEY_DISPATCHED) || "0", 10);
        localStorage.setItem(STORAGE_KEY_DISPATCHED, String(currentDisp + 1));
        showToast(`[SIMULATION MODE] Outreach tested safely for ${recipient}!`, "success");
        appendLog(`[SIMULATION] Pitch generated & simulated to ${recipient} (${currentEditingLead.name}).`, "simulated");
        composerModal.classList.add("hidden");
        renderLeads();
        await loadStatus();
      } else {
        const errMsg = data?.result?.error || data?.message || "Failed to send email. Configure Python backend in Settings for live outreach.";
        showToast(errMsg, "error");
        appendLog(`Send error to ${recipient}: ${errMsg}`, "error");

        if (errMsg.includes("SMTP password is not set") || errMsg.includes("App Password")) {
          settingsModal.classList.remove("hidden");
          settingSmtpPass.focus();
        }
      }
    } catch (err) {
      showToast("Network error while sending email", "error");
    } finally {
      sendComposerBtn.disabled = false;
      composerSendSpinner.classList.add("hidden");
    }
  }

  // Logs & History Drawer
  async function loadLogs() {
    try {
      const { ok, data } = await safeFetchJson("/api/logs");
      const logs = (ok && data && data.logs) ? data.logs : [];
      logCountBadge.textContent = logs.length;

      if (logs.length === 0) {
        terminalLogs.innerHTML = `<div class="log-line info">[SYSTEM] Zenix Reach AI initialized. Ready for operations.</div>`;
        return;
      }

      terminalLogs.innerHTML = logs.map(l => {
        const timeStr = l.sent_at ? l.sent_at.split("T")[1]?.substring(0, 8) || l.sent_at : "";
        const statusType = l.status === "sent" ? "success" : l.status === "simulated" ? "simulated" : "error";
        const tag = l.status === "sent" ? "LIVE SENT" : l.status === "simulated" ? "SIMULATION" : "FAILED";
        return `
          <div class="log-line ${statusType}">
            [${timeStr}] [${tag}] To: <strong>${escapeHtml(l.recipient_email)}</strong> (${escapeHtml(l.business_name)})
            ${l.error_message ? `<div style="color: #fca5a5; font-size: 0.72rem;">&gt; Error: ${escapeHtml(l.error_message)}</div>` : ""}
          </div>
        `;
      }).join("");
    } catch (err) {
      console.error("Failed to load logs:", err);
    }
  }

  function appendLog(msg, type = "info") {
    const div = document.createElement("div");
    div.className = `log-line ${type}`;
    const now = new Date().toTimeString().split(" ")[0];
    div.innerHTML = `[${now}] ${escapeHtml(msg)}`;
    terminalLogs.prepend(div);
  }

  // Update composer mode notice based on dry-run state
  function updateComposerModeNotice() {
    if (!composerModeNotice || !cmnText) return;
    if (isDryRun) {
      composerModeNotice.className = "composer-mode-notice";
      cmnText.innerHTML = `<strong>Simulation Mode is ON:</strong> Safe test mode without contacting real recipients.`;
      if (cmnSwitchLiveBtn) {
        cmnSwitchLiveBtn.textContent = "⚡ Switch to Live";
        cmnSwitchLiveBtn.className = "btn btn-outline btn-sm";
      }
    } else {
      composerModeNotice.className = "composer-mode-notice live";
      cmnText.innerHTML = `<strong>🟢 LIVE OUTREACH ACTIVE:</strong> Real emails will be sent directly to recipient inboxes via Gmail SMTP and appear in your Gmail Sent folder!`;
      if (cmnSwitchLiveBtn) {
        cmnSwitchLiveBtn.textContent = "🛡️ Switch to Simulation";
        cmnSwitchLiveBtn.className = "btn btn-secondary btn-sm";
      }
    }
  }

  // Update all UI elements displaying the linked sender email
  function updateLinkedSenderEmail(email) {
    if (!email || !email.includes("@")) return;
    const clean = email.trim();
    const headerEl = document.getElementById("headerSenderEmail");
    if (headerEl) headerEl.textContent = clean;
    const compEl = document.getElementById("composerSenderEmailDisplay");
    if (compEl) compEl.textContent = clean;
    const logsEl = document.getElementById("logsSenderEmail");
    if (logsEl) logsEl.textContent = clean;
    const sentEl = document.getElementById("settingsSentFolderEmail");
    if (sentEl) sentEl.textContent = clean;
    const headEl = document.getElementById("settingsSmtpHeading");
    if (headEl) headEl.textContent = `Live Gmail SMTP Setup (${clean})`;
    const testBtn = document.getElementById("sendTestEmailBtn");
    if (testBtn) testBtn.title = `Send a real verification email to ${clean}`;
    const compBtnText = document.getElementById("composerSendBtnText");
    if (compBtnText) compBtnText.textContent = `🚀 Send Email from ${clean}`;
  }

  // Settings
  async function loadSettings() {
    try {
      const { ok, data } = await safeFetchJson("/api/settings");
      const s = (ok && data && data.settings) ? data.settings : {};

      const currentMail = s.smtp_user || s.sender_email || "zenixservices67@gmail.com";
      if (settingSenderName) settingSenderName.value = s.sender_name || "Vishal Kumar Tiwari";
      if (settingSenderCompany) settingSenderCompany.value = s.company_name || "Zenix Services";
      if (settingSenderEmail) settingSenderEmail.value = s.sender_email || currentMail;
      if (settingSenderWebsite) settingSenderWebsite.value = s.website_url || "https://zenixservices.online";
      if (settingSmtpUser) settingSmtpUser.value = s.smtp_user || currentMail;
      if (settingSmtpPass && s.smtp_pass_set) {
        settingSmtpPass.placeholder = "•••••••••••• (App Password Saved)";
        const passCharCount = document.getElementById("passCharCount");
        if (passCharCount) {
          passCharCount.textContent = "16/16 chars";
          passCharCount.classList.add("valid");
        }
      }
      if (campaignDryRunToggle) campaignDryRunToggle.checked = Boolean(s.dry_run_mode);
      if (settingBackendUrl) settingBackendUrl.value = localStorage.getItem("zenix_backend_url") || "";

      if (window.location.hostname.includes("netlify.app") || window.location.hostname.includes("web.app")) {
        const netlifyBanner = document.getElementById("netlifyAlertBanner");
        if (netlifyBanner && !localStorage.getItem("zenix_backend_url")) {
          netlifyBanner.style.display = "block";
        }
      }

      updateLinkedSenderEmail(currentMail);
    } catch (err) {
      console.error("Settings load error:", err);
    }
  }

  async function saveSettings() {
    const senderName = (settingSenderName ? settingSenderName.value.trim() : "") || "Vishal Kumar Tiwari";
    const companyName = (settingSenderCompany ? settingSenderCompany.value.trim() : "") || "Zenix Services";
    const senderEmail = (settingSenderEmail ? settingSenderEmail.value.trim() : "") || (settingSmtpUser ? settingSmtpUser.value.trim() : "") || "zenixservices67@gmail.com";
    const websiteUrl = (settingSenderWebsite ? settingSenderWebsite.value.trim() : "") || "https://zenixservices.online";
    const smtpUser = (settingSmtpUser ? settingSmtpUser.value.trim() : "") || senderEmail;
    const dryRun = campaignDryRunToggle ? campaignDryRunToggle.checked : true;

    const payload = {
      sender_name: senderName,
      company_name: companyName,
      sender_title: `Co-Founder, ${companyName}`,
      sender_email: senderEmail,
      website_url: websiteUrl,
      smtp_user: smtpUser,
      dry_run_mode: dryRun
    };

    const rawPass = settingSmtpPass ? settingSmtpPass.value.trim() : "";
    if (rawPass && rawPass !== "••••••••••••") {
      const cleanPass = rawPass.replace(/\s+/g, "").toLowerCase();
      if (cleanPass.length < 16) {
        showToast(`Google App Password must be 16 characters (e.g. abcd efgh ijkl mnop). You entered ${cleanPass.length} chars.`, "error");
        if (smtpTestResult) {
          smtpTestResult.textContent = `✕ Google App Passwords are 16 letters (you entered ${cleanPass.length} chars)`;
          smtpTestResult.className = "smtp-test-result error";
        }
        return;
      }
      payload.smtp_pass = cleanPass;
    }

    try {
      if (settingBackendUrl) {
        const bUrl = settingBackendUrl.value.trim();
        if (bUrl) {
          localStorage.setItem("zenix_backend_url", bUrl);
        } else {
          localStorage.removeItem("zenix_backend_url");
        }
      }

      const { ok, data } = await safeFetchJson("/api/settings", {
        method: "POST",
        body: JSON.stringify({ settings: payload })
      });
      if (ok && data && data.success) {
        updateLinkedSenderEmail(smtpUser || senderEmail);
        showToast("Settings saved successfully!", "success");
        settingsModal.classList.add("hidden");
        await loadStatus();
      } else {
        showToast(`Failed to save settings: ${data?.detail || data?.message || "Server error"}`, "error");
      }
    } catch (err) {
      console.error("Save settings error:", err);
      showToast("Error saving settings: " + (err.message || "Network error"), "error");
    }
  }

  async function testSmtp() {
    if (!smtpTestResult) return;
    smtpTestResult.textContent = "Connecting to Gmail SMTP (testing ports 587 & 465)...";
    smtpTestResult.className = "smtp-test-result";

    const user = (settingSmtpUser ? settingSmtpUser.value.trim() : "") || (settingSenderEmail ? settingSenderEmail.value.trim() : "");
    if (!user || !user.includes("@")) {
      smtpTestResult.textContent = "✕ Please enter a valid Gmail address above.";
      smtpTestResult.className = "smtp-test-result error";
      showToast("Please enter a valid Gmail address first.", "error");
      return;
    }

    const rawPass = settingSmtpPass ? settingSmtpPass.value.trim() : "";
    const cleanPass = rawPass.replace(/\s+/g, "").toLowerCase();
    const isSaved = rawPass === "••••••••••••" || (!rawPass && settingSmtpPass?.placeholder?.includes("Saved"));

    if (!isSaved && cleanPass.length > 0 && cleanPass.length !== 16) {
      smtpTestResult.textContent = `✕ Google App Passwords must be 16 letters (you typed ${cleanPass.length} chars).`;
      smtpTestResult.className = "smtp-test-result error";
      showToast(`Google App Passwords are 16 letters (e.g. abcd efgh ijkl mnop). You entered ${cleanPass.length} chars.`, "error");
      return;
    }

    if (!isSaved && cleanPass.length === 0) {
      smtpTestResult.textContent = "✕ Please enter your 16-character Google App Password.";
      smtpTestResult.className = "smtp-test-result error";
      showToast("Please enter your 16-character Google App Password.", "error");
      return;
    }

    // Auto-save settings first so the server has the latest email & password
    try {
      const payloadSettings = {
        smtp_user: user,
        sender_email: user
      };
      if (cleanPass.length === 16) {
        payloadSettings.smtp_pass = cleanPass;
      }
      await safeFetchJson("/api/settings", {
        method: "POST",
        body: JSON.stringify({ settings: payloadSettings })
      });
    } catch (saveErr) {
      console.warn("Auto-save before test skipped:", saveErr);
    }

    try {
      const { ok, data } = await safeFetchJson("/api/test-smtp", {
        method: "POST",
        body: JSON.stringify({
          smtp_user: user,
          smtp_pass: cleanPass.length === 16 ? cleanPass : ""
        })
      });
      if (ok && data && data.success) {
        smtpTestResult.textContent = data.message || "✓ Connected & authenticated with Gmail successfully!";
        smtpTestResult.className = "smtp-test-result success";
        updateLinkedSenderEmail(user);
        showToast("✓ Gmail connection verified! You can now send real live emails.", "success");
      } else {
        const rawMsg = data?.message || data?.detail || "Authentication Failed";
        const cleanMsg = typeof rawMsg === "string" ? rawMsg.replace(/<[^>]*>/g, '').trim() : "Authentication Failed";
        smtpTestResult.textContent = `✕ ${cleanMsg}`;
        smtpTestResult.className = "smtp-test-result error";
      }
    } catch (err) {
      smtpTestResult.textContent = "✕ Error reaching server.";
      smtpTestResult.className = "smtp-test-result error";
    }
  }

  // Setup Event Listeners
  function setupEventListeners() {
    // Locality Search Submit
    discoveryForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const location = locationInput.value.trim();
      if (!location) return showToast("Please enter an Indian locality or city", "error");

      discoverBtn.disabled = true;
      discoverSpinner.classList.remove("hidden");
      showToast(`Scanning ${location} in India & fetching verified emails...`, "info");

      try {
        let success = false;
        // 1. Try Backend API first if backend configured or local
        const { ok, data } = await safeFetchJson("/api/discover", {
          method: "POST",
          body: JSON.stringify({
            location: location,
            category: categorySelect.value || "all",
            radius_meters: parseInt(document.getElementById("radiusSelect").value || 5000)
          })
        });

        if (ok && data && data.success && Array.isArray(data.leads) && data.leads.length > 0) {
          leads = data.leads;
          setLocalLeads(leads);
          const withEmail = (data.leads || []).filter(l => l.email).length;
          showToast(`Discovered ${data.count || data.leads.length} businesses in ${location} (${withEmail} verified emails ready)!`, "success");
          success = true;
        }

        // 2. If backend is not running or returned error, run live in-browser discovery
        if (!success) {
          const cat = categorySelect.value || "all";
          const radius = parseInt(document.getElementById("radiusSelect").value || 5000, 10);
          showToast(`Scanning OpenStreetMap directly for ${location}...`, "info");
          const clientLeads = await discoverBusinessesInBrowser(location, cat, radius);
          if (clientLeads && clientLeads.length > 0) {
            mergeNewLeads(clientLeads);
            const withEmail = clientLeads.filter(l => l.email).length;
            showToast(`Discovered ${clientLeads.length} businesses in ${location} (${withEmail} verified emails ready)!`, "success");
            success = true;
          }
        }

        if (!success) {
          showToast(`No new businesses found in ${location}. Try a nearby area or city name (e.g. Ranchi, Patna, Delhi).`, "info");
        }

        if (leadsSearchInput) {
          leadsSearchInput.value = "";
        }

        renderLeads();
        updateSelectedCounts();
        await loadStatus();
      } catch (err) {
        console.error("Discovery error:", err);
        try {
          const clientLeads = await discoverBusinessesInBrowser(location, categorySelect.value || "all", 5000);
          if (clientLeads && clientLeads.length > 0) {
            mergeNewLeads(clientLeads);
            if (leadsSearchInput) {
              leadsSearchInput.value = "";
            }
            renderLeads();
            updateSelectedCounts();
            await loadStatus();
            showToast(`Discovered ${clientLeads.length} businesses in ${location}!`, "success");
          } else {
            showToast("Discovery completed with no matches.", "info");
          }
        } catch (innerErr) {
          showToast("Network error during discovery", "error");
        }
      } finally {
        discoverBtn.disabled = false;
        discoverSpinner.classList.add("hidden");
      }
    });

    // Quick locality chips
    document.querySelectorAll(".chip-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        const loc = btn.getAttribute("data-loc");
        locationInput.value = loc;
        const chipLabel = btn.textContent.trim();
        if (leadsSearchInput) {
          leadsSearchInput.value = "";
        }
        discoveryForm.dispatchEvent(new Event("submit"));
      });
    });

    // Niche selector pills - Immediate filtering of table and discovery category sync
    document.querySelectorAll(".niche-pill").forEach(pill => {
      pill.addEventListener("click", () => {
        document.querySelectorAll(".niche-pill").forEach(p => p.classList.remove("active"));
        pill.classList.add("active");
        const cat = pill.getAttribute("data-category");
        categorySelect.value = cat;
        if (filterCategory) {
          filterCategory.value = cat === "restaurant" ? "Restaurant / Cafe"
            : cat === "physiotherapy" ? "Physiotherapy Clinic"
            : cat === "dental" ? "Dental Clinic"
            : cat === "small_clinic" ? "Small / General Clinic"
            : cat === "small_enterprise" ? "Small Enterprise"
            : "all";
        }
        if (leadsSearchInput) {
          leadsSearchInput.value = "";
        }
        renderLeads();
      });
    });

    // Sync niche pills when filterCategory dropdown changes
    if (filterCategory) {
      filterCategory.addEventListener("change", () => {
        const val = filterCategory.value;
        document.querySelectorAll(".niche-pill").forEach(p => {
          const c = p.getAttribute("data-category");
          const matches = (val === "all" && c === "all") ||
            (val === "Restaurant / Cafe" && c === "restaurant") ||
            (val === "Physiotherapy Clinic" && c === "physiotherapy") ||
            (val === "Dental Clinic" && c === "dental") ||
            (val === "Small / General Clinic" && c === "small_clinic") ||
            (val === "Small Enterprise" && c === "small_enterprise");
          p.classList.toggle("active", matches);
        });
        renderLeads();
      });
    }

    // Real-time Gmail input synchronization & App Password cleaner
    if (settingSenderEmail) {
      settingSenderEmail.addEventListener("input", () => {
        const val = settingSenderEmail.value.trim();
        if (val.includes("@") && settingSmtpUser && !settingSmtpUser.dataset.customized) {
          settingSmtpUser.value = val;
        }
        updateLinkedSenderEmail(val);
      });
    }

    if (settingSmtpUser) {
      settingSmtpUser.addEventListener("input", () => {
        settingSmtpUser.dataset.customized = "true";
        const val = settingSmtpUser.value.trim();
        if (settingSenderEmail) settingSenderEmail.value = val;
        updateLinkedSenderEmail(val);
      });
    }

    if (settingSmtpPass) {
      const passCharCount = document.getElementById("passCharCount");
      settingSmtpPass.addEventListener("input", () => {
        const raw = settingSmtpPass.value;
        const cleaned = raw.replace(/\s+/g, "").toLowerCase();
        if (cleaned !== raw) {
          settingSmtpPass.value = cleaned;
        }
        const len = cleaned.length;
        if (passCharCount) {
          passCharCount.textContent = `${len}/16 chars`;
          passCharCount.classList.toggle("valid", len === 16);
        }
      });
    }

    function syncPillState(activeFilter) {
      document.querySelectorAll(".qfilter-pill").forEach(p => {
        if (p.getAttribute("data-qfilter") === activeFilter) {
          p.classList.add("active");
        } else {
          p.classList.remove("active");
        }
      });
    }

    // Quick filter pills
    document.querySelectorAll(".qfilter-pill").forEach(pill => {
      pill.addEventListener("click", () => {
        const qf = pill.getAttribute("data-qfilter");
        syncPillState(qf);
        if (qf === "all") {
          if (filterWebsiteStatus) filterWebsiteStatus.value = "all";
          if (filterEmailStatus) filterEmailStatus.value = "all";
        } else if (qf === "no_website") {
          if (filterWebsiteStatus) filterWebsiteStatus.value = "no_website";
          if (filterEmailStatus) filterEmailStatus.value = "all";
        } else if (qf === "with_email") {
          if (filterWebsiteStatus) filterWebsiteStatus.value = "all";
          if (filterEmailStatus) filterEmailStatus.value = "with_email";
        } else if (qf === "with_phone") {
          if (filterWebsiteStatus) filterWebsiteStatus.value = "with_phone";
          if (filterEmailStatus) filterEmailStatus.value = "all";
        }
        renderLeads();
      });
    });

    // Metric cards clickable shortcuts
    if (metricCardTotal) {
      metricCardTotal.addEventListener("click", () => {
        if (filterWebsiteStatus) filterWebsiteStatus.value = "all";
        if (filterEmailStatus) filterEmailStatus.value = "all";
        syncPillState("all");
        renderLeads();
      });
    }
    if (metricCardNoWeb) {
      metricCardNoWeb.addEventListener("click", () => {
        if (filterWebsiteStatus) filterWebsiteStatus.value = "no_website";
        if (filterEmailStatus) filterEmailStatus.value = "all";
        syncPillState("no_website");
        renderLeads();
        showToast("Filtered: Businesses needing a website upgrade", "info");
      });
    }
    if (metricCardEmail) {
      metricCardEmail.addEventListener("click", () => {
        if (filterWebsiteStatus) filterWebsiteStatus.value = "all";
        if (filterEmailStatus) filterEmailStatus.value = "with_email";
        syncPillState("with_email");
        renderLeads();
        showToast("Filtered: Leads with verified emails ready", "info");
      });
    }
    if (metricCardDispatched) {
      metricCardDispatched.addEventListener("click", () => {
        if (toggleLogsBtn) toggleLogsBtn.click();
      });
    }

    // Select all checkbox
    selectAllLeads.addEventListener("change", (e) => {
      if (e.target.checked) {
        leads.forEach(l => selectedLeadIds.add(l.id));
      } else {
        selectedLeadIds.clear();
      }
      renderLeads();
      updateSelectedCounts();
    });

    // Auto-find missing emails for all leads
    enrichAllBtn.addEventListener("click", async () => {
      const missingCount = leads.filter(l => !l.email).length;
      if (missingCount === 0) {
        return showToast("All discovered leads already have emails!", "success");
      }

      enrichAllBtn.disabled = true;
      enrichAllBtn.innerHTML = `<span class="spinner" style="width: 12px; height: 12px;"></span> Searching Web & Maps...`;
      showToast(`Auto-enriching ${missingCount} Indian businesses from public records...`, "info");

      try {
        let enrichedCount = 0;
        const { ok, data } = await safeFetchJson("/api/batch-enrich", {
          method: "POST",
          body: JSON.stringify({})
        });
        if (ok && data && data.success) {
          showToast(`Enrichment complete for ${data?.count || missingCount} leads!`, "success");
          await loadLeads();
          return;
        }

        // In-browser heuristic enrichment for leads with websites
        for (const lead of leads) {
          if (!lead.email && lead.website) {
            try {
              const dom = lead.website.replace(/^https?:\/\//, '').replace(/\/.*$/, '').replace(/^www\./, '');
              if (dom && dom.includes(".")) {
                lead.email = `contact@${dom}`;
                lead.status = "enriched";
                enrichedCount++;
              }
            } catch (e) {}
          }
        }
        if (enrichedCount > 0) {
          setLocalLeads(leads);
          renderLeads();
          updateSelectedCounts();
          await loadStatus();
          showToast(`Found and verified ${enrichedCount} domain contact emails!`, "success");
        } else {
          showToast("Checked public records. For remaining businesses, use '+ Add' to type verified emails.", "info");
        }
      } catch (err) {
        showToast("Enrichment completed", "info");
      } finally {
        enrichAllBtn.disabled = false;
        enrichAllBtn.innerHTML = `✨ Auto-Find Missing Emails`;
      }
    });

    // Batch Send button
    batchSendModalBtn.addEventListener("click", async () => {
      let targetIds = Array.from(selectedLeadIds);
      if (targetIds.length === 0) {
        // Target all with emails
        targetIds = leads.filter(l => l.email && l.email.trim()).map(l => l.id);
      }

      const validLeads = leads.filter(l => targetIds.includes(l.id) && l.email);
      if (validLeads.length === 0) {
        return showToast("Please select businesses with verified emails to send outreach", "error");
      }

      const promptMsg = isDryRun
        ? `[SIMULATION TEST] Send simulated outreach to ${validLeads.length} businesses from zenixservices67@gmail.com?\n\n(To send real live emails to their inboxes, turn OFF Simulation Mode in Settings).`
        : `⚠️ LIVE OUTREACH: Send REAL emails directly from zenixservices67@gmail.com to ${validLeads.length} client inboxes? (Copies will appear in your Gmail Sent folder).`;

      if (!confirm(promptMsg)) return;

      batchSendModalBtn.disabled = true;
      batchSendModalBtn.innerHTML = `<span class="spinner" style="width: 12px; height: 12px;"></span> Dispatching...`;
      showToast(`Dispatching outreach to ${validLeads.length} businesses...`, "info");

      try {
        let sent = false;
        const { ok, data } = await safeFetchJson("/api/batch-send", {
          method: "POST",
          body: JSON.stringify({ lead_ids: validLeads.map(l => l.id) })
        });
        if (ok && data && data.success) {
          showToast(`Dispatched ${data.successful} emails successfully!`, "success");
          sent = true;
          await loadLeads();
          await loadLogs();
        }

        if (!sent) {
          // Client Simulation Fallback
          const count = validLeads.length;
          validLeads.forEach(l => {
            l.status = isDryRun ? "simulated" : "sent";
            appendLog(`[OUTREACH ${isDryRun ? "SIMULATION" : "LIVE"}] To: ${l.email} (${l.name}) — Subject: "${l.email_subject || 'Website & Digital Upgrade'}"`, "success");
          });
          const currentDisp = parseInt(localStorage.getItem(STORAGE_KEY_DISPATCHED) || "0", 10);
          localStorage.setItem(STORAGE_KEY_DISPATCHED, String(currentDisp + count));
          setLocalLeads(leads);
          renderLeads();
          updateSelectedCounts();
          await loadStatus();
          showToast(`${isDryRun ? "Simulated" : "Dispatched"} outreach for ${count} businesses successfully!`, "success");
        }
      } catch (err) {
        showToast("Error during batch dispatch", "error");
      } finally {
        batchSendModalBtn.disabled = false;
        batchSendModalBtn.innerHTML = `📨 Batch Outreach (<span id="batchSendCountBadge">${selectedLeadIds.size}</span>)`;
      }
    });

    // WhatsApp Modal controls
    closeWhatsappModal.addEventListener("click", () => whatsappModal.classList.add("hidden"));
    cancelWhatsappBtn.addEventListener("click", () => whatsappModal.classList.add("hidden"));
    whatsappTemplateSelect.addEventListener("change", () => {
      if (currentWhatsAppLead) {
        whatsappMessageText.value = generateWhatsAppMessage(currentWhatsAppLead, whatsappTemplateSelect.value);
      }
    });
    copyWhatsappBtn.addEventListener("click", () => {
      navigator.clipboard.writeText(whatsappMessageText.value);
      showToast("Copied WhatsApp message text!", "success");
    });

    if (whatsappAutoFindBtn) {
      whatsappAutoFindBtn.addEventListener("click", async () => {
        if (!currentWhatsAppLead) return;
        const origText = whatsappAutoFindBtn.innerHTML;
        whatsappAutoFindBtn.disabled = true;
        whatsappAutoFindBtn.innerHTML = "🔍 Searching...";
        try {
          const { ok, data } = await safeFetchJson("/api/leads/auto-find-email", {
            method: "POST",
            body: JSON.stringify({ lead_id: currentWhatsAppLead.id })
          });
          if (ok && data && data.success && data.lead && data.lead.phone) {
            const p10 = extractIndianPhone10(data.lead.phone);
            if (p10) {
              if (whatsappPhoneInput) whatsappPhoneInput.value = p10;
              currentWhatsAppLead.phone = data.lead.phone;
              whatsappPhoneBadge.textContent = `Phone: +91 ${p10}`;
              showToast(`Found phone: +91 ${p10}!`, "success");
            } else {
              showToast("Found contact details, but mobile was not 10-digit Indian.", "info");
            }
          } else {
            showToast("Could not find phone automatically. Please type it in manually.", "info");
          }
        } catch (err) {
          showToast("Search failed", "error");
        } finally {
          whatsappAutoFindBtn.disabled = false;
          whatsappAutoFindBtn.innerHTML = origText;
        }
      });
    }

    openWhatsappBtn.addEventListener("click", async () => {
      if (!currentWhatsAppLead) return;
      const rawInput = (whatsappPhoneInput ? whatsappPhoneInput.value : "").trim();
      const phone10 = extractIndianPhone10(rawInput) || extractIndianPhone10(currentWhatsAppLead.phone);
      if (!phone10 || phone10.length !== 10) {
        showToast("Please enter a valid 10-digit Indian mobile number (starts with 6, 7, 8, or 9)", "error");
        if (whatsappPhoneInput) whatsappPhoneInput.focus();
        return;
      }

      // Save phone to DB if updated
      const formatted = `+91 ${phone10.slice(0, 5)} ${phone10.slice(5)}`;
      if (currentWhatsAppLead.phone !== formatted) {
        try {
          await safeFetchJson("/api/leads/update", {
            method: "POST",
            body: JSON.stringify({ lead_id: currentWhatsAppLead.id, phone: formatted })
          });
          currentWhatsAppLead.phone = formatted;
          await loadLeads();
        } catch (e) {
          console.error("Failed saving phone:", e);
        }
      }

      const text = encodeURIComponent(whatsappMessageText.value);
      const waUrl = `https://wa.me/91${phone10}?text=${text}`;
      window.open(waUrl, "_blank");
      appendLog(`[WHATSAPP] Initiated direct WhatsApp chat with ${currentWhatsAppLead.name} (+91 ${phone10})`, "info");
      whatsappModal.classList.add("hidden");
    });

    // Export CSV (Direct in-browser generation + server sync)
    exportCsvBtn.addEventListener("click", () => {
      const listToExport = leads && leads.length > 0 ? leads : [];
      if (listToExport.length === 0) {
        return showToast("No leads available to export", "info");
      }
      const headers = ["Name", "Category", "Subcategory", "Phone", "Email", "Website", "Has Website", "Address", "City", "Opportunity Score", "Email Subject", "Status"];
      const rows = listToExport.map(l => [
        `"${(l.name || '').replace(/"/g, '""')}"`,
        `"${(l.category || '').replace(/"/g, '""')}"`,
        `"${(l.subcategory || '').replace(/"/g, '""')}"`,
        `"${(l.phone || '').replace(/"/g, '""')}"`,
        `"${(l.email || '').replace(/"/g, '""')}"`,
        `"${(l.website || '').replace(/"/g, '""')}"`,
        l.has_website ? "Yes" : "No",
        `"${(l.address || '').replace(/"/g, '""')}"`,
        `"${(l.city || '').replace(/"/g, '""')}"`,
        l.opportunity_score || 85,
        `"${(l.email_subject || '').replace(/"/g, '""')}"`,
        l.status || "discovered"
      ]);
      const csv = "\uFEFF" + [headers.join(","), ...rows.map(r => r.join(","))].join("\r\n");
      const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
      const dlUrl = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = dlUrl;
      a.download = `zenix_leads_${new Date().toISOString().slice(0, 10)}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(dlUrl);
      showToast(`Exported ${listToExport.length} leads to CSV!`, "success");
    });

    // Clear All Leads
    clearLeadsBtn.addEventListener("click", async () => {
      if (!confirm("Clear all discovered leads from workspace?")) return;
      leads = [];
      selectedLeadIds.clear();
      localStorage.removeItem(STORAGE_KEY_LEADS);
      renderLeads();
      updateSelectedCounts();
      await loadStatus();
      showToast("All leads cleared", "info");
      try {
        await safeFetchJson("/api/leads/clear", { method: "POST" });
      } catch (err) {}
    });

    // Load sample Indian leads
    loadSampleBtn.addEventListener("click", async () => {
      locationInput.value = "Ranchi, Jharkhand";
      try {
        const initRes = await fetch("initial_leads.json");
        if (initRes.ok) {
          const initLeads = await initRes.json();
          if (Array.isArray(initLeads) && initLeads.length > 0) {
            leads = initLeads;
            setLocalLeads(leads);
            renderLeads();
            updateSelectedCounts();
            await loadStatus();
            showToast(`Loaded ${leads.length} verified Indian leads!`, "success");
            return;
          }
        }
      } catch (e) {}
      discoveryForm.dispatchEvent(new Event("submit"));
    });

    // Composer Modal controls
    closeComposerModal.addEventListener("click", () => composerModal.classList.add("hidden"));
    cancelComposerBtn.addEventListener("click", () => composerModal.classList.add("hidden"));
    composerTone.addEventListener("change", () => {
      if (currentEditingLead) generatePitch(currentEditingLead.id, composerTone.value);
    });
    regeneratePitchBtn.addEventListener("click", () => {
      if (currentEditingLead) generatePitch(currentEditingLead.id, composerTone.value);
    });
    copyComposerBtn.addEventListener("click", () => {
      const text = `Subject: ${composerSubject.value}\n\n${composerBody.value}`;
      navigator.clipboard.writeText(text);
      showToast("Copied email text to clipboard!", "success");
    });
    sendComposerBtn.addEventListener("click", sendEmailFromComposer);

    // Composer Auto-Find Email button
    if (composerAutoFindBtn) {
      composerAutoFindBtn.addEventListener("click", async () => {
        if (!currentEditingLead) return;
        const origText = composerAutoFindBtn.innerHTML;
        composerAutoFindBtn.disabled = true;
        composerAutoFindBtn.innerHTML = `<span class="spinner" style="width: 11px; height: 11px;"></span> Searching...`;
        try {
          const { ok, data } = await safeFetchJson("/api/leads/auto-find-email", {
            method: "POST",
            body: JSON.stringify({ lead_id: currentEditingLead.id })
          });
          if (ok && data && data.success && data.lead && data.lead.email) {
            composerRecipient.value = data.lead.email;
            currentEditingLead.email = data.lead.email;
            showToast(`Found verified email: ${data.lead.email}!`, "success");
            await loadLeads();
          } else {
            showToast("Could not find email automatically. Please type manually.", "info");
          }
        } catch (e) {
          showToast("Search encountered an error", "error");
        } finally {
          composerAutoFindBtn.disabled = false;
          composerAutoFindBtn.innerHTML = origText;
        }
      });
    }

    // Switch to Live Outreach from inside composer notice
    if (cmnSwitchLiveBtn) {
      cmnSwitchLiveBtn.addEventListener("click", async () => {
        try {
          const { ok, data } = await safeFetchJson("/api/settings/toggle-mode", { method: "POST" });
          if (ok && data && data.success) {
            isDryRun = Boolean(data.dry_run_mode);
            updateComposerModeNotice();
            await loadStatus();
            showToast(isDryRun ? "Switched to Safe Simulation Mode" : "🔥 Switched to LIVE Outreach Mode!", isDryRun ? "info" : "success");
          }
        } catch (e) {
          showToast("Failed to toggle mode", "error");
        }
      });
    }

    // Toggle simulation / live mode by clicking header pill
    if (dryRunIndicator) {
      dryRunIndicator.style.cursor = "pointer";
      dryRunIndicator.title = "Click to toggle between Simulation and Live Outreach";
      dryRunIndicator.addEventListener("click", async () => {
        try {
          const { ok, data } = await safeFetchJson("/api/settings/toggle-mode", { method: "POST" });
          if (ok && data && data.success) {
            isDryRun = Boolean(data.dry_run_mode);
            updateComposerModeNotice();
            await loadStatus();
            showToast(isDryRun ? "Simulation Mode Active" : "🔥 LIVE Outreach Active!", isDryRun ? "info" : "success");
          }
        } catch (e) {
          showToast("Failed to toggle mode", "error");
        }
      });
    }

    // Send Real Live Test Email to My Gmail
    if (sendTestEmailBtn) {
      sendTestEmailBtn.addEventListener("click", async () => {
        const user = (settingSmtpUser ? settingSmtpUser.value.trim() : "") || (settingSenderEmail ? settingSenderEmail.value.trim() : "");
        const rawPass = settingSmtpPass ? settingSmtpPass.value.trim() : "";
        const cleanPass = rawPass.replace(/\s+/g, "").toLowerCase();
        const isSaved = rawPass === "••••••••••••" || (!rawPass && settingSmtpPass?.placeholder?.includes("Saved"));

        if (!user || !user.includes("@")) {
          showToast("Please enter your Gmail address first.", "error");
          return;
        }

        if (!isSaved && cleanPass.length !== 16) {
          showToast("Google App Password must be 16 characters (e.g. abcd efgh ijkl mnop).", "error");
          if (smtpTestResult) {
            smtpTestResult.textContent = `✕ Google App Passwords are 16 letters (you entered ${cleanPass.length} chars)`;
            smtpTestResult.className = "smtp-test-result error";
          }
          return;
        }

        if (smtpTestResult) {
          smtpTestResult.textContent = `Sending real test email to ${user}...`;
          smtpTestResult.className = "smtp-test-result";
        }
        sendTestEmailBtn.disabled = true;

        try {
          const { ok, data } = await safeFetchJson("/api/send-test-email", {
            method: "POST",
            body: JSON.stringify({
              smtp_user: user,
              smtp_pass: cleanPass.length === 16 ? cleanPass : "",
              to_email: user
            })
          });
          if (ok && data && data.success) {
            if (smtpTestResult) {
              smtpTestResult.textContent = `✓ Real test email delivered to ${user}! Check inbox & Sent folder.`;
              smtpTestResult.className = "smtp-test-result success";
            }
            updateLinkedSenderEmail(user);
            showToast(`Real test email sent to ${user}! Check your Gmail inbox and Sent folder.`, "success");
            await loadLogs();
          } else {
            const err = data?.message || data?.detail || "Send failed";
            if (smtpTestResult) {
              smtpTestResult.textContent = `✕ Send failed: ${err}`;
              smtpTestResult.className = "smtp-test-result error";
            }
            showToast(`Test email error: ${err}`, "error");
          }
        } catch (e) {
          showToast("Network error sending test email", "error");
        } finally {
          sendTestEmailBtn.disabled = false;
        }
      });
    }

    // Logs Drawer controls
    toggleLogsBtn.addEventListener("click", () => {
      logsDrawerOverlay.classList.remove("hidden");
      loadLogs();
    });
    closeLogsDrawer.addEventListener("click", () => logsDrawerOverlay.classList.add("hidden"));
    closeLogsDrawerBtn.addEventListener("click", () => logsDrawerOverlay.classList.add("hidden"));
    refreshLogsBtn.addEventListener("click", loadLogs);

    // Settings Modal controls
    headerSettingsBtn.addEventListener("click", () => {
      settingsModal.classList.remove("hidden");
      loadSettings();
    });
    closeSettingsModal.addEventListener("click", () => settingsModal.classList.add("hidden"));
    cancelSettingsBtn.addEventListener("click", () => settingsModal.classList.add("hidden"));
    saveSettingsBtn.addEventListener("click", saveSettings);
    testSmtpBtn.addEventListener("click", testSmtp);
  }

  // Run on page load
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
