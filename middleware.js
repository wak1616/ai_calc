export default function middleware(request) {
  const url = new URL(request.url);
  const host = request.headers.get("host") || "";

  if (host.includes("derojas.info")) {
    const newUrl = `https://aicalc.derojas.ai${url.pathname}${url.search}`;
    const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Site Has Moved — AI Calc</title>
  <meta http-equiv="refresh" content="10;url=${newUrl}">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #f5f7fa;
      color: #333;
      padding: 1.5rem;
    }
    .card {
      background: white;
      border-radius: 12px;
      box-shadow: 0 4px 24px rgba(0,0,0,0.1);
      padding: 2.5rem;
      max-width: 520px;
      width: 100%;
      text-align: center;
    }
    h1 {
      font-size: 1.5rem;
      margin-bottom: 1rem;
      color: #1a1a2e;
    }
    p {
      font-size: 1rem;
      line-height: 1.6;
      margin-bottom: 1rem;
      color: #555;
    }
    a {
      color: #1976d2;
      text-decoration: none;
      font-weight: 600;
    }
    a:hover { text-decoration: underline; }
    .notice {
      background: #fff3e0;
      border-left: 4px solid #ff9800;
      padding: 0.75rem 1rem;
      border-radius: 4px;
      font-size: 0.9rem;
      margin: 1.25rem 0;
      text-align: left;
      color: #6d4c00;
    }
    .redirect-note {
      font-size: 0.85rem;
      color: #999;
      margin-top: 0.5rem;
    }
  </style>
</head>
<body>
  <div class="card">
    <h1>This Site Has Moved</h1>
    <p>
      AI Calc is now available at its new home:<br>
      <a href="${newUrl}">aicalc.derojas.ai</a>
    </p>
    <div class="notice">
      Please update your bookmarks. The <strong>derojas.info</strong> domain
      will expire on <strong>March 12, 2026</strong> and will no longer be
      accessible after that date.
    </div>
    <p>
      <a href="${newUrl}">Go to aicalc.derojas.ai &rarr;</a>
    </p>
    <p class="redirect-note">You will be redirected automatically in 10 seconds.</p>
  </div>
</body>
</html>`;

    return new Response(html, {
      status: 200,
      headers: { "Content-Type": "text/html; charset=utf-8" },
    });
  }
}

export const config = {
  matcher: "/(.*)",
};
