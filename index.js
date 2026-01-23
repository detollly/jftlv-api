import jftlv from "./jftlv.json"
import html from "./index.html"

function getTodayKey() {
  const now = new Date().toLocaleString("en-US", { timeZone: "Europe/Riga" });
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${month}-${day}`;
}

export default {
  async fetch(request) {
    const url = new URL(request.url);

    // Serve the HTML frontend
    if (url.pathname === "/") {
      return new Response(html, {
        status: 200,
        headers: { "Content-Type": "text/html" }
      });
    }

    // Serve today's entry as JSON
    if (url.pathname === "/api/today") {
      const key = getTodayKey();
      const entry = jftlv.find(e => e.date === key);

      if (!entry) {
        return new Response(
          JSON.stringify({ error: "No entry found for today" }),
          {
            status: 404,
            headers: { "Content-Type": "application/json" }
          }
        );
      }

      return new Response(JSON.stringify(entry), {
        status: 200,
        headers: {
          "Content-Type": "application/json",
          "Cache-Control": "public, max-age=300"
        }
      });
    }

    // Fallback for unknown paths
    return new Response("Not found", {
      status: 404,
      headers: { "Content-Type": "text/plain" }
    });

  }
};