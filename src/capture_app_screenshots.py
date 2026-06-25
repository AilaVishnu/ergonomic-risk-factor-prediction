"""
Capture 5 PNGs of the running Streamlit app at localhost:8501
and save them to outputs/app_screenshots/.

Streamlit must be running:
    python -m streamlit run app/streamlit_app.py

Then:
    python src/capture_app_screenshots.py
"""

import asyncio
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT  = ROOT / "outputs" / "app_screenshots"
URL  = "http://localhost:8501"

SHOTS = [
    ("web_01_header_demographic.png",  "Page header and Demographic Q1-17"),
    ("web_02_nmq.png",                  "Nordic + 7-day + outcomes Q18-24"),
    ("web_03_nasa_borg.png",            "NASA-TLX + Borg CR10 sliders Q25-36"),
    ("web_04_rula_qec.png",             "RULA + QEC observation + Predict button"),
    ("web_05_prediction_output.png",    "Predicted risk profile + recommendations"),
]


async def capture():
    OUT.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(viewport={"width": 1600, "height": 950})
        page = await context.new_page()

        await page.goto(URL, wait_until="networkidle")
        await page.wait_for_timeout(1500)

        # Hide Streamlit chrome (top bar, deploy button)
        await page.add_style_tag(content="""
            header[data-testid='stHeader'] { display: none !important; }
            .stDeployButton { display: none !important; }
            .stAppToolbar { display: none !important; }
        """)
        await page.wait_for_timeout(500)

        # ---- Shot 1: top of page (header + demographic) ----
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(400)
        await page.screenshot(path=str(OUT / SHOTS[0][0]), full_page=False)
        print(f"  saved {SHOTS[0][0]}")

        # ---- Shot 2: NMQ section ----
        await page.evaluate("""
            const headers = [...document.querySelectorAll('h2,h3')];
            const nmq = headers.find(h => h.textContent.includes('Nordic'));
            if (nmq) nmq.scrollIntoView({block: 'start'});
        """)
        await page.wait_for_timeout(400)
        await page.screenshot(path=str(OUT / SHOTS[1][0]), full_page=False)
        print(f"  saved {SHOTS[1][0]}")

        # ---- Shot 3: NASA-TLX + Borg ----
        await page.evaluate("""
            const headers = [...document.querySelectorAll('h2,h3')];
            const nasa = headers.find(h => h.textContent.includes('NASA-TLX'));
            if (nasa) nasa.scrollIntoView({block: 'start'});
        """)
        await page.wait_for_timeout(400)
        await page.screenshot(path=str(OUT / SHOTS[2][0]), full_page=False)
        print(f"  saved {SHOTS[2][0]}")

        # ---- Shot 4: RULA + QEC + Predict ----
        await page.evaluate("""
            const headers = [...document.querySelectorAll('h2,h3')];
            const rula = headers.find(h => h.textContent.includes('Posture observation'));
            if (rula) rula.scrollIntoView({block: 'start'});
        """)
        await page.wait_for_timeout(400)
        await page.screenshot(path=str(OUT / SHOTS[3][0]), full_page=False)
        print(f"  saved {SHOTS[3][0]}")

        # ---- Shot 5: click Predict, wait, capture output section ----
        # Predict button is a form submit button with text 'Predict risk levels'
        await page.evaluate("""
            const btns = [...document.querySelectorAll('button')];
            const predict = btns.find(b => b.textContent.includes('Predict'));
            if (predict) predict.click();
        """)
        await page.wait_for_timeout(3500)
        # Scroll to the "Predicted risk profile" heading
        await page.evaluate("""
            const headers = [...document.querySelectorAll('h2,h3')];
            const out = headers.find(h => h.textContent.includes('Predicted risk profile'));
            if (out) out.scrollIntoView({block: 'start'});
        """)
        await page.wait_for_timeout(700)
        await page.screenshot(path=str(OUT / SHOTS[4][0]), full_page=False)
        print(f"  saved {SHOTS[4][0]}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(capture())
    print(f"\nall 5 screenshots saved to {OUT.relative_to(ROOT)}")
