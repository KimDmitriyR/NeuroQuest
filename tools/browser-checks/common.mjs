// Shared helpers for the browser checks.
//
// Browser: if CHROME_PATH is set (e.g. on Windows:
//   C:\Program Files\Google\Chrome\Application\chrome.exe ) that browser is used;
// otherwise the Chromium bundled in @sparticuz/chromium (works on Linux CI /
// sandboxes without a browser installed).
import chromium from "@sparticuz/chromium";
import puppeteer from "puppeteer-core";

export const API = process.env.API_URL ?? "http://localhost:8000";
export const WEB = process.env.WEB_URL ?? "http://localhost:5173";
export const PARENT_TOKEN_KEY = "neuroquest.parent_token";
export const PLAYER_TOKEN_KEY = "neuroquest.player_token";

export async function launchBrowser() {
  if (process.env.CHROME_PATH) {
    return puppeteer.launch({ executablePath: process.env.CHROME_PATH, headless: true });
  }
  return puppeteer.launch({
    // --single-process breaks isolated browser contexts, which these checks use
    args: [...chromium.args.filter((a) => a !== "--single-process"), "--no-sandbox"],
    executablePath: await chromium.executablePath(),
    headless: "shell",
  });
}

/** A fresh, isolated context = empty localStorage (a real "guest"). */
export async function newContext(browser) {
  return browser.createBrowserContext
    ? browser.createBrowserContext()
    : browser.createIncognitoBrowserContext();
}

export async function api(path, { method = "GET", token, body } = {}) {
  const res = await fetch(API + path, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error(`${method} ${path} -> ${res.status} ${await res.text()}`);
  return res.json();
}

/** Parent-only: the credential a child's device carries (what the child link contains). */
export async function issuePlayerToken(parentToken, playerId) {
  const res = await api(`/api/players/${playerId}/access-token`, {
    method: "POST",
    token: parentToken,
  });
  return res.access_token;
}

/** Registers a throw-away parent + one child. Needs the backend running with seeded content. */
export async function seedParentAndChild(childName = "Маша") {
  const email = `check-${Date.now()}-${Math.floor(Math.random() * 1e6)}@example.com`;
  const reg = await api("/api/auth/register", {
    method: "POST",
    body: { email, password: "parol12345", accept_terms: true },
  });
  const child = await api("/api/players", {
    method: "POST",
    token: reg.access_token,
    body: { name: childName },
  });
  const playerToken = await issuePlayerToken(reg.access_token, child.id);
  return { email, token: reg.access_token, child, playerToken };
}

export const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
