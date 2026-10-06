"""Capture actual browser-rendered outputs from the executed assignment notebook."""
from pathlib import Path
from playwright.sync_api import sync_playwright

folder = Path(__file__).resolve().parent
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 950, "height": 1100}, device_scale_factor=2)
    # Screenshot only local notebook output; no network resources are needed.
    page.route("http://**/*", lambda route: route.abort())
    page.route("https://**/*", lambda route: route.abort())
    page.goto((folder / "Assignment2_Executed_Notebook.html").as_uri(), wait_until="load")
    for gate in ["h", "y", "z"]:
        source = f'qc_{gate}, state_{gate}, counts_{gate} = run_single_qubit_circuit("{gate}")'
        cell = page.locator(".jp-CodeCell").filter(has_text=source)
        assert cell.count() == 1, (gate, cell.count())
        outputs = cell.locator(".jp-OutputArea-child")
        assert outputs.count() == 4, (gate, outputs.count())
        for index, kind in [(1, "circuit"), (2, "histogram")]:
            target = outputs.nth(index).locator("img")
            target.scroll_into_view_if_needed()
            target.wait_for(state="visible")
            target.screenshot(path=str(folder / f"screenshot_{kind}_{gate}.png"))
            print(f"Captured screenshot_{kind}_{gate}.png", flush=True)
    browser.close()
