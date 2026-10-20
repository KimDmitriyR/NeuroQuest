// Fails if any page scrolls horizontally on phone/tablet widths.
// Run:  node overflow.mjs
import { WEB, api, launchBrowser, newContext, seedParentAndChild, issuePlayerToken, sleep, PARENT_TOKEN_KEY, PLAYER_TOKEN_KEY } from "./common.mjs";

const { token, child, playerToken } = await seedParentAndChild("ОченьДлинноеИмяРебёнкаДляПроверки");
const session = await api("/api/quests/start", {
  method: "POST",
  token,
  body: { player_id: child.id, qr_token: "finstartup-2-0-01" },
});
const missions = await api("/api/missions");

// the grand finale needs a child who collected all 12 letters
const ALL_CARDS = [
  "finstartup-2-0-01", "finstartup-2-0-02", "finstartup-2-0-03", "finstartup-2-0-04",
  "kibershchit-01", "kibershchit-02", "kibershchit-03", "kibershchit-04",
  "ai-logika-01", "ai-logika-02", "ai-logika-03", "ai-logika-04",
];
const finalist = await api("/api/players", { method: "POST", token, body: { name: "Финалист" } });
const finalistToken = await issuePlayerToken(token, finalist.id);
for (const qr of ALL_CARDS) {
  const s = await api("/api/quests/start", { method: "POST", token, body: { player_id: finalist.id, qr_token: qr } });
  for (let i = 0; i < 10; i++) {
    const cur = await api(`/api/quests/sessions/${s.id}`, { token });
    const res = await api(`/api/quests/sessions/${s.id}/choices`, { method: "POST", token, body: { choice_id: cur.current_node.choices[0].id } });
    if (res.completed) break;
  }
}

const routes = [
  "/", "/missions", `/mission/${missions[0].id}`, `/mission/${missions[1].id}`,
  `/quest/${session.id}`, "/profile", "/settings", "/parent", "/review", "/terms", "/privacy",
];

const browser = await launchBrowser();
let bad = 0;
for (const width of [360, 390, 768]) {
  for (const signedIn of [true, false]) {
    for (const route of routes) {
      const ctx = await newContext(browser);
      const page = await ctx.newPage();
      await page.setViewport({ width, height: 800, isMobile: width < 700, hasTouch: width < 700 });
      if (signedIn) {
        await page.evaluateOnNewDocument(
          (k1, t, k2, pt) => { localStorage.setItem(k1, t); localStorage.setItem(k2, pt); },
          PARENT_TOKEN_KEY, token, PLAYER_TOKEN_KEY, playerToken,
        );
      }
      await page.goto(WEB + route, { waitUntil: "networkidle0" });
      await sleep(250);
      const m = await page.evaluate(() => {
        const vw = document.documentElement.clientWidth;
        const offenders = [...document.querySelectorAll("body *")]
          .filter((e) => {
            const r = e.getBoundingClientRect();
            return r.width > 0 && r.right > vw + 1 && getComputedStyle(e).position !== "fixed" && !e.closest(".chips");
          })
          .slice(0, 3)
          .map((e) => e.className || e.tagName);
        return { vw, sw: document.documentElement.scrollWidth, offenders };
      });
      if (m.sw > m.vw + 1) {
        bad++;
        console.log(`OVERFLOW ${width}px ${signedIn ? "signed-in" : "guest"} ${route.slice(0, 24)}: ${m.sw} > ${m.vw}; e.g. ${m.offenders.join(", ")}`);
      }
      await ctx.close();
    }
  }
}
for (const width of [360, 390, 768]) {
  const ctx = await newContext(browser);
  const page = await ctx.newPage();
  await page.setViewport({ width, height: 800, isMobile: width < 700, hasTouch: width < 700 });
  await page.evaluateOnNewDocument(
    (k1, t, k2, pt) => { localStorage.setItem(k1, t); localStorage.setItem(k2, pt); },
    PARENT_TOKEN_KEY, token, PLAYER_TOKEN_KEY, finalistToken,
  );
  await page.goto(WEB + "/finale", { waitUntil: "networkidle0" });
  await sleep(6800); // letters fly in -> hack effect -> stamp -> certificate
  const m = await page.evaluate(() => ({
    vw: document.documentElement.clientWidth,
    sw: document.documentElement.scrollWidth,
    cert: !!document.querySelector(".finale-page__certificate"),
    certRight: document.querySelector(".finale-page__certificate")?.getBoundingClientRect().right ?? 0,
  }));
  if (!m.cert || m.sw > m.vw + 1 || m.certRight > m.vw + 1) {
    bad++;
    console.log(`FINALE ${width}px: certificate shown=${m.cert}, scrollWidth ${m.sw}, viewport ${m.vw}, certificate right edge ${Math.round(m.certRight)}`);
  }
  await ctx.close();
}

console.log(bad ? `\n${bad} overflow problem(s)` : `\nno horizontal overflow on ${routes.length} routes x 3 widths x 2 states`);
await browser.close();
process.exit(bad ? 1 : 0);
