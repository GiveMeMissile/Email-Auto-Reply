from playwright.sync_api import sync_playwright
from time import sleep
from llm_handler import LLMManager
import email_processor
import json


# Constants IG
PASSWORD_FILE = "info.json"
# Using my school website to access gmail bc google does not like scrapers ):
START_WEBSITE = "https://aisd-tx.us001-rapididentity.com/p/portal"
MAX_TOKENS = 256


def browser(playwright, ai_manager):
    # Set Headless to False for testing and if you want to see the browser at work, keep it True otherwise
    browser = playwright.chromium.launch(channel="msedge", headless=False)

    # Create context for web browser
    context = browser.new_context()

    # Open new tab and go to gmail
    tab1 = context.new_page()
    tab1.goto("https://aisd-tx.us001-rapididentity.com/p/portal")
    sleep(1)

    # Note: I will be accessing gmail through my school's portal until I am able to directly access gmail 
    # through a google account, password setup for use will be set up later.
    # Log into school gmail
    with open(PASSWORD_FILE, "r") as f:
        data = json.load(f)
    tab1.get_by_label("Username").fill(data["Username"])
    tab1.get_by_role("button", name="Go").click()
    sleep(1)
    tab1.get_by_role("textbox", name="password").fill(data["Password"])
    tab1.get_by_role("button", name="Go").click()

    # Get to gmail
    with context.expect_page() as new_tab:
        sleep(1)
        tab1.get_by_role("button", name="Gmail").first.click()
    tab2 = new_tab.value

    # Get gmail HTML
    tab2.wait_for_selector(".Cp")
    gmail_html = tab2.locator(".Cp").inner_html()

    # Get the names of the unread Emails
    unread_emails = email_processor.get_unread_emails(gmail_html)
    email_text = access_email(tab2, unread_emails[0])
    sleep(1)
    respond_to_email(tab2, email_text, unread_emails[0], ai_manager)

def access_email(tab, info):

    email_row = tab.locator("tr:has-text('" + info[1] + "').zA.zE")
    email_row.click()

    tab.wait_for_selector(".ii.gt")
    email_html = tab.locator(".ii.gt").inner_html()
    text = email_processor.proccess_email_html(email_html)
    tab.wait_for_load_state("domcontentloaded")
    tab.locator(".pYTkkf-JX-I.pYTkkf-JX-I-ql-ay5-ays.DILLkc").click()
    tab.wait_for_load_state("domcontentloaded")
    return text

def respond_to_email(tab, email_text, info, ai_manager):
    message_box = tab.get_by_role("textbox", name="Message Body")
    tokens = 0
    ai_text = ""
    while True:
        ai_token = ai_manager.forward(email_text, info[0], ai_text)
        tokens += 1
        print(f"AI Text: {ai_text}")
        if ai_manager.stop_generating(ai_token):
            break
        elif tokens >= MAX_TOKENS:
            break
        else:
            ai_text += ai_token
            message_box.fill(ai_text)



if __name__ == "__main__":
    print("Setting up Local LLM...")
    ai_manager = LLMManager()
    print("Local LLM has been set up!")
    with sync_playwright() as playwright:
        browser(playwright, ai_manager)