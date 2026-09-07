const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, content-type, x-admin-password",
  "Access-Control-Allow-Methods": "POST, GET, DELETE, OPTIONS",
};

const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), {
  status,
  headers: { ...corsHeaders, "Content-Type": "application/json" },
});

const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
const serviceRoleKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const adminPassword = Deno.env.get("ADMIN_PASSWORD")!;

function clientIp(request: Request) {
  return request.headers.get("x-forwarded-for")?.split(",")[0].trim()
    || request.headers.get("cf-connecting-ip") || "unknown";
}

async function database(path: string, init: RequestInit = {}) {
  return fetch(`${supabaseUrl}/rest/v1/${path}`, {
    ...init,
    headers: {
      apikey: serviceRoleKey,
      Authorization: "Bearer " + serviceRoleKey,
      "Content-Type": "application/json",
      ...(init.headers || {}),
    },
  });
}

Deno.serve(async (request) => {
  if (request.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });
  if (!supabaseUrl || !serviceRoleKey || !adminPassword) return json({ error: "Function settings are incomplete" }, 500);

  if (request.method === "POST") {
    const body = await request.json();
    if (typeof body.visitorId !== "string" || !/^[a-zA-Z0-9_-]{16,80}$/.test(body.visitorId)) {
      return json({ error: "Invalid visitor ID" }, 400);
    }
    const now = new Date();
    const response = await database("access_logs?on_conflict=visitor_id", {
      method: "POST",
      headers: { Prefer: "resolution=merge-duplicates,return=minimal" },
      body: JSON.stringify({
        visitor_id: body.visitorId,
        player_name: typeof body.playerName === "string" ? body.playerName.slice(0, 12) : null,
        device_info: body.deviceInfo || {},
        ip_address: clientIp(request),
        current_page: body.page === "game" ? "game" : "title",
        last_seen: now.toISOString(),
        expires_at: new Date(now.getTime() + 90 * 24 * 60 * 60 * 1000).toISOString(),
      }),
    });
    if (!response.ok) {
      console.error("Access log insert failed:", response.status, await response.text());
      return json({ error: "Access log failed" }, 502);
    }
    return json({ ok: true });
  }

  if (request.headers.get("x-admin-password") !== adminPassword) return json({ error: "Unauthorized" }, 401);
  if (request.method === "GET") {
    const response = await database("access_logs?select=visitor_id,player_name,device_info,ip_address,current_page,first_seen,last_seen,expires_at&expires_at=gt.now()&order=last_seen.desc&limit=200");
    if (!response.ok) {
      console.error("Access log query failed:", response.status, await response.text());
      return json({ error: "Access log query failed" }, 502);
    }
    return json(await response.json());
  }
  if (request.method === "DELETE") {
    const response = await database("access_logs?expires_at=lt.now()", { method: "DELETE" });
    if (!response.ok) return json({ error: "Cleanup failed" }, 502);
    return json({ ok: true });
  }
  return json({ error: "Method not allowed" }, 405);
});
