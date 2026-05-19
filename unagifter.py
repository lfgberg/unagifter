from playwright.sync_api import sync_playwright, Playwright, expect
import re
import time
import argparse
import json

# TODO:
# - handle expect() errors
# - add cli use help/docs etc
# - add variable products
# - verify config file inputs
# - make it schedulable/run as a service?
# - get the confirmation numbers at the end of the run
# - add a scientology dvd option

def main(playwright: Playwright):
    # Import product catalog & config
    catalog = read_json("products.json")
    config = read_json("test-config.json") # TODO: Validate config
    validate_config(config, catalog)

    # Setup browser
    firefox = playwright.firefox
    browser = firefox.launch(headless=False)
    page = browser.new_page()

    # Place the orders
    login(page, config)
    empty_cart(page)
    add_product(page, config)
    checkout(page, config)

    browser.close()

def validate_config(config, catalog):
    # Validate basic info
    assert(validate_email(config['usps']['email']) == True, "Invalid USPS email.")
    assert(validate_email(config['address']['email']) == True, "Invalid recipient email.")
    assert(validate_phone_number(config['address']['phone']) == True, "Invalid recipient phone number.")

    # Validate order configuration
    for product in config['usps-order']:
        # Ensure product exists
        if (not product in catalog):
            raise Exception("Product SKU not found in catalog.")
        
        # Verify quantities
        print(product['quantity'])
        if (product['quantity'] <= 0):
            raise Exception("Invalid order quantity.")

def validate_phone_number(phoneNumber):
    regex = r'(0|91)?[6-9][0-9]{9}'
    if(re.fullmatch(regex, phoneNumber)):
        return True
    else:
        return False

def validate_email(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if(re.fullmatch(regex, email)):
        return True
    else:
        return False

def read_json(filename):
    with open(filename, "r") as jsonfile:
        data = json.load(jsonfile)
        jsonfile.close()
        return data

def add_product(page, config):
    # Check to see if we're on the page via title
    page.goto("https://store.usps.com/store/product/cremated-remains-labels-P_LABEL139")
    expect(page).to_have_title(re.compile("Cremated Remains Labels"))

    # Set quantity & add to cart
    page.locator('id=cartQuantity').fill("1")
    page.get_by_role("button", name="Add to Cart").click()

def checkout(page, config):
    # Check to see if we're on the page via title
    page.goto("https://store.usps.com/store/cart/cart.jsp")
    expect(page).to_have_title(re.compile("Postal Store Cart"))

    page.get_by_role("button", name="Check Out Now").click()

    # Fill in address information
    # TODO: check to see if address is already in the book, select if so, add new addy if not
    page.get_by_role("link", name="Edit").click()

    page.locator('id=atg_store_firstNameInput').fill(config['address']['firstName'])
    page.locator('id=atg_store_lastNameInput').fill(config['address']['lastName'])
    page.locator('id=atg_store_streetAddressInput').fill(config['address']['addressLine1'])
    page.locator('id=atg_store_streetAddressOptionalInput').fill(config['address']['addressLine2'])
    page.locator('id=atg_store_localityInput').fill(config['address']['city'])
    page.locator('id=atg_store_stateSelect').select_option(config['address']['state'])
    page.locator('id=atg_store_postalCodeInput').fill(config['address']['zip'])
    page.locator('id=atg_store_countryNameSelect').select_option('United States') # Only domestic shipments are allowed
    page.locator('id=atg_store_telephoneInput').fill(config['address']['phone'])
    page.locator('id=atg_store_emailInput').fill(config['address']['email'])

    time.sleep(1)
    page.get_by_role("button", name="Save Address").click()
    time.sleep(1)
    page.get_by_role("button", name="Ship to this Address").click()
    time.sleep(1)
    page.get_by_label('USPS Ground Advantage™: Arrives in 2-5 business days   -   $0.00').click()
    page.get_by_role("button", name="Confirm Shipment").click()
    time.sleep(1)
    page.get_by_role("button", name="Place My Order").click()
    time.sleep(1)
    page.get_by_role("button", name="I Agree").click()

def empty_cart(page):
     # Check to see if we're on the page via title
    page.goto("https://store.usps.com/store/cart/cart.jsp")
    expect(page).to_have_title(re.compile("Postal Store Cart"))

    page.get_by_role("button", name="Clear Shopping Cart").click()

def login(page, config):
    # Check to see if we're on the page via title
    page.goto("https://reg.usps.com/login")
    expect(page).to_have_title(re.compile("Sign In"))

    # Enter login info & login
    page.locator('id=username').fill(config['usps']['username'])
    page.locator('id=password').fill(config['usps']['password'])
    page.get_by_role("button", name="Sign In").click()

    # Delay to allow login - we can play w this value
    time.sleep(2)

    # Check to see if we logged in successfully and have the right login info
    page.goto("https://store.usps.com/store/myaccount/profile.jsp")
    expect(page.get_by_text(config['usps']['email'], exact=True)).to_be_visible()

with sync_playwright() as playwright:
    main(playwright)