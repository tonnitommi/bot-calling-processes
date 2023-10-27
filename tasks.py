from robocorp.tasks import task
from robocorp import browser, workitems
import json

@task
def report_sales_data():
    '''This task reads the sales data from the incoming workitem(s) and submits it to the intranet website. Input work item needs to have the following fields:
    - firstname: First name of the sales person
    - lastname: Last name of the sales person
    - salesresult: Sales result for the month
    - salestarget: Sales target for the month (will be made to match the nearest dropdown value)'''

    browser.configure(
        slowmo=400,
        headless=False,
    )

    # Read the incoming workitem(s)
    open_the_intranet_website()
    log_in()

    for item in workitems.inputs:
        fill_and_submit_sales_form(item)


def open_the_intranet_website():
    """Navigates to the given URL"""
    browser.goto("https://robotsparebinindustries.com/")


def log_in():
    """Fills in the login form and clicks the 'Log in' button"""
    page = browser.page()
    page.fill("#username", "maria")
    page.fill("#password", "thoushallnotpass")
    page.click("button:text('Log in')")

def fill_and_submit_sales_form(item):
    """Fills in the sales data and click the 'Submit' button"""
    page = browser.page()

    print(item.payload["query"])

    data = json.loads(item.payload["query"])

    print(json.dumps(data, indent=4))

    # type conversions
    if isinstance(data["salestarget"], int):
        target = data["salestarget"]
    else:
        # If it's not an integer, try to convert it from a string
        try:
            target = int(data["salestarget"])
        except ValueError:
            raise TypeError(f"Cannot convert {data['salestarget']} to integer")


    if isinstance(data["salesresult"], int):
        result = data["salesresult"]
    else:
        # If it's not an integer, try to convert it from a string
        try:
            result = int(data["salesresult"])
        except ValueError:
            raise TypeError(f"Cannot convert {data['salesresult']} to integer")

    page.fill("#firstname", data["firstname"])
    page.fill("#lastname", data["lastname"])
    page.fill("#salesresult", str(result))

    # map the sales target value to dropdown values
    possible_values = list(range(5000, 100001, 5000))
    nearest_value = min(possible_values, key=lambda x:abs(x-target))
    page.select_option("#salestarget", str(nearest_value))

    page.click("text=Submit")

    if result < 0.5 * target:
        outload = "POOR"
    elif result < target:
        outload = "BELOW"
    else:
        outload = "ABOVE"

    workitems.outputs.create(
        payload={"response": outload},
    )