import os
import io
import json
import gzip
import csv
import pandas as pd
import requests
from datetime import datetime
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ------------------------
# CONFIG
# ------------------------
START_URL = "https://training.gov.au/search?searchText=&searchType=RTO&status=0&status=2"
START_API_URL = "api/organisation/csv"

today_str = datetime.today().strftime("%Y-%m-%d")

QUALIFICATIONS_API_TEMPLATE = (
    "https://training.gov.au/api/organisation/{code}/scope"
    f"?api-version=1.0&offset=0&pageSize=100&delivery=true"
    f"&filters=componentType==qualification,DateNullSearch=={today_str}&sorts=code"
)

COURSES_API_TEMPLATE = (
    "https://training.gov.au/api/organisation/{code}/scope"
    f"?api-version=1.0&offset=0&pageSize=100&delivery=true"
    f"&filters=componentType==accreditedCourse,DateNullSearch=={today_str}&sorts=code"
)

# API → schema mapping
API_TO_SCHEMA = {
    "Organisation Code": "Code",
    "Legal Name": "Legal Name",
    "Business Name(s)": "Business Name",
    "Status": "Status",
    "Registration Manager": "Registration Manager",
    "Legal Authority": "Legal Authority",
    "Initial Registration Date": "Initial Registration Date",
    "Registration Start Date": "Start Date",
    "Registration End Date": "End Date",
    "Head Office Physical Address": "Address",
    "RTO Type": "RTO Type",
    "ABN": "ABN",
    "ACN": "ACN",
    "URL": "Web Address",
    "CEO Contact Name": "Chief Executive Contact Name",
    "CEO Email": "Chief Executive Emails",
    "CEO Mobile": "Chief Executive Title",
    "CEO Phone": "Chief Executive Phone",
    "Public Enquiries Contact Name": "Public Enquiries Contact Name",
    "Public Enquiries Contact Role Job Title": "Public Enquiries Contact Title",
    "Public Enquiries Email": "Public Enquiries Email",
    "Public Enquiries Phone": "Public Enquiries Phone",
    "Registration Enquiries Contact Name": "Registration Enquiries Contact Name",
    "Registration Enquiries Contact Role Job Title": "Registration Enquiries Title",
    "Registration Enquiries Email": "Registration Enquiries Email",
    "Registration Enquiries Phone": "Registration Enquiries Phone",
}

# Final schema — exact order
PHASE2_COLUMNS = [
    "Code", "Legal Name", "Business Name", "Status", "ABN", "ACN", "RTO Type", "Web Address",
    "Registration Manager", "Legal Authority", "Initial Registration Date", "Start Date", "End Date", "Address",
    "Chief Executive Contact Name", "Chief Executive Emails", "Chief Executive Title", "Chief Executive Phone",
    "Public Enquiries Contact Name", "Public Enquiries Contact Title", "Public Enquiries Email", "Public Enquiries Phone",
    "Registration Enquiries Contact Name", "Registration Enquiries Title", "Registration Enquiries Email", "Registration Enquiries Phone",
    "Qualifications", "Courses"
]

# ------------------------
# FUNCTIONS
# ------------------------
def get_all_rtos_via_selenium(url, api):
    """
    Opens RTO search, clicks export, intercepts CSV API, returns DataFrame and RTO codes.
    """
    print("🚀 Starting Selenium to fetch ALL RTOs...")
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 20)

    try:
        driver.get(url)
        print("✅ Website loaded.")

        # Open export dropdown
        trigger_btn = wait.until(EC.element_to_be_clickable((By.ID, "trigger-button_13")))
        trigger_btn.click()
        print("✅ Export dropdown opened.")

        # Click Export as CSV
        export_csv_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Export as CSV']")))
        export_csv_btn.click()
        print("✅ Clicked 'Export as CSV', waiting for API...")

        # Wait for API request
        request = driver.wait_for_request(api, timeout=60)
        csv_bytes = gzip.decompress(request.response.body)
        csv_text = csv_bytes.decode("utf-8-sig")

        df = pd.read_csv(io.StringIO(csv_text))
        rto_codes = df["Organisation Code"].astype(str).tolist()

        print(f"🎉 Got {len(rto_codes)} RTO codes.")
        return df, rto_codes

    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None
    finally:
        driver.quit()

def transform_api_response(df, mapping, final_columns):
    df = df.rename(columns=mapping)
    for col in final_columns:
        if col not in df.columns:
            df[col] = ""
    return df[final_columns].fillna("")

def save_filtered_csv(df, filename):
    os.makedirs("data", exist_ok=True)
    file_path = os.path.join("data", filename)
    df.to_csv(file_path, index=False, encoding="utf-8-sig")
    print(f"✅ CSV saved: {file_path}")
    return file_path


def get_scope_data(api_url, retries=3, delay=1):
    """
    Fetch and parse scope data from the given API URL with retries and 404 handling.
    Returns a list where each element is a list of "key: value" strings.
    """
    for attempt in range(retries):
        try:
            r = requests.get(api_url, timeout=15)
            if r.status_code == 404:
                print(f"[INFO] No scope data found (404) for {api_url}")
                return []

            r.raise_for_status()
            json_data = r.json()

            if not isinstance(json_data, dict) or "value" not in json_data:
                print(f"[WARN] Unexpected response schema for {api_url}")
                return []

            if json_data.get("count", 0) == 0 or not json_data["value"]:
                return []

            result = []
            for item in json_data["value"]:
                formatted_item = [
                    f"deliveryAct: {item.get('deliveryAct', '')}",
                    f"deliveryNsw: {item.get('deliveryNsw', '')}",
                    f"deliveryNt: {item.get('deliveryNt', '')}",
                    f"deliveryQld: {item.get('deliveryQld', '')}",
                    f"deliverySa: {item.get('deliverySa', '')}",
                    f"deliveryTas: {item.get('deliveryTas', '')}",
                    f"deliveryVic: {item.get('deliveryVic', '')}",
                    f"deliveryWa: {item.get('deliveryWa', '')}",
                    f"isInternational: {item.get('isInternational', '')}",
                    f"code: {item.get('code', '')}",
                    f"componentType: {item.get('componentType', '')}",
                    f"componentTypeLabel: {item.get('componentTypeLabel', '')}",
                    f"endDate: {item.get('endDate', '')}",
                    f"extent: {item.get('extent', '')}",
                    f"extentLabel: {item.get('extentLabel', '')}",
                    f"isImplicit: {item.get('isImplicit', '')}",
                    f"nrtId: {item.get('nrtId', '')}",
                    f"startDate: {item.get('startDate', '')}",
                    f"status: {item.get('status', '')}",
                    f"statusLabel: {item.get('statusLabel', '')}",
                    f"title: {item.get('title', '')}"
                ]
                result.append(formatted_item)

            return result

        except requests.exceptions.RequestException as e:
            print(f"[WARN] Attempt {attempt+1}/{retries} failed for {api_url}: {e}")
            if attempt < retries - 1:
                time.sleep(delay * (attempt + 1))
            else:
                return []

    return []


def format_list_of_lists_no_outer_brackets(items: list[list[str]]) -> str:
    """
    Turn a list of lists like [[a,b],[c,d]] into:
    "[a, b], [c, d]" (no outer brackets).
    """
    if not items:
        return ""
    return ", ".join("[" + ", ".join(inner) + "]" for inner in items)


# ------------------------
# FULL RUN MODE
# ------------------------
def run_full():
    df_all, rto_codes = get_all_rtos_via_selenium(START_URL, START_API_URL)
    if df_all is None:
        exit("❌ Could not fetch RTO list.")

    df_transformed = transform_api_response(df_all, API_TO_SCHEMA, PHASE2_COLUMNS)

    quals_map = {}
    courses_map = {}

    for idx, code in enumerate(rto_codes, start=1):
        padded_code = str(code).zfill(4)
        print(f"[INFO] ({idx}/{len(rto_codes)}) Fetching scope for RTO {padded_code}...")

        quals_data = get_scope_data(QUALIFICATIONS_API_TEMPLATE.format(code=padded_code))
        courses_data = get_scope_data(COURSES_API_TEMPLATE.format(code=padded_code))

        # Map using the unpadded code from CSV
        quals_map[code] = format_list_of_lists_no_outer_brackets(quals_data)
        courses_map[code] = format_list_of_lists_no_outer_brackets(courses_data)

    df_transformed["Qualifications"] = df_transformed["Code"].map(quals_map)
    df_transformed["Courses"] = df_transformed["Code"].map(courses_map)

    save_filtered_csv(df_transformed, "rto_with_qualifications_and_courses.csv")
    print("🎯 All done.")


# ------------------------
# SINGLE DEBUG MODE
# ------------------------
def run_debug_single(target_code="0049"):
    # Load the Phase 2 CSV
    df_all = pd.read_csv("data/rto_filtered.csv")
    df_transformed = transform_api_response(df_all, API_TO_SCHEMA, PHASE2_COLUMNS)

    padded_code = target_code.zfill(4)
    print(f"[DEBUG] Fetching Qualifications & Courses for {padded_code}...")

    quals_data = get_scope_data(QUALIFICATIONS_API_TEMPLATE.format(code=padded_code))
    courses_data = get_scope_data(COURSES_API_TEMPLATE.format(code=padded_code))

    # Update only the matching row
    df_transformed.loc[df_transformed["Code"] == int(target_code), "Qualifications"] = \
        format_list_of_lists_no_outer_brackets(quals_data)
    df_transformed.loc[df_transformed["Code"] == int(target_code), "Courses"] = \
        format_list_of_lists_no_outer_brackets(courses_data)

    save_filtered_csv(df_transformed, f"rto_debug_{target_code}.csv")
    print(f"✅ Debug CSV updated with qualifications & courses for {target_code}.")


if __name__ == "__main__":
    # Uncomment one of these:
    run_full()
    # run_debug_single("0049")
