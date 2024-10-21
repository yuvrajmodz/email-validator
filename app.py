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

        # Extract the email status
        result = soup.find('li', class_='status success ctc-container')

        if result:
            # Get the data text from the status
            data_text = result['data-text'] if 'data-text' in result.attrs else None

            # Return the result in JSON format
            return jsonify({"response": data_text})

        # If email status not found, return an error message
        return jsonify({"response": "Email status not found or invalid email."})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5016))
    app.run(host='0.0.0.0', port=port, debug=True)