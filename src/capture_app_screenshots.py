"""
Capture screenshots of the running multi-page Streamlit app.

The app must already be running:
    python -m streamlit run app/streamlit_app.py

Then:
    python src/capture_app_screenshots.py

Writes seven PNGs to outputs/app_screenshots/:
  Home, Assessment (top / NMQ / NASA-Borg / RULA-QEC),
  Results, Methodology, About.
"""

import asyncio
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT  = ROOT / "outputs" / "app_screenshots"
URL  = "http://localhost:8501"


async def _click_sidebar(page, label):
    await page.evaluate(f"""
        const links = [...document.querySelectorAll('a')];
        const target = links.find(a => a.textContent.trim() === {label!r});
        if (target) target.click();
    """)
    await page.wait_for_timeout(1500)


async def _scroll_to(page, needle):
    """Scroll the first element whose textContent contains `needle` to
    the top of the viewport."""
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
        context = await browser.new_context(viewport={"width": 1600, "height": 1100})
        page = await context.new_page()

        await page.goto(URL, wait_until="networkidle")
        await page.wait_for_timeout(2000)

        # Hide Streamlit toolbar / deploy chrome
        await page.add_style_tag(content="""
            header[data-testid='stHeader'] { display: none !important; }
            .stDeployButton { display: none !important; }
            .stAppToolbar { display: none !important; }
        """)
        await page.wait_for_timeout(300)

        # -------------------- HOME --------------------
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(300)
        await page.screenshot(path=str(OUT / "web_01_home.png"), full_page=True)
        print("  saved web_01_home.png")

        # -------------------- ASSESSMENT --------------------
        await _click_sidebar(page, "Assessment")

        # Top with sample profile buttons + demographic section
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(300)
        await page.screenshot(path=str(OUT / "web_02_assessment_top.png"),
                              full_page=False)
        print("  saved web_02_assessment_top.png")

        # NMQ + 7-day + outcomes
        await _scroll_to(page, "Nordic Musculoskeletal")
        await page.screenshot(path=str(OUT / "web_03_assessment_nmq.png"),
                              full_page=False)
        print("  saved web_03_assessment_nmq.png")

        # NASA-TLX + Borg CR10 sliders
        await _scroll_to(page, "NASA-TLX")
        await page.screenshot(path=str(OUT / "web_04_assessment_nasa_borg.png"),
                              full_page=False)
        print("  saved web_04_assessment_nasa_borg.png")

        # RULA + QEC observation
        await _scroll_to(page, "Posture observation")
        await page.screenshot(path=str(OUT / "web_05_assessment_rula_qec.png"),
                              full_page=False)
        print("  saved web_05_assessment_rula_qec.png")

        # -------------------- RESULTS via High-risk preset --------------------
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(300)
        await page.evaluate("""
            const btns = [...document.querySelectorAll('button')];
            const high = btns.find(b => b.textContent.trim() === 'High-risk rider');
            if (high) high.click();
        """)
        await page.wait_for_timeout(4000)  # redirect + render

        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(300)
        await page.screenshot(path=str(OUT / "web_06_results.png"), full_page=True)
        print("  saved web_06_results.png")

        # -------------------- METHODOLOGY --------------------
        await _click_sidebar(page, "Methodology")
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(400)
        await page.screenshot(path=str(OUT / "web_07_methodology.png"), full_page=True)
        print("  saved web_07_methodology.png")

        # -------------------- ABOUT --------------------
        await _click_sidebar(page, "About")
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(400)
        await page.screenshot(path=str(OUT / "web_08_about.png"), full_page=True)
        print("  saved web_08_about.png")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(capture())
    print(f"\nall screenshots saved to {OUT.relative_to(ROOT)}")
