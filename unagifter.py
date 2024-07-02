from playwright.sync_api import sync_playwright, Playwright, expect
import re
import time

def run(playwright: Playwright):
    firefox = playwright.firefox
    browser = firefox.launch(headless=False)
    page = browser.new_page()

    # Check to see if we're on the page via title
    page.goto("https://store.usps.com/store/results/free-shipping-supplies/shipping-supplies/_/N-alnx4jZ7d0v8v")
    expect(page).to_have_title(re.compile("Shipping Supplies"))

    page.goto("https://reg.usps.com/login")

    # Check to see if we're on the page via title
    expect(page).to_have_title(re.compile("Sign In"))

    # Enter login info & login
    page.locator('id=username').fill("")
    page.locator('id=password').fill("")
    page.get_by_role("button", name="Sign In").click()

    # Delay to allow login - we can play w this value
    time.sleep(5)

    # Check to see if we logged in successfully and have the right login info
    page.goto("https://store.usps.com/store/myaccount/profile.jsp")
    expect(page.get_by_text("", exact=True)).to_be_visible()

    browser.close()

with sync_playwright() as playwright:
    run(playwright)