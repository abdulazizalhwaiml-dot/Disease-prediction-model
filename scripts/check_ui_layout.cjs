/* Browser regression for nested scrollbars, responsive labels and native help.
 * Start Streamlit first. See docs/DEVELOPMENT.md for the optional Playwright setup.
 */
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const baseUrl = process.env.MIZANAK_TEST_URL || 'http://localhost:8501';
const outputDir = process.env.MIZANAK_UI_OUTPUT;

async function main() {
  const browser = await chromium.launch({
    ...(process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH
      ? { executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH } : {}),
    args: ['--no-sandbox', '--disable-features=OverlayScrollbar'],
  });
  const checks = [];
  if (outputDir) fs.mkdirSync(outputDir, { recursive: true });
  try {
    for (const width of [320, 390, 768, 1100, 1285, 1440]) {
      const page = await browser.newPage({ viewport: { width, height: 900 } });
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      await page.goto(baseUrl);
      await page.getByTestId('stNumberInput').nth(4).waitFor();
      for (const language of ['ar', 'en']) {
        if (language === 'en') {
          await page.getByTestId('stMain').evaluate(e => e.scrollTo({ top: 0, behavior: 'instant' }));
          await page.getByTestId('stSelectbox').getByRole('combobox').click();
          await page.getByRole('option', { name: 'English', exact: true }).click();
          await page.getByRole('button', { name: 'Show my report', exact: true }).waitFor();
        }
        for (const zoom of [1, 1.25, 1.5, 2]) {
          await page.evaluate(value => { document.body.style.zoom = String(value); }, zoom);
          // Allow native widget sizing to settle after zoom and language changes.
          await page.waitForTimeout(100);
          const layout = await page.evaluate(() => {
            const roots = ['.st-key-topbar', '.st-key-input_panel'].map(s => document.querySelector(s));
            const scrollers = roots.flatMap(root => Array.from(root.querySelectorAll('*')))
              .filter(e => e.clientHeight > 0 && (
                (e.scrollHeight > e.clientHeight + 1 && /^(auto|scroll)$/.test(getComputedStyle(e).overflowY)) ||
                (e.scrollWidth > e.clientWidth + 1 && /^(auto|scroll)$/.test(getComputedStyle(e).overflowX))
              )).map(e => ({ test: e.dataset.testid, height: e.clientHeight, content: e.scrollHeight }));
            const headings = Array.from(document.querySelectorAll('[class*="st-key-label_"]'));
            const clipped = headings.flatMap(row => {
              const bounds = row.getBoundingClientRect();
              return Array.from(row.querySelectorAll('.field-title, [data-testid="stPopoverButton"]'))
                .filter(e => e.getBoundingClientRect().width > 0)
                .filter(e => {
                  const r = e.getBoundingClientRect();
                  return r.top < bounds.top - 2 || r.bottom > bounds.bottom + 2 ||
                    r.left < bounds.left - 2 || r.right > bounds.right + 2;
                }).map(e => e.textContent);
            });
            return {
              headings: headings.length, scrollers, clipped,
              mainScroll: getComputedStyle(document.querySelector('[data-testid="stMain"]')).overflowY,
            };
          });
          const context = JSON.stringify({ width, language, zoom, ...layout });
          assert.deepEqual(layout.scrollers, [], context);
          assert.equal(layout.headings, 8, context);
          assert.deepEqual(layout.clipped, [], context);
          assert.equal(layout.mainScroll, 'auto', context);
          checks.push({ width, language, zoom, ...layout });
        }
        await page.evaluate(() => { document.body.style.zoom = '1'; });
        const buttons = page.locator('[data-testid="stPopoverButton"]:visible');
        assert.equal(await buttons.count(), 8);
        for (let i = 0; i < 8; i++) {
          const button = buttons.nth(i);
          assert.ok((await button.textContent()).includes(language === 'ar' ? 'توضيح:' : 'Help:'));
          assert.ok((await button.boundingBox()).width <= 65);
          await button.focus();
          await page.keyboard.press('Enter');
          const dialog = page.getByRole('dialog');
          await dialog.waitFor();
          assert.ok((await dialog.innerText()).trim().length > 0);
          if (i === 1) await dialog.getByText(language === 'ar' ? 'ذكر أو أنثى.' : 'Male or female.', { exact: true }).waitFor();
          if (i === 2 || i === 4) await dialog.getByRole('img').waitFor();
          await page.keyboard.press('Escape');
          await dialog.waitFor({ state: 'hidden' });
        }
        if (outputDir && [390, 1100, 1285].includes(width)) {
          await page.getByTestId('stMain').evaluate(e => e.scrollTo(0, 0));
          await page.screenshot({ path: path.join(outputDir, `${language}-${width}.png`), fullPage: true });
        }
      }
      assert.deepEqual(errors, []);
      await page.close();
    }
  } finally {
    await browser.close();
  }
  if (outputDir) fs.writeFileSync(path.join(outputDir, 'layout.json'), JSON.stringify(checks, null, 2));
  console.log(`Passed ${checks.length} viewport/language/zoom cases, all eight help dialogs in both languages, and normal page scrolling.`);
}

main().catch(error => { console.error(error); process.exit(1); });
