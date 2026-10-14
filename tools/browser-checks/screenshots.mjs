// Screenshots of every screen on desktop (1440px) and phone (390px), with realistic data.
// Run:  node screenshots.mjs [name ...]     -> PNGs in ./out  (git-ignored)
import { mkdirSync } from "node:fs";
import {
  WEB, api, launchBrowser, newContext, seedParentAndChild, sleep, PARENT_TOKEN_KEY, PLAYER_KEY,
} from "./common.mjs";

const OUT = new URL("./out/", import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1");
mkdirSync(OUT, { recursive: true });

// ---- seed: a child who finished 2 cards, has a card in progress and a photo waiting for review
const { token, child } = await seedParentAndChild("Маша");
await api("/api/players", { method: "POST", token, body: { name: "Артём" } });

async function playCard(qr, labels) {
  const s = await api("/api/quests/start", { method: "POST", body: { player_id: child.id, qr_token: qr } });
  for (const label of labels) {
    const cur = await api(`/api/quests/sessions/${s.id}`);
    const c = cur.current_node.choices.find((x) => x.label === label);
    await api(`/api/quests/sessions/${s.id}/choices`, { method: "POST", body: { choice_id: c.id } });
  }
  return s;
}
await playCard("finstartup-2-0-01", ["C", "C", "C"]);
await playCard("kibershchit-02", ["B", "A", "B"]);
const openQuest = await api("/api/quests/start", { method: "POST", body: { player_id: child.id, qr_token: "ai-logika-01" } });

const missions = await api("/api/missions");
const photoMission = missions.find((m) => m.validation_type === "photo");
const attempt = await api(`/api/missions/${photoMission.id}/attempts`, { method: "POST", body: { player_id: child.id } });
const svg = `<svg xmlns='http://www.w3.org/2000/svg' width='800' height='600'><rect width='800' height='600' fill='#fda085'/><circle cx='400' cy='300' r='120' fill='white' opacity='.7'/><text x='400' y='318' font-size='46' text-anchor='middle' fill='#7a1fc4' font-family='sans-serif'>Копилка 4/3/2/1</text></svg>`;
await api(`/api/missions/attempts/${attempt.id}/submit`, {
  method: "POST",
  body: { photo_url: "data:image/svg+xml;utf8," + encodeURIComponent(svg) },
});

const browser = await launchBrowser();
const DESKTOP = { width: 1440, height: 900, deviceScaleFactor: 1 };
const MOBILE = { width: 390, height: 844, deviceScaleFactor: 2, isMobile: true, hasTouch: true };
const openMenu = async (p) => { await p.click(".profile-menu__button"); await sleep(300); };
const answerFirst = async (p) => { await p.click(".choice-button"); await sleep(900); };

async function shot(name, path, viewport, { signedIn = true, fullPage = true, act } = {}) {
  const ctx = await newContext(browser);
  const page = await ctx.newPage();
  await page.setViewport(viewport);
  page.on("pageerror", (e) => console.log(`[pageerror ${name}]`, e.message));
  if (signedIn) {
    await page.evaluateOnNewDocument(
      (k1, t, k2, id) => { localStorage.setItem(k1, t); localStorage.setItem(k2, id); },
      PARENT_TOKEN_KEY, token, PLAYER_KEY, child.id,
    );
  }
  await page.goto(WEB + path, { waitUntil: "networkidle0" });
  await sleep(400);
  if (act) await act(page);
  await page.screenshot({ path: `${OUT}${name}.png`, fullPage });
  await ctx.close();
  console.log("shot", name);
}

const jobs = {
  "home-guest-d": () => shot("home-guest-d", "/", DESKTOP, { signedIn: false }),
  "home-guest-m": () => shot("home-guest-m", "/", MOBILE, { signedIn: false }),
  "home-d": () => shot("home-d", "/", DESKTOP),
  "home-m": () => shot("home-m", "/", MOBILE),
  "missions-d": () => shot("missions-d", "/missions", DESKTOP),
  "missions-m": () => shot("missions-m", "/missions", MOBILE),
  "mission-d": () => shot("mission-d", `/mission/${photoMission.id}`, DESKTOP),
  "mission-m": () => shot("mission-m", `/mission/${photoMission.id}`, MOBILE),
  "menu-d": () => shot("menu-d", "/missions", DESKTOP, { fullPage: false, act: openMenu }),
  "menu-m": () => shot("menu-m", "/missions", MOBILE, { fullPage: false, act: openMenu }),
  "quest-d": () => shot("quest-d", `/quest/${openQuest.id}`, DESKTOP, { fullPage: false, act: answerFirst }),
  "quest-m": () => shot("quest-m", `/quest/${openQuest.id}`, MOBILE, { fullPage: false, act: answerFirst }),
  "profile-d": () => shot("profile-d", "/profile", DESKTOP),
  "profile-m": () => shot("profile-m", "/profile", MOBILE),
  "settings-d": () => shot("settings-d", "/settings", DESKTOP),
  "parent-d": () => shot("parent-d", "/parent", DESKTOP),
  "parent-m": () => shot("parent-m", "/parent", MOBILE),
  "review-d": () => shot("review-d", "/review", DESKTOP),
  "auth-d": () => shot("auth-d", "/parent", DESKTOP, { signedIn: false }),
  "auth-m": () => shot("auth-m", "/parent", MOBILE, { signedIn: false }),
  "legal-m": () => shot("legal-m", "/privacy", MOBILE, { signedIn: false }),
};
const only = process.argv.slice(2);
for (const [name, run] of Object.entries(jobs)) if (!only.length || only.includes(name)) await run();
await browser.close();
console.log(`\nSaved to ${OUT}`);
