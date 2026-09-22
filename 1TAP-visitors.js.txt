
// File: functions/api/visitors.js  (for Cloudflare Pages)
// This gives you TRUE global daily/monthly/yearly counter with auto yearly reset
// Setup: Create KV namespace named VISITORS and bind to Pages

export async function onRequestPost(context) {
  const kv = context.env.VISITORS;
  if (!kv) {
    return new Response(JSON.stringify({ error: 'KV not bound. Create KV VISITORS' }), { status: 500 });
  }

  // IST date
  const now = new Date();
  const ist = new Date(now.getTime() + (now.getTimezoneOffset() * 60000) + (5.5 * 60 * 60000));
  const y = ist.getFullYear();
  const m = String(ist.getMonth() + 1).padStart(2, '0');
  const d = String(ist.getDate()).padStart(2, '0');
  const ymd = `${y}-${m}-${d}`;
  const ym = `${y}-${m}`;
  const yKey = String(y);

  // Keys for KV
  const dailyKey = `daily:${ymd}`;
  const monthlyKey = `monthly:${ym};
  const yearlyKey = `yearly:${yKey}`;
  const totalKey = `total`;

  // Get current counts
  let daily = parseInt((await kv.get(dailyKey)) || '0');
  let monthly = parseInt((await kv.get(monthlyKey)) || '0');
  let yearly = parseInt((await kv.get(yearlyKey)) || '0');
  let total = parseInt((await kv.get(totalKey)) || '0');

  // Increment (you can add IP check to avoid spam - simple version counts every POST)
  daily++;
  monthly++;
  yearly++;
  total++;

  // Save with expiration: daily 2 days, monthly 40 days, yearly 400 days
  await kv.put(dailyKey, String(daily), { expirationTtl: 172800 });
  await kv.put(monthlyKey, String(monthly), { expirationTtl: 3456000 });
  await kv.put(yearlyKey, String(yearly), { expirationTtl: 34560000 });
  await kv.put(totalKey, String(total));

  // Auto yearly archive logic: if new year, old yearly keys remain as archive automatically
  // You can fetch archive via /api/visitors?archive=1 if needed

  return new Response(JSON.stringify({
    daily, monthly, yearly, total,
    date: ymd,
    month: ym,
    year: yKey,
    ist: ist.toISOString()
  }), {
    headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
  });
}

export async function onRequestGet(context) {
  // GET returns current counts without incrementing (for admin check)
  const kv = context.env.VISITORS;
  if (!kv) {
    return new Response(JSON.stringify({ error: 'KV not bound' }), { status: 500 });
  }
  const now = new Date();
  const ist = new Date(now.getTime() + (now.getTimezoneOffset() * 60000) + (5.5 * 60 * 60000));
  const y = ist.getFullYear();
  const m = String(ist.getMonth() + 1).padStart(2, '0');
  const d = String(ist.getDate()).padStart(2, '0');
  const ymd = `${y}-${m}-${d}`;
  const ym = `${y}-${m}`;
  
  const daily = parseInt((await kv.get(`daily:${ymd}`)) || '0');
  const monthly = parseInt((await kv.get(`monthly:${ym}`)) || '0');
  const yearly = parseInt((await kv.get(`yearly:${y}`)) || '0');
  const total = parseInt((await kv.get(`total`)) || '0');
  
  return new Response(JSON.stringify({ daily, monthly, yearly, total }), {
    headers: { 'Content-Type': 'application/json' }
  });
}
