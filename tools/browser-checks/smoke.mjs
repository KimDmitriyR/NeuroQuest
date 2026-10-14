// End-to-end click-through of the main user journey, in a real browser.
// Run:  node smoke.mjs      (backend on :8000 with seeded content, frontend on :5173)
import { WEB, launchBrowser, newContext, sleep } from "./common.mjs";

const browser = await launchBrowser();
const ctx = await newContext(browser);
const page = await ctx.newPage();
await page.setViewport({ width: 1280, height: 800 });

const problems = [];
page.on("pageerror", (e) => problems.push("pageerror: " + e.message));
page.on("console", (m) => {
  // the deliberately wrong card code below makes the API answer 404 - expected
  if (m.type() === "error" && !m.text().includes("404")) problems.push("console.error: " + m.text());
});

const text = () => page.evaluate(() => document.body.innerText);
let step = 0;
let failed = 0;
async function check(label, cond) {
  step++;
  if (!cond) failed++;
  console.log(`${cond ? "PASS" : "FAIL"}  ${step}. ${label}`);
  if (!cond) console.log("   page text:", (await text()).slice(0, 300).replace(/\n/g, " | "));
}
const waitText = (t, ms = 8000) =>
  page.waitForFunction((x) => document.body.innerText.includes(x), { timeout: ms }, t).catch(() => {});

// 1. guest
await page.goto(WEB + "/", { waitUntil: "networkidle0" });
await check("guest home asks for a parent profile", (await text()).includes("Профиль ребёнка создаёт родитель"));

// 2. register through the real form (consent gate)
await page.goto(WEB + "/parent", { waitUntil: "networkidle0" });
await check("/parent shows a login form for a guest", (await page.$('input[type="email"]')) !== null);
await (await page.$$(".parent-auth__tab"))[1].click();
await page.type('input[type="email"]', `smoke-${Date.now()}@example.com`);
await page.type('input[type="password"]', "parol12345");
const submit = await page.$('.parent-auth__form button[type="submit"]');
await check("register is disabled until consent is ticked", await page.evaluate((b) => b.disabled, submit));
await page.click(".parent-auth__consent input");
await check("register is enabled after consent", !(await page.evaluate((b) => b.disabled, submit)));
await submit.click();
await waitText("Мои дети");
await check("registration lands on the parent dashboard", (await text()).includes("Мои дети"));

// 3. add a child, play on this device
await page.type(".add-child .input", "Тест-Ребёнок");
await page.click('.add-child button[type="submit"]');
await waitText("Тест-Ребёнок");
await check("child appears after adding", (await text()).includes("Тест-Ребёнок"));
await Promise.all([
  page.waitForNavigation({ waitUntil: "networkidle0" }),
  page.click(".child-card__actions .btn:not(.btn--ghost)"),
]);
await check("home greets the child by name", (await text()).includes("Привет, Тест-Ребёнок"));

// 4. start a quest by code, answer
await page.type(".code-form--hero .code-form__input", "finstartup-2-0-01");
await page.click(".code-form--hero .code-form__submit");
await page.waitForFunction(() => location.pathname.startsWith("/quest/"), { timeout: 8000 }).catch(() => {});
await check("a card code opens the quest chat", page.url().includes("/quest/"));
await page.waitForSelector(".choice-button", { timeout: 8000 }).catch(() => {});
await check("first question has 3 answer buttons", (await page.$$(".choice-button")).length === 3);
await (await page.$$(".choice-button"))[2].click();
await waitText("Достижение получено");
await check("answering shows outcome + achievement toast", (await text()).includes("Достижение получено"));

// 5. header code field: friendly error
await page.goto(WEB + "/missions", { waitUntil: "networkidle0" });
await page.type(".app-header .code-form__input", "no-such-card");
await page.click(".app-header .code-form__submit");
await page.waitForSelector(".code-form__error", { timeout: 5000 }).catch(() => {});
await check("unknown code shows 'not found'", (await text()).includes("Карточка с таким кодом не найдена"));

// 6. mission catalog
await (await page.$$(".chips .chip"))[2].click();
await sleep(200);
await check("sector chip filters the catalog to one card", (await page.$$(".product-card")).length === 1);
await page.click(".product-card");
await page.waitForFunction(
  () => location.pathname.startsWith("/mission/") && document.body.innerText.includes("Начать миссию"),
  { timeout: 8000 },
).catch(() => {});
await check("a card opens the mission page", page.url().includes("/mission/") && (await text()).includes("Начать миссию"));

// 7. profile dropdown
await page.click(".profile-menu__button");
await check("profile dropdown opens", (await page.$(".profile-menu__panel")) !== null);
await page.keyboard.press("Escape");
await sleep(150);
await check("Escape closes the dropdown", (await page.$(".profile-menu__panel")) === null);
await page.click(".profile-menu__button");
const items = await page.$$(".profile-menu__item");
const labels = await Promise.all(items.map((i) => i.evaluate((e) => e.textContent.trim())));
await check(
  "dropdown has profile / missions / parent area / settings / sign out",
  ["Мой профиль", "Конверты с миссиями", "Кабинет родителя", "Настройки", "Выйти"].every((l) => labels.includes(l)),
);
await items[labels.indexOf("Выйти")].click();
await sleep(500);
await check("sign out returns to the guest home", (await text()).includes("Профиль ребёнка создаёт родитель"));
const stored = await page.evaluate(() => [
  localStorage.getItem("neuroquest.parent_token"),
  localStorage.getItem("neuroquest.player_id"),
]);
await check("sign out cleared both parent token and active child", stored[0] === null && stored[1] === null);

console.log(problems.length ? "\nBROWSER PROBLEMS:\n" + problems.join("\n") : "\nno console errors / page errors");
await browser.close();
process.exit(failed || problems.length ? 1 : 0);
