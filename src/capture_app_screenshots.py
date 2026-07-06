"""
Capture screenshots of the running multi-page Streamlit app.

The app must already be running:
    python -m streamlit run app/streamlit_app.py

Then:
    python src/capture_app_screenshots.py

Writes eight PNGs to outputs/app_screenshots/:
  Home, Assessment (top / NMQ / NASA-Borg / RULA-QEC),
  Results, Methodology, About.
"""

import asyncio
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT  = ROOT / "outputs" / "app_screenshots"
URL  = "http://localhost:8501"


async def _click_button(page, label):
    """Click a button whose visible text equals `label`."""
    await page.evaluate(f"""
        const btns = [...document.querySelectorAll('button')];
        const target = btns.find(b => b.textContent.trim() === {label!r});
        if (target) target.click();
    """)
    await page.wait_for_timeout(2000)


async def _click_sidebar(page, label):
    """Click a sidebar page link by visible text."""
    await page.evaluate(f"""
        const links = [...document.querySelectorAll(
            "[data-testid='stSidebarNav'] a")];
        const target = links.find(a => a.textContent.trim() === {label!r});
        if (target) target.click();
    """)
    await page.wait_for_timeout(1800)


async def _scroll_to(page, needle):
    await page.evaluate(f"""
        const hs = [...document.querySelectorAll('h1, h2, h3, h4, p, strong')];
        const target = hs.find(h => h.textContent.includes({needle!r}));
        if (target) target.scrollIntoView({{block: 'start', behavior: 'instant'}});
    """)
    await page.wait_for_timeout(400)


async def capture():
    OUT.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(
            viewport={"width": 1600, "height": 1100}
        )
        page = await context.new_page()

        await page.goto(URL, wait_until="networkidle")
        await page.wait_for_timeout(2500)

        # Hide the Streamlit top-header row so screenshots start clean
        await page.add_style_tag(content="""
            header[data-testid='stHeader'] { display: none !important; }
            .stDeployButton { display: none !important; }
            .stAppToolbar   { display: none !important; }
        """)
        await page.wait_for_timeout(300)

        # -------------------- HOME --------------------
        # Home hides the sidebar; take a full-page shot of the Vercel hero
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(300)
        await page.screenshot(path=str(OUT / "web_01_home.png"),
                              full_page=True)
        print("  saved web_01_home.png")

        # -------------------- ASSESSMENT --------------------
        # Navigate via the primary Start Assessment button (the sidebar
        # is hidden on Home so we can't click a nav link)
        await _click_button(page, "Start Assessment")

        # Slice 1: top of Assessment (sample profiles + demographic Q1-17)
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(400)
        await page.screenshot(path=str(OUT / "web_02_assessment_top.png"),
                              full_page=False)
        print("  saved web_02_assessment_top.png")

        # Slice 2: NMQ + follow-ups
        await _scroll_to(page, "Nordic Musculoskeletal")
        await page.screenshot(path=str(OUT / "web_03_assessment_nmq.png"),
                              full_page=False)
        print("  saved web_03_assessment_nmq.png")

        # Slice 3: NASA-TLX + Borg CR10 sliders
        await _scroll_to(page, "NASA-TLX")
        await page.screenshot(path=str(OUT / "web_04_assessment_nasa_borg.png"),
                              full_page=False)
        print("  saved web_04_assessment_nasa_borg.png")

        # Slice 4: RULA + QEC
        await _scroll_to(page, "Posture observation")
        await page.screenshot(path=str(OUT / "web_05_assessment_rula_qec.png"),
                              full_page=False)
        print("  saved web_05_assessment_rula_qec.png")

        # -------------------- RESULTS (High-risk preset) --------------------
        # 1. 'High-risk rider' -- autofills the form (no navigation).
        # 2. 'Predict risk levels' -- submits and jumps to Results.
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(300)
        await _click_button(page, "High-risk rider")
        await page.wait_for_timeout(1500)               # let re-render land

        await _click_button(page, "Predict risk levels")
        await page.wait_for_timeout(3500)               # predict + switch_page

        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(500)
        await page.screenshot(path=str(OUT / "web_06_results.png"),
                              full_page=True)
        print("  saved web_06_results.png")

        # -------------------- METHODOLOGY --------------------
        await _click_sidebar(page, "Methodology")
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(500)
        await page.screenshot(path=str(OUT / "web_07_methodology.png"),
                              full_page=True)
        print("  saved web_07_methodology.png")

        # -------------------- ABOUT --------------------
        await _click_sidebar(page, "About")
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(500)
        await page.screenshot(path=str(OUT / "web_08_about.png"),
                              full_page=True)
        print("  saved web_08_about.png")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(capture())
    print(f"\nall screenshots saved to {OUT.relative_to(ROOT)}")
