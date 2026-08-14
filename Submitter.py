"""
Submitter.py — Full SSM School Assessment Auto-Submitter
=========================================================
Uses SeleniumBase with UC (Undetected Chrome) mode to bypass bot detection.

Flow:
  1. Open the login page
  2. Enter admission number (6767) and password (ilikefeet)
  3. Submit login via the page's own myFunction() JS call
  4. Wait for redirect to the dashboard (Header.aspx)
  5. Switch into the main content iframe (myIframe)
  6. Navigate to Academics section via homework_Click()
  7. Open Morning Assessment via assessment()
  8. Click the first available (Not Attended) assessment
  9. Randomly answer all MCQ questions (radio buttons)
  10. Click Submit and accept the confirmation alert
"""

from seleniumbase import Driver
import random
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
    print("[1/10] Launching stealth Chrome browser...")
    driver = Driver(uc=True)

    try:
        # ─── 2. Navigate to the login page ───
        print("[2/10] Opening login page...")
        driver.get(
            "https://ssms.edu.in/SSM63/Parent_portal/parent_publish/Login_page.html?"
        )
        time.sleep(3)

        # ─── 3. Enter credentials ───
        print("[3/10] Entering credentials...")
        driver.execute_script("document.getElementById('l1').value = '<enter your admn no>';")
        driver.execute_script("document.getElementById('l2').value = '<enter your password>';")

        # ─── 4. Submit login ───
        print("[4/10] Logging in...")
        old_url = driver.current_url
        driver.execute_script("myFunction();")

        if wait_for_url_change(driver, old_url):
            print(f"        Redirected to: {driver.current_url}")
        else:
            print("        WARNING: URL didn't change -- login may have failed!")
            try:
                alert = driver.switch_to.alert
                print(f"        Alert: {alert.text}")
                alert.accept()
            except Exception:
                pass
            sys.exit(1)

        # ─── 5. Switch into the main content iframe ───
        print("[5/10] Switching into dashboard iframe...")
        time.sleep(3)
        iframe = driver.find_element("css selector", "iframe#myIframe")
        driver.switch_to.frame(iframe)
        time.sleep(3)

        # ─── 6. Navigate to Academics ───
        print("[6/10] Opening Academics section...")
        driver.execute_script("homework_Click();")
        time.sleep(3)

        # ─── 7. Open Morning Assessment ───
        print("[7/10] Opening Morning Assessment...")
        driver.execute_script("assessment();")
        time.sleep(5)

        # ─── 8. Click the first "Not Attended" assessment ───
        rows = driver.find_elements("css selector", "tbody#assgrid tr")
        print(f"\n        Found {len(rows)} assessments in the grid.")

        clicked = False
        for i, row in enumerate(rows):
            try:
                cells = row.find_elements("css selector", "td")
                if len(cells) >= 8:
                    subject = cells[1].text.strip()
                    status = cells[7].text.strip()
                    print(f"        [{i+1}] {subject} -- {status}")

                    if status == "Not Attended" and not clicked:
                        print(f"\n  >>> Clicking: {subject}")
                        driver.execute_script("arguments[0].click();", cells[1])
                        clicked = True
                        break
            except Exception:
                break

        if not clicked:
            print("\n        No 'Not Attended' assessments found today.")
            sys.exit(0)

        # ─── 9. Answer all MCQ questions randomly ───
        # After clicking a subject, the page loads the questions inside
        # the iframe. We need to maximize the window, switch back to
        # the main page, and re-enter the iframe to access the questions.
        print("\n[8/10] Waiting for questions to load...")
        driver.maximize_window()
        driver.switch_to.default_content()
        time.sleep(3)

        # Re-enter the iframe
        try:
            iframe = driver.find_element("css selector", "iframe#myIframe")
            driver.switch_to.frame(iframe)
            print("        Switched into iframe for questions.")
        except Exception as e:
            print(f"        Could not switch to iframe: {e}")
            sys.exit(1)

        # Wait for radio buttons to appear (the MCQ answer options)
        print("[9/10] Finding and answering questions...")
        time.sleep(5)

        all_radios = driver.find_elements("css selector", "input[type='radio']")

        # Group radio buttons by Question ID.
        # Each radio has an ID like "3964_opt1", "3964_opt2", etc.
        # Splitting on "_" gives us the question ID ("3964").
        questions_dict = {}
        for radio in all_radios:
            element_id = radio.get_attribute("id") or radio.get_attribute("name") or ""
            q_id = element_id.split("_")[0]
            if q_id:
                if q_id not in questions_dict:
                    questions_dict[q_id] = []
                questions_dict[q_id].append(radio)

        print(f"        Total Radio Buttons Found: {len(all_radios)}")
        print(f"        Total Unique Questions: {len(questions_dict)}")

        # For each question, randomly pick one option, scroll to it, and click
        for q_id, options in questions_dict.items():
            selected = random.choice(options)
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", selected
            )
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", selected)

        print("        Finished answering all questions!")

        # ─── 10. Click Submit and accept the confirmation alert ───
        print("[10/10] Submitting assessment...")
        submit_btn = driver.find_element("css selector", "#submit")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_btn)
        time.sleep(0.5)
        submit_btn.click()

        # Handle the confirmation alert popup
        time.sleep(2)
        try:
            alert = driver.switch_to.alert
            print(f"        Alert: '{alert.text}'")
            alert.accept()
            print("        Assessment submitted and alert accepted!")
        except Exception:
            print("        No alert appeared (may have submitted silently).")

        # ─── Keep browser open locally, auto-close in CI ───
        if os.environ.get('CI'):
            print("\n[DONE] Assessment complete in CI mode.")
        else:
            print("\n[DONE] Assessment complete!")
            print("       Browser will stay open. Press Ctrl+C to close.")
            while True:
                time.sleep(1)

    except KeyboardInterrupt:
        print("\nClosing browser...")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()

