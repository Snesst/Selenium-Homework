from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
import pandas as pd
from datetime import datetime

# Set up Chrome options
options = webdriver.ChromeOptions()
# Set the download directory to the current working directory
download_directory = os.getcwd()  # Save to current terminal directory
options.add_experimental_option("prefs", {
    "download.default_directory": download_directory,
    "download.prompt_for_download": False,
    "safebrowsing.enabled": True
})

# Create a new instance of the Chrome driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    # Navigate to the webpage
    driver.get("https://www.manulife.com.hk/en/individual/fund-price/mpf.html/v2/funddetails/SHK130?product=Manulife%20Global%20Select%20(MPF)%20Scheme")

    # Wait for the disclaimer modal to appear
    time.sleep(5)  # Wait for the page to load

    # Click the "Agree" button
    agree_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Agree')]"))
    )
    driver.execute_script("arguments[0].click();", agree_button)
    print("Agree button clicked.")

    # Wait for the page to load completely
    time.sleep(10)  # Increased wait time

    # Find all clickable elements related to "Export"
    export_buttons = WebDriverWait(driver, 30).until(
        EC.presence_of_all_elements_located((By.XPATH, "//*[contains(text(), 'Export')]"))
    )

    # Click the first "Export" button found
    if export_buttons:
        driver.execute_script("arguments[0].click();", export_buttons[0])
        print("Export button clicked.")
    else:
        print("No export buttons found.")

    # Wait for the CSV option to become available
    csv_radio_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//label[normalize-space()='Export to .csv']"))
    )
    csv_radio_button.click()  # Click the radio button for CSV export
    print("CSV export option selected.")

    # Click the final "Export" button to initiate download
    final_export_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Export']"))
    )
    final_export_button.click()
    print("Final Export button clicked.")

    # Wait for the download to complete
    print("Waiting for the download to complete...")
    time.sleep(10)  # You can adjust this if needed

    # Process the downloaded CSV file to change date format
    downloaded_files = os.listdir(download_directory)

    for filename in downloaded_files:
        if filename.startswith("Manulife-Fund-SHK130") and filename.endswith(".csv"):
            csv_file_path = os.path.join(download_directory, filename)

            # Load the CSV file into a DataFrame
            df = pd.read_csv(csv_file_path, header=None)

            # Check the contents of the DataFrame
            print("Original DataFrame:")
            print(df)

            # Assuming the date is in the second column (index 1)
            if len(df.columns) > 1:
                # Convert the date from mm/dd/yyyy to dd/mm/yyyy
                def convert_date(date_str):
                    if isinstance(date_str, str) and date_str.count('/') == 2:
                        month, day, year = date_str.split('/')
                        return f"{day}/{month}/{year}"
                    return date_str  # Return the original value if it doesn't match

                # Apply the conversion only to rows starting from index 1 to avoid the header
                df[1] = df[1].apply(convert_date)

            # Get today's date for the new filename
            today = datetime.now().strftime("%d_%m_%Y")
            new_filename = f"Manulife-Fund-SHK130_{today}.csv"
            new_file_path = os.path.join(download_directory, new_filename)

            # Save the modified DataFrame back to the new CSV file
            df.to_csv(new_file_path, index=False, header=False)
            print(f"Date format changed and saved as '{new_filename}'.")

            break

    # Print confirmation of the downloaded file
    print(f"Manulife-Fund-SHK130_{today}.csv downloaded successfully.")

finally:
    # Close the browser
    driver.quit()