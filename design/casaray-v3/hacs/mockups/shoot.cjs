const {chromium} = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const dir = process.argv[2];
  const b = await chromium.launch();
  for (const f of fs.readdirSync(dir).filter(f => f.endsWith('.html'))) {
    const [w, h] = fs.readFileSync(path.join(dir, f.replace('.html', '.size')), 'utf8').trim().split(' ').map(Number);
    const p = await b.newPage({viewport: {width: w, height: h}, deviceScaleFactor: 2});
    await p.goto('file://' + path.resolve(dir, f));
    await p.evaluate(() => document.fonts.ready);
    const over = await p.evaluate(() => [...document.querySelectorAll('.card,.sheet,.footer')].filter(e =>
      e.scrollWidth > e.clientWidth + 1).map(e => e.className));
    await p.screenshot({path: path.join(dir, f.replace('.html', '.png'))});
    console.log(f, w + 'x' + h, over.length ? 'OVERFLOW ' + over.join(',') : 'ok');
    await p.close();
  }
  await b.close();
})();
