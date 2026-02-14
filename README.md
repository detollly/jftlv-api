🌅 Tikai Šodien
A beautifully simple daily‑reading experience powered by Cloudflare Workers
A clean, distraction‑free daily reading experience delivered through a tiny serverless backend and a lightweight HTML frontend.
Designed for speed, clarity, and a calm reading flow.

🎯 Purpose
Create a frictionless, instantly‑loading daily reading page that:
- Works anywhere
- Loads fast on any device
- Requires zero maintenance
No frameworks. No build steps. No servers.
Just content, clean UI, and a Worker.

✨ UX & UI Principles
- Zero cognitive load — today’s reading appears instantly
- Typography‑first — calm, readable, balanced
- Minimal chrome — no menus, no clutter
- Responsive — mobile → desktop → ultra‑wide
- Predictable structure — consistent layout
- Fast as thought — Cloudflare edge delivery

🧩 Architecture Overview
Frontend (index.html)
      ↓ fetches
API (/api/today) — hosted at:
https://jftlv-api.detollly.workers.dev/api/today
      ↓ reads
jftlv.json (MM-DD keyed entries)


Everything is static except the Worker logic that selects the correct entry for the current date.
The full API implementation is open‑source:
👉 https://github.com/detollly/jftlv-api

📁 Project Structure
JFTLV-WORKER/
├── index.html          # Minimalist UI
├── index.js            # Cloudflare Worker logic
├── jftlv.json          # Daily entries (MM-DD)
├── jftlvraw.txt        # Raw source text
├── jftlv-JSON.py       # JSON generator script
├── jftlv.pdf           # Source document (optional)
├── package.json        # Node metadata
├── wrangler.toml       # Worker configuration
└── .wrangler/          # Wrangler state



🧠 How the Worker Works
1. Generate today’s key
function getTodayKey() {
  const now = new Date();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${month}-${day}`;
}


2. Serve the frontend
/ → returns index.html
3. Serve today’s entry
/api/today → returns JSON for today’s MM-DD key
If missing → returns a graceful JSON 404
Live example:
https://jftlv-api.detollly.workers.dev/api/today

🎨 UI & Styling
The UI uses Milligram for a clean baseline and custom CSS for readability and balance.
Base layout
#content {
  margin: 3rem;
  max-width: 80vw;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}


Ultra‑wide screens
@media (min-width: 1920px) {
  #content {
    max-width: 40vw;
    margin-left: auto;
    margin-right: auto;
    align-items: center;
    justify-content: center;
  }
}


This creates a centered, book‑like reading column on large monitors.

🖥️ Frontend Rendering Logic
fetch("/api/today")
  .then(res => res.json())
  .then(data => {
    const fields = ["dateLV", "title", "quote", "reference", "body", "affirmation"];
    const html = fields
      .filter(key => data[key])
      .map(key => `<div class="${key}">${data[key]}</div>`)
      .join("");

    document.getElementById("content").innerHTML = html;
  })
  .catch(() => {
    document.getElementById("content").textContent = "Failed to load entry.";
  });



🧪 Local Development
npm install -g wrangler
wrangler dev


Open:
http://localhost:8787

🚀 Deployment
wrangler publish



📄 License
MIT — open, flexible, and yours to build on.
