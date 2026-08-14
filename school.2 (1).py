from seleniumbase import SB
import random
import time

# ─── Use SeleniumBase in UC (Undetected Chrome) mode ───
# UC mode patches ChromeDriver so anti-bot systems can't fingerprint
# the browser as automated. SB() handles setup & teardown automatically.

with SB(uc=True, test=False) as sb:

    # 1. Navigate to the school portal login page
    sb.open("https://ssms.edu.in/SSM63/Parent_portal/parent_publish/Login_page.html?")
    time.sleep(2)

    # 2. Enter login credentials
    #    sb.type() finds the element, clears it, then types into it.
    #    "#l1" is a CSS selector for <input id="l1"> (username field).
    #    "#l2" is for <input id="l2"> (password field).
    sb.type("#l1", "1979")
    sb.type("#l2", "Sanjeev")

    # 3. Click the login button
    #    Using CSS selector 'button[type="submit"][onclick="myFunction()"]'
    sb.click('button[type="submit"][onclick="myFunction()"]')

    # 4. Switch into the iframe where the main content lives
    #    The school site nests everything inside <iframe id="myIframe">.
    #    We must switch context into it before we can interact with anything inside.
    print("Switching into iframe...")
    sb.switch_to_default_content()
    sb.switch_to_frame("iframe#myIframe")

    # 5. Navigate to Academics → Morning Assessment
    #    Instead of finding and clicking menu elements, we call the page's
    #    own JavaScript functions directly — this is faster and more reliable.
    sb.execute_script("homework_Click();")
    print("Successfully navigated to Academics!")
    time.sleep(3)

    sb.execute_script("assessment();")
    print("Boom! In Morning Assessment now.")
    time.sleep(3)

    # 6. Click the first subject in the assessment grid
    #    Wait for the grid to load, then click the subject cell in row 1.
    sb.wait_for_element_present("//tbody[@id='assgrid']/tr[1]/td[2]", by="xpath")
    subject_cell = sb.find_element("//tbody[@id='assgrid']/tr[1]/td[2]", by="xpath")
    sb.execute_script("arguments[0].click();", subject_cell)

    # 7. Maximize the window and re-enter the iframe
    #    After clicking the subject, the page reloads content inside the iframe,
    #    so we need to switch back to the main page and re-enter the iframe.
    sb.maximize_window()
    sb.switch_to_default_content()

    try:
        sb.switch_to_frame("iframe#myIframe")
        print("Switched into myIframe successfully!")
    except Exception as e:
        print("Already in iframe or iframe not found:", e)

    # 8. Wait for radio buttons (the MCQ answer options) to load
    try:
        sb.wait_for_element_present("input[type='radio']", timeout=20)
    except Exception:
        print("Warning: Radio buttons didn't load in time.")

    # 9. Find ALL radio buttons on the page
    all_radios = sb.find_elements("input[type='radio']")

    # 10. Group radio buttons by Question ID
    #     Each radio button has an ID like "3964_opt1", "3964_opt2", etc.
    #     We split on "_" to extract the question ID ("3964") and group
    #     all options belonging to the same question together.
    questions_dict = {}

    for radio in all_radios:
        element_id = radio.get_attribute("id") or radio.get_attribute("name") or ""
        q_id = element_id.split("_")[0]

        if q_id:
            if q_id not in questions_dict:
                questions_dict[q_id] = []
            questions_dict[q_id].append(radio)

    print(f"Total Radio Buttons Found: {len(all_radios)}")
    print(f"Total Unique Questions Identified: {len(questions_dict)}")

    # 11. Randomly answer each question
    #     For every question, pick one random option from its group,
    #     scroll it into view, then click it via JavaScript.
    for q_id, options in questions_dict.items():
        selected_choice = random.choice(options)
        sb.execute_script("arguments[0].scrollIntoView({block: 'center'});", selected_choice)
        time.sleep(0.5)
        sb.execute_script("arguments[0].click();", selected_choice)

    print("Finished answering all questions!")