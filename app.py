from flask import Flask, jsonify
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

@app.route('/<email>', methods=['GET'])
def verify_email(email):
    with sync_playwright() as p:
        # Start browser session
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Go to the email verification website
        page.goto("https://www.verifyemailaddress.org")

        # Fill the email field
        page.fill('input[name="email"]', email)

        # Click the 'Verify Email' button
        page.click('button:has-text("Verify Email")')

        # Wait for the result page to load
        page.wait_for_url("https://www.verifyemailaddress.org/email-validation")

        # Get the page content after verification
        content = page.content()
        browser.close()

        # Use BeautifulSoup to parse the HTML
        soup = BeautifulSoup(content, 'html.parser')

        # Extract the relevant <li> element with the success class
        result = soup.find('li', class_='success ctc-container')

        if result:
            # Get the 'data-text' attribute from the <li> element
            data_text = result.get('data-text', None)

            # Return the extracted data in the 'record' field of the JSON response
            return jsonify({"record": data_text})

        # If no valid result was found, return an error message
        return jsonify({"record": "No valid email status found or invalid email."})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5015))
    app.run(host='0.0.0.0', port=port, debug=True)