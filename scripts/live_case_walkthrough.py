"""Run the requested Cedar/Beacon walkthrough against the existing local server."""
import argparse
import json
from pathlib import Path

from playwright.sync_api import sync_playwright


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[1] / "artifacts" / "live-walkthrough")
args = parser.parse_args()
ARTIFACTS = args.output_dir
ARTIFACTS.mkdir(parents=True, exist_ok=True)
results = {"url": "http://127.0.0.1:8000", "runs": {}, "browser_errors": []}


def save():
    (ARTIFACTS / "results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 1050})
    page.on("pageerror", lambda error: results["browser_errors"].append(str(error)))
    try:
        page.goto(results["url"])
        page.locator(".case-item").nth(2).wait_for()
        results["config"] = page.evaluate("state.config")

        def investigate(name):
            page.select_option("#mode", "live")
            print(f"START {name}: Live AI", flush=True)
            page.locator("#run-btn").click()
            page.locator("#run-btn:not([disabled])").wait_for(timeout=125000)
            data = page.evaluate("""() => ({
                mode: document.querySelector('#mode').value,
                message: document.querySelector('#message').textContent,
                error: document.querySelector('#message').classList.contains('error'),
                result: state.result,
                source_ids: activeSources().map(s => s.id),
                versions: state.current.versions || []
            })""")
            results["runs"][name] = data
            page.screenshot(path=str(ARTIFACTS / f"{name}.png"), full_page=True)
            save()
            print(json.dumps({"run": name, "error": data["error"],
                              "message": data["message"],
                              "summary": (data["result"] or {}).get("report", {}).get("summary"),
                              "meta": (data["result"] or {}).get("meta")}, ensure_ascii=True), flush=True)
            return data

        page.locator(".case-item").filter(has_text="Cedar").click()
        before = investigate("cedar-before")
        results["supplement_button_label"] = page.locator("#supplement-btn").inner_text()
        page.locator("#supplement-btn").click()
        after = investigate("cedar-after")
        if after["result"]:
            page.locator('[data-tab="history"]').click()
            results["cedar_versions_text"] = page.locator("#report-content").inner_text()
            results["cedar_version_cards"] = page.locator(".version-card").count()
            page.screenshot(path=str(ARTIFACTS / "cedar-versions.png"), full_page=True)
            with page.expect_download() as download:
                page.locator("#bundle-btn").click()
            download.value.save_as(str(ARTIFACTS / "cedar-case.json"))
        save()

        page.locator(".case-item").filter(has_text="Beacon").click()
        beacon = investigate("beacon")
        if beacon["result"]:
            results["beacon_tabs"] = {}
            for tab in ("overview", "timeline", "commitments"):
                page.locator(f'[data-tab="{tab}"]').click()
                results["beacon_tabs"][tab] = page.locator("#report-content").inner_text()
                page.screenshot(path=str(ARTIFACTS / f"beacon-{tab}.png"), full_page=True)
            with page.expect_download() as download:
                page.locator("#bundle-btn").click()
            download.value.save_as(str(ARTIFACTS / "beacon-case.json"))
        save()
        print("COMPLETE " + str(ARTIFACTS), flush=True)
    finally:
        save()
        browser.close()
