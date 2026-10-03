// Screenshots the prismarine-viewer page of mc_bot.js (--viewer 3008) into <dir>/<unix_ms>.jpg until killed.
//   LD_LIBRARY_PATH=/mnt/mc/libs/root/usr/lib/x86_64-linux-gnu PUPPETEER_CACHE_DIR=/mnt/mc/puppeteer node mc_record.js frames 3008 8
const puppeteer = require('puppeteer'), fs = require('fs'), path = require('path')
const [dir, port, fps] = [process.argv[2] || 'frames', process.argv[3] || 3008, +(process.argv[4] || 8)]
;(async () => {
  fs.mkdirSync(dir, { recursive: true })
  const exe = require('child_process').execSync(`ls ${process.env.PUPPETEER_CACHE_DIR}/chrome-headless-shell/linux-*/chrome-headless-shell-linux64/chrome-headless-shell`).toString().trim()
  const browser = await puppeteer.launch({ executablePath: exe, args: ['--no-sandbox', '--use-gl=angle', '--use-angle=gl-egl', '--ignore-gpu-blocklist', '--enable-gpu'] }) // hardware EGL: ~70 ms per shot, SwiftShader: 2-4 s
  const page = await browser.newPage()
  await page.setViewport({ width: 960, height: 540 })
  page.on('console', m => { if (m.type() === 'error') console.log('page error:', m.text()) })
  await page.goto(`http://127.0.0.1:${port}`)
  await new Promise(r => setTimeout(r, 5000))
  console.log('recording to', dir)
  let n = 0
  for (;;) {
    const t0 = Date.now()
    await page.screenshot({ path: path.join(dir, `${t0}.jpg`), type: 'jpeg', quality: 80 })
    if (++n % 100 === 0) console.log(n, 'frames,', Date.now() - t0, 'ms per shot')
    await new Promise(r => setTimeout(r, Math.max(0, 1000 / fps - (Date.now() - t0))))
  }
})()
