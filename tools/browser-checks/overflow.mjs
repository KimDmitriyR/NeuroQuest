// Fails if any page scrolls horizontally on phone/tablet widths.
// Run:  node overflow.mjs
import { WEB, api, launchBrowser, newContext, seedParentAndChild, sleep, PARENT_TOKEN_KEY, PLAYER_KEY } from "./common.mjs";

const { token, child } = await seedParentAndChild("ОченьДлинноеИмяРебёнкаДляПроверки");
const session = await api("/api/quests/start", {
  method: "POST",
  body: { player_id: child.id, qr_token: "finstartup-2-0-01" },
});
const missions = await api("/api/missions");

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
          (k1, t, k2, id) => { localStorage.setItem(k1, t); localStorage.setItem(k2, id); },
          PARENT_TOKEN_KEY, token, PLAYER_KEY, child.id,
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
console.log(bad ? `\n${bad} overflow problem(s)` : `\nno horizontal overflow on ${routes.length} routes x 3 widths x 2 states`);
await browser.close();
process.exit(bad ? 1 : 0);
