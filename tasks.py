from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
import zipfile
import os

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=1000,
    )
    open_robot_order_website()
    orders = get_orders()
    pdf_files_to_zip = []
    for order in orders:
        close_annoying_modal()

        fill_the_form(order)
        orderRobot()
        screenshotName = screenshot_robot(order["Order number"])
        pdfName = store_receipt_as_pdf(order["Order number"])
        pdf_files_to_zip.append(pdfName)
        embed_screenshot_to_receipt(screenshotName, pdfName)
        nextOrder()


def open_robot_order_website():
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def get_orders():
    """
    Downloads the orders file
    """
    url = "https://robotsparebinindustries.com/orders.csv"
    fileName = "orders.csv"
    tables = Tables()
    http = HTTP()
    http.download(url, overwrite=True)
    csv = tables.read_table_from_csv(fileName)
    data = [dict(row) for row in csv]

    return data

def close_annoying_modal():
    page = browser.page()
    page.click("button:text('Yep')")

def loop_through_data():
    print("")

def fill_the_form(formData):
    page = browser.page()
    page.select_option("#head", formData["Head"])
    page.click("#id-body-"+formData["Body"])
    page.fill(f"input[placeholder='Enter the part number for the legs']", formData["Legs"])
    page.fill("#address", formData["Address"])
    page.click("#preview")

def orderRobot():
    alert_selector = 'div.alert.alert-danger[role="alert"]'
    page = browser.page()
    page.click("#order")
    try:
        exists = page.query_selector(alert_selector)
    except:
        page.click("#order-another");
        return;    
    while (True):
        if(exists):
            page.click("#order")
        else:
            break;
        try:
            exists = page.query_selector(alert_selector)
        except:
            break;

def screenshot_robot(order_number):
    page = browser.page()
    element = page.query_selector("#robot-preview-image")
    screenshotPath = f"output/screenshot/{order_number}.png"
    element.screenshot(path=screenshotPath)
    return screenshotPath

def store_receipt_as_pdf(order_number):
    page = browser.page()
    sales_results_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf.html_to_pdf(sales_results_html, f"output/PDF/{order_number}.pdf")
    return f"output/PDF/{order_number}.pdf"

def embed_screenshot_to_receipt(screenshot, pdf_file):
    pdf = PDF()
    pdf.add_files_to_pdf(files=[pdf_file,screenshot],target_document=pdf_file)
    # pdf.open_pdf(pdf_file)
    # pdf.add_image(screenshot) 

def archive_receipts(pdf_files, zip_file_name):
     with zipfile.ZipFile(zip_file_name, 'w') as zipf:
        for pdf_file in pdf_files:
            if os.path.exists(pdf_file):  # Check if the PDF file exists
                zipf.write(pdf_file, os.path.basename(pdf_file))  # Add PDF to zip
                print(f"Added {pdf_file} to {zip_file_name}.")
            else:
                print(f"File {pdf_file} does not exist and will not be added.")

def nextOrder():
    page = browser.page()
    page.click("#order-another")