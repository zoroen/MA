from seleniumbase import SB
import time

# ─── Use SeleniumBase in UC (Undetected Chrome) mode ───
# UC mode patches the ChromeDriver so anti-bot systems
# (Cloudflare, DataDome, etc.) cannot fingerprint it as automated.
# SB() is a context manager that handles browser setup & teardown.

with SB(uc=True, test=False) as sb:

    # 1. Navigate to the school portal login page
    sb.open("https://ssms.edu.in/SSM63/Parent_portal/parent_publish/Login_page.html?")
    time.sleep(2)

    # 2. Switch into the iframe that contains the assessment form
    #    The page embeds its main content inside an <iframe id="myIframe">.
    #    Selenium (and SeleniumBase) can only interact with elements
    #    inside an iframe after explicitly switching context into it.
    sb.switch_to_frame("iframe#myIframe")

    # 3. Find and click the Submit button
    #    sb.click() waits for the element to be clickable before clicking,
    #    which replaces the manual WebDriverWait + EC.element_to_be_clickable combo.
    print("Locating the Submit button...")
    sb.click("#submit")
    print("Clicked Submit!")

    # 4. Handle the JavaScript confirmation alert popup
    #    After clicking Submit, the page fires a JS alert().
    #    We wait for it, print its text, then accept (dismiss) it.
    print("Waiting for confirmation alert...")
    sb.wait_for_and_accept_alert(timeout=5)
    print("Assessment successfully submitted and alert accepted automatically!")