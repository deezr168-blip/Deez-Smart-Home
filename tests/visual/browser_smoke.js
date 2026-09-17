const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({
    headless: true,
    executablePath: '/opt/pw-browsers/chromium'
  });

  const page = await browser.newPage({
    viewport: { width: 1366, height: 768 }
  });

  await page.setContent(`
    <html>
      <body style="font-family:sans-serif">
        <h1>CasaRay browser automation works</h1>
      </body>
    </html>
  `);

  await page.screenshot({
    path: 'tests/visual/screenshots/browser-smoke.png',
    fullPage: true
  });

  console.log('PASS: Chromium launched and screenshot created');
  await browser.close();
})();
