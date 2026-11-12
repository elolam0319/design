const { chromium } = require('playwright');
(async () => {
  const [file, out, ...times] = process.argv.slice(2);
  const browser = await chromium.launch({ proxy: process.env.HTTPS_PROXY ? { server: process.env.HTTPS_PROXY } : undefined });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  page.on('console', m => console.log('console:', m.text()));
  page.on('pageerror', e => console.log('pageerror:', e.message));
  await page.goto('file://' + file + '?render=1');
  await page.waitForFunction(() => window.__ready, null, { timeout: 30000 });
  console.log('fonts:', await page.evaluate(() => ["Anton","Pretendard Variable","Hada Condensed"].map(f => f + '=' + document.fonts.check('40px "' + f + '"', '가A')).join(' ')));
  for (const t of times) {
    await page.evaluate(x => window.seek(+x), t);
    await page.screenshot({ path: `${out}/t${String(t).padStart(5,'0')}.png`, clip: { x: 0, y: 0, width: 1080, height: 1920 } });
  }
  await browser.close();
})();
