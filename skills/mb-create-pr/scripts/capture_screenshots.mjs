#!/usr/bin/env node

import { mkdir, realpath } from "node:fs/promises";
import { createRequire } from "node:module";
import path from "node:path";
import process from "node:process";

const DEFAULT_BASE_URL = "http://localhost:3000";
const DEFAULT_VIEWPORT = "1440x1200";
const DEFAULT_OUT_DIR = path.join("/tmp", "mb-create-pr-screenshots", nowForPath());

const HELP = `
Usage:
  node /path/to/mb-create-pr/scripts/capture_screenshots.mjs [options] "label=/path" ...

Options:
  --base-url <url>    Base URL for relative paths. Default: ${DEFAULT_BASE_URL}
  --out-dir <path>    Output directory outside this repository. Default: ${DEFAULT_OUT_DIR}
  --viewport <WxH>    Viewport size. Default: ${DEFAULT_VIEWPORT}
  --wait-ms <ms>      Extra wait time before each screenshot. Default: 500
  --help             Show this help.
`;

// パス用の時刻表現を共通化し、既定出力先が毎回衝突しないようにする。
function nowForPath() {
  return new Date().toISOString().replace(/[:.]/g, "-");
}

// CLI から受け取る撮影条件を、後続処理で扱いやすい形へ正規化する。
function parseArgs(argv) {
  const options = {
    baseUrl: DEFAULT_BASE_URL,
    outDir: DEFAULT_OUT_DIR,
    viewport: DEFAULT_VIEWPORT,
    waitMs: 500,
    routes: [],
  };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--help" || arg === "-h") {
      options.help = true;
      continue;
    }
    if (arg === "--base-url") {
      options.baseUrl = requireValue(argv, i, arg);
      i += 1;
      continue;
    }
    if (arg === "--out-dir") {
      options.outDir = requireValue(argv, i, arg);
      i += 1;
      continue;
    }
    if (arg === "--viewport") {
      options.viewport = requireValue(argv, i, arg);
      i += 1;
      continue;
    }
    if (arg === "--wait-ms") {
      options.waitMs = Number(requireValue(argv, i, arg));
      i += 1;
      continue;
    }
    options.routes.push(parseRoute(arg));
  }

  return options;
}

// オプション指定漏れを早い段階で検出し、誤った撮影を防ぐ。
function requireValue(argv, index, name) {
  const value = argv[index + 1];
  if (!value || value.startsWith("--")) {
    throw new Error(`${name} には値を指定して下さい。`);
  }
  return value;
}

// PR 本文へ載せる表示名と、実際に開く URL パスを 1 つの引数から取り出す。
function parseRoute(value) {
  const separatorIndex = value.indexOf("=");
  if (separatorIndex === -1) {
    throw new Error(`撮影対象は "表示名=/path" 形式で指定して下さい: ${value}`);
  }

  const label = value.slice(0, separatorIndex).trim();
  const routePath = value.slice(separatorIndex + 1).trim();
  if (!label || !routePath) {
    throw new Error(`表示名とパスはどちらも必須です: ${value}`);
  }

  return { label, path: routePath };
}

// PC/SP など撮影サイズを明示できるよう、WxH 形式だけを受け付ける。
function parseViewport(value) {
  const match = value.match(/^(\d+)x(\d+)$/);
  if (!match) {
    throw new Error(`viewport は 1440x1200 のような形式で指定して下さい: ${value}`);
  }

  return { width: Number(match[1]), height: Number(match[2]) };
}

// 絶対 URL と相対パスのどちらでも同じ撮影フローを使えるようにする。
function buildUrl(baseUrl, routePath) {
  if (/^https?:\/\//.test(routePath)) {
    return routePath;
  }
  return new URL(routePath, baseUrl).toString();
}

// 画面名をファイル名へ使っても壊れにくいように、記号を区切り文字へ寄せる。
function sanitizeFileName(value) {
  return value
    .normalize("NFKC")
    .replace(/[^\p{Letter}\p{Number}._-]+/gu, "-")
    .replace(/^-+|-+$/g, "")
    .toLowerCase();
}

// 共有 Skill をリポジトリ外から実行しても、対象リポジトリ側の Playwright を使えるようにする。
function loadChromium() {
  const requireFromTargetRepo = createRequire(path.join(process.cwd(), "package.json"));
  for (const packageName of ["@playwright/test", "playwright"]) {
    try {
      return requireFromTargetRepo(packageName).chromium;
    } catch (error) {
      if (error.code !== "MODULE_NOT_FOUND") {
        throw error;
      }
    }
  }

  throw new Error("Playwright を読み込めませんでした。対象リポジトリで @playwright/test または playwright を利用できる状態にして下さい。");
}

// スクリーンショットを誤ってコミットしないよう、保存先はリポジトリ外に限定する。
async function assertOutDirOutsideRepo(outDir) {
  const repoRoot = await realpath(process.cwd());
  const absoluteOutDir = path.resolve(outDir);
  const relative = path.relative(repoRoot, absoluteOutDir);

  if (relative === "" || (!relative.startsWith("..") && !path.isAbsolute(relative))) {
    throw new Error(`スクリーンショット保存先はリポジトリ外を指定して下さい: ${absoluteOutDir}`);
  }

  return absoluteOutDir;
}

// 引数検証、ブラウザ起動、撮影結果の出力までを 1 回の実行単位として扱う。
async function main() {
  const options = parseArgs(process.argv.slice(2));
  if (options.help) {
    console.log(HELP.trim());
    return;
  }
  if (options.routes.length === 0) {
    throw new Error("撮影対象を 1 件以上指定して下さい。");
  }
  if (!Number.isFinite(options.waitMs) || options.waitMs < 0) {
    throw new Error("--wait-ms には 0 以上の数値を指定して下さい。");
  }

  const viewport = parseViewport(options.viewport);
  const outDir = await assertOutDirOutsideRepo(options.outDir);
  await mkdir(outDir, { recursive: true });

  const chromium = loadChromium();
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport });
  const results = [];

  try {
    for (const route of options.routes) {
      const url = buildUrl(options.baseUrl, route.path);
      const fileName = `${sanitizeFileName(route.label) || "screenshot"}.png`;
      const filePath = path.join(outDir, fileName);

      await page.goto(url, { waitUntil: "networkidle", timeout: 30_000 });
      await page.waitForTimeout(options.waitMs);
      await page.screenshot({ path: filePath, fullPage: true });
      results.push({ label: route.label, filePath, url });
    }
  } finally {
    await browser.close();
  }

  console.log("スクリーンショットを撮影しました。PR 本文へ反映して下さい。");
  for (const result of results) {
    console.log(`- ${result.label}: ${result.filePath} (${result.url})`);
  }
}

main().catch((error) => {
  console.error(`[ERROR] ${error.message}`);
  process.exit(1);
});
