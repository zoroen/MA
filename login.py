"""
login.py — Automates the SSM School Parent Portal
===================================================
Uses SeleniumBase with UC (Undetected Chrome) mode to bypass bot detection.

Flow:
  1. Open the login page
  2. Enter admission number (1979) and password (Sanjeev)
  3. Submit login via the page's own myFunction() JS call
  4. Wait for redirect to the dashboard (Header.aspx)
  5. Switch into the main content iframe (myIframe)
  6. Navigate to Academics section via homework_Click()
  7. Open Morning Assessment via assessment()
  8. Click the first available (Not Attended) assessment to begin it
"""

from seleniumbase import Driver
import time
import sys
import os


def wait_for_url_change(driver, old_url, timeout=15):
    """Poll until the browser URL changes from old_url, or timeout."""
    for _ in range(timeout * 2):
        if driver.current_url != old_url:
            return True
        time.sleep(0.5)
    return False


def main():
    # ─── 1. Launch a stealth Chrome browser (UC mode) ───
    # UC mode patches ChromeDriver internals so anti-bot systems
    # (Cloudflare, DataDome, etc.) cannot fingerprint it as automated.
    print("[1/7] Launching stealth Chrome browser...")
    driver = Driver(uc=True)

    try:
        # ─── 2. Navigate to the login page ───
        print("[2/7] Opening login page...")
        driver.get(
            "https://ssms.edu.in/SSM63/Parent_portal/parent_publish/Login_page.html?"
        )
        time.sleep(3)  # Let the page fully render (JS + CSS)

        # ─── 3. Enter credentials ───
        # We use execute_script() instead of send_keys() because the
        # username field has an onkeypress handler that only allows
        # numeric input and limits length to 5 chars. Setting .value
        # directly via JS bypasses these client-side restrictions.
        print("[3/7] Entering credentials...")
        driver.execute_script("document.getElementById('l1').value = '1979';")
        driver.execute_script("document.getElementById('l2').value = 'Sanjeev';")

        # ─── 4. Submit login ───
        # The login button calls myFunction() which makes an AJAX POST
        # to Home.aspx/Login. On success, it redirects to Header.aspx.
        # We call myFunction() directly via JS to avoid issues with
        # SeleniumBase UC mode disconnecting the driver during click().
        print("[4/7] Logging in...")
        old_url = driver.current_url
        driver.execute_script("myFunction();")

        # Wait for the AJAX login to complete and redirect to Header.aspx
        if wait_for_url_change(driver, old_url):
            print(f"       Redirected to: {driver.current_url}")
        else:
            print("       WARNING: URL didn't change — login may have failed!")
            # Check if an alert popped up (invalid credentials)
            try:
                alert = driver.switch_to.alert
                print(f"       Alert: {alert.text}")
                alert.accept()
            except Exception:
                pass
            sys.exit(1)

        # ─── 5. Switch into the main content iframe ───
        # Header.aspx embeds all content inside <iframe id="myIframe">
        # which loads Home.aspx with the student's session params.
        # We must switch the driver's context into this iframe before
        # we can interact with any elements inside it.
        print("[5/7] Switching into dashboard iframe...")
        time.sleep(3)  # Wait for iframe to load
        iframe = driver.find_element("css selector", "iframe#myIframe")
        driver.switch_to.frame(iframe)
        time.sleep(3)  # Wait for iframe content to render

        # ─── 6. Navigate to Academics → Morning Assessment ───
        # The dashboard is a grid of tiles. "Academics" tile has an
        # <img onclick="homework_Click()">. Calling it directly via JS
        # opens the Academics sidebar with sub-menu items.
        print("[6/7] Opening Academics section...")
        driver.execute_script("homework_Click();")
        time.sleep(3)

        # The sidebar now shows menu items including:
        #   - Attendance, Timetable, Assignment, Classwork, Portion,
        #   - Student Spotlight, e-Diary, Morning Assessment, Achievement Record
        # Morning Assessment is triggered by the assessment() JS function.
        print("[7/7] Opening Morning Assessment...")
        driver.execute_script("assessment();")
        time.sleep(5)  # Assessment grid takes a few seconds to load

        # ─── 7. Find and click the first available assessment ───
        # The assessment grid is in <tbody id="assgrid">.
        # Each row has cells: [Sl.No, Date-Subject, MaxMarks, MarksObtained,
        #                      InTime, SubmittedTime, TimeSpent, Status, ...]
        # We look for the first row with "Not Attended" status.
        rows = driver.find_elements("css selector", "tbody#assgrid tr")
        print(f"\n       Found {len(rows)} assessments in the grid.")

        clicked = False
        for i, row in enumerate(rows):
            try:
                cells = row.find_elements("css selector", "td")
                if len(cells) >= 8:
                    subject = cells[1].text.strip()
                    status = cells[7].text.strip()
                    print(f"       [{i+1}] {subject} — {status}")

                    if not clicked:
                        print(f"\n  >>> Clicking: {subject}")
                        # Click the subject cell (td[1]) to open the assessment
                        driver.execute_script("arguments[0].click();", cells[1])
                        clicked = True
                        break  # Page navigates away; remaining rows go stale
            except Exception:
                break  # Elements went stale after navigation

        if not clicked:
            print("\n       No 'Not Attended' assessments found today.")

        # ─── Keep browser open locally, auto-close in CI ───
        if os.environ.get('CI'):
            print("\n[DONE] Finished in CI mode.")
        else:
            print("\n[DONE] Browser will stay open.")
            print("   Press Ctrl+C in the terminal to close it.")
            while True:
                time.sleep(1)

    except KeyboardInterrupt:
        print("\nClosing browser...")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
