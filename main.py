from playwright.sync_api import sync_playwright
from time import sleep # I really want to do this, yet I musn't...
import email_processor
import json

def browser(playwright):
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
    with open("info.json", "r") as f:
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

    # Test code to open an singular email
    # email_row = tab2.locator("tr:has-text('Appily')")
    # email_row.click()
    # sleep(5)


if __name__ == "__main__":
    with sync_playwright() as playwright:
        browser(playwright)