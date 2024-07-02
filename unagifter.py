from playwright.sync_api import sync_playwright, Playwright, expect
import re
import time
import configparser

# TODO:
# - handle expect() errors
# - add cli use help/docs etc
# - add variable products
# - verify config file inputs
# - make it schedulable/run as a service?

def main(playwright: Playwright):
    # Pull in config
    config = configparser.ConfigParser()
    # TODO: add like a default config name or a supplied one and have help popup if blank is used
    config.read('test.config')

    # Setup browser
    firefox = playwright.firefox
    browser = firefox.launch(headless=False)
    page = browser.new_page()

    login(page, config)
    add_product(page, config)
    checkout(page, config)
    time.sleep(5)
    browser.close()

def add_product(page, config):
    # Check to see if we're on the page via title
    page.goto("https://store.usps.com/store/product/cremated-remains-labels-P_LABEL139")
    expect(page).to_have_title(re.compile("Cremated Remains Labels"))

    # Set quantity & add to cart
    page.locator('id=cartQuantity').fill("5")
    page.get_by_role("button", name="Add to Cart").click()

def checkout(page, config):
    # Check to see if we're on the page via title
    page.goto("https://store.usps.com/store/cart/cart.jsp")
    expect(page).to_have_title(re.compile("Postal Store Cart"))

    page.get_by_role("button", name="Check Out Now").click()

    # Fill in address information
    # TODO: check to see if address is already in the book, select if so, add new addy if not
    page.get_by_role("link", name="Create a Shipping Address").click()
    page.locator('id=atg_store_firstNameInput').fill(config['ADDRESS']['firstName'])


def login(page, config):
    # Check to see if we're on the page via title
    page.goto("https://reg.usps.com/login")
    expect(page).to_have_title(re.compile("Sign In"))

    # Enter login info & login
    page.locator('id=username').fill(config['USPS']['username'])
    page.locator('id=password').fill(config['USPS']['password'])
    page.get_by_role("button", name="Sign In").click()

    # Delay to allow login - we can play w this value
    time.sleep(3)

    # Check to see if we logged in successfully and have the right login info
    page.goto("https://store.usps.com/store/myaccount/profile.jsp")
    expect(page.get_by_text(config['USPS']['email'], exact=True)).to_be_visible()

with sync_playwright() as playwright:
    main(playwright)