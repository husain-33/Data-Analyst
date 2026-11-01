// Vercel serverless function: fetch the published Product Sheet CSV server-side.
// This avoids browser CORS errors from fetching docs.google.com directly.
module.exports = async function handler(req, res) {
  const sheetUrl = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRL_cCuyWVc6LX2conLa7XXkJhNAkhMHPON2cp97MQ5nvnjFVE2a_favxxZyZ6ST7YVxl1kPOjdh5H8/pub?output=csv&gid=1821278063";
  try {
    const upstream = await fetch(sheetUrl, { headers: { "Cache-Control": "no-cache" } });
    if (!upstream.ok) {
      return res.status(502).json({ error: `Google Sheets returned HTTP ${upstream.status}` });
    }
    const csv = await upstream.text();
    if (!csv || csv.trim().startsWith("<")) {
      return res.status(502).json({ error: "Google Sheets did not return CSV. Confirm that the Product Sheet tab is published as CSV." });
    }
    res.setHeader("Content-Type", "text/csv; charset=utf-8");
    res.setHeader("Cache-Control", "no-store, max-age=0");
    res.setHeader("Access-Control-Allow-Origin", "*");
    return res.status(200).send(csv);
  } catch (err) {
    return res.status(502).json({ error: "Could not reach Google Sheets: " + err.message });
  }
};
