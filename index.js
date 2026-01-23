import jftlv from "./jftlv.json";
import html from "./index.html";

// --- Utilities --------------------------------------------------------------

function getTodayKey() {
  const formatter = new Intl.DateTimeFormat("en-US", {
    timeZone: "Europe/Riga",
    month: "2-digit",
    day: "2-digit"
  });

  const parts = formatter.formatToParts(new Date());
  const month = parts.find(p => p.type === "month").value;
  const day = parts.find(p => p.type === "day").value;

  return `${month}-${day}`;
}

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type"
};

// --- Handlers ---------------------------------------------------------------

function handleOptions() {
  return new Response(null, {
    status: 204,
    headers: CORS_HEADERS
  });
}

function handleRoot() {
  return new Response(html, {
    status: 200,
    headers: {
      "Content-Type": "text/html; charset=utf-8"
    }
  });
}

function handleToday() {
  const key = getTodayKey();
  const entry = jftlv.find(e => e.date === key);

  if (!entry) {
    return new Response(
      JSON.stringify({ error: "No entry found for today" }),
      {
        status: 404,
        headers: {
          "Content-Type": "application/json",
          ...CORS_HEADERS
        }
      }
    );
  }

  return new Response(JSON.stringify(entry), {
    status: 200,
    headers: {
      "Content-Type": "application/json",
      "Cache-Control": "public, max-age=300",
      ...CORS_HEADERS
    }
  });
}

function handleNotFound() {
  return new Response("Not found", {
    status: 404,
    headers: { "Content-Type": "text/plain" }
  });
}

// --- Router -----------------------------------------------------------------

export default {
  async fetch(request) {
    const url = new URL(request.url);

    if (request.method === "OPTIONS") return handleOptions();

    switch (url.pathname) {
      case "/":
        return handleRoot();

      case "/api/today":
        return handleToday();

      default:
        return handleNotFound();
    }
  }
};