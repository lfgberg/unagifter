import re
from playwright.sync_api import Page, expect

# Browse to USPS
def test_browse(page: Page):
    page.goto("https://store.usps.com/store/results/free-shipping-supplies/shipping-supplies/_/N-alnx4jZ7d0v8v")

    # Check to see if we're on the page via title
    expect(page).to_have_title(re.compile("Shipping Supplies"))

def test_login(page: Page):
    page.goto("https://reg.usps.com/login")

    # Check to see if we're on the page via title
    expect(page).to_have_title(re.compile("Sign In"))

    # Enter login info & login
    page.get_by_role("text", name="username").fill("USERNAME HERE")
    page.get_by_role("text", name="password").fill("PASSWORD HERE")
    page.get_by_role("button", name="Sign In").click()

    # Check to see if we logged in successfully and have the right login info
    page.goto("https://store.usps.com/store/myaccount/profile.jsp")
    expect(page.get_by_text("EMAIL HERE", exact=True)).to_be_visible()