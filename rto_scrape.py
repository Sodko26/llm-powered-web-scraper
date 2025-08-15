# rto_scrape.py

# ── requirements ─────────────────────────────────────────────────────────
# pip install crawl4ai openai pydantic python-dotenv
# playwright install

import os, json, asyncio
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CrawlerRunConfig,
    CacheMode,
    LLMConfig
)

from crawl4ai.extraction_strategy import LLMExtractionStrategy

# ── 1. load keys ─────────────────────────────────────────────────────────
load_dotenv()
# highlight-start
# DEFINE all the URLs we need to visit to get the complete data
BASE_URL = "https://training.gov.au/organisation/details/0115"
URLS_TO_SCRAPE = [
    f"{BASE_URL}/summary",
    f"{BASE_URL}/contacts",
    f"{BASE_URL}/addresses",
    f"{BASE_URL}/qualifications",
    f"{BASE_URL}/courses",
]
# highlight-end

# ── 2. declare a schema that matches the *instruction* ───────────────────
# (Your Pydantic models: Qualifications, Courses, RTO_Model remain the same)
class Qualifications(BaseModel):
    code: str = Field(..., description="Qualification code, e.g., 'BSB60420'")
    title: str = Field(..., description="Qualification title, e.g., 'Advanced Diploma of Leadership and Management'")
    status: str = Field(..., description="Qualification status, e.g., 'Current'")
    start_date: str = Field(..., description="Start date of the qualification e.g., '17/Dec/2020'")
    end_date: str = Field(..., description="End date of the qualification, e.g., '31/Dec/2030'")
    delivery_notification: list[str] = Field(..., description="Delivery notification regions, e.g. ['NSW', 'VIC', 'QLD', 'SA', 'WA', 'TAS', 'NT', 'ACT']")

class Courses(BaseModel):
    code: str = Field(..., description="Course code, e.g., '10787NAT'")
    title: str = Field(..., description="Course title, e.g., 'Advanced Diploma of Digital Marketing'")
    status: str = Field(..., description="Course status, e.g., 'Non-Current'")
    start_date: str = Field(..., description="Start date of the course e.g., '17/Dec/2020'")
    end_date: str = Field(..., description="End date of the course, e.g., '31/Dec/2030'")
    delivery_notification: list[str] = Field(..., description="Delivery notification regions, e.g. ['NSW', 'VIC', 'QLD', 'SA', 'WA', 'TAS', 'NT', 'ACT']")

class RTO_Model(BaseModel):
    code: str | None = Field(..., description="Unique identifier for the model, found in Summary section (/summary)")
    legal_name: str | None = Field(..., description="Legal name of the Registered Training Organisation, found in Summary section (/summary)")
    business_name: str | None = Field(..., description="Business name of the Registered Training Organisation, found in Summary section (/summary)")
    status: str | None = Field(..., description="Status e.g., 'current', found in Summary section (/summary)")
    abn: str | None = Field(..., description="Australian Business Number e.g '40009668553', found in Summary section (/summary)")
    acn: str | None = Field(..., description="Australian Company Number e.g '0009668553', found in Summary section (/summary)")
    rto_type: str | None = Field(..., description="Type of Registered Training Organisation, found in Summary section (/summary)")
    web_address: str | None = Field(..., description="The url web address of the Registered Training Organisation e.g 'http://aim.com.au/', found in Summary section (/summary)")
    registration_manager: str | None = Field(..., description="The name of the registration manager e.g 'Australian Skills Quality Authority', found in Summary section (/summary)")
    initial_registration_date: str | None = Field(..., description="Initial registration date of the Registered Training Organisation, found in Summary section (/summary)")
    start_date: str | None = Field(..., description="Start date of the Registered Training Organisation, found in Summary section (/summary)")
    end_date: str | None = Field(..., description="End date of the Registered Training Organisation, found in Summary section (/summary)")
    legal_authority: str | None = Field(..., description="Legal authority of the Registered Training Organisation, found in Summary section (/summary)")
    chief_executive_contact_name: str | None = Field(..., description="Name of the Chief Executive Contact, found in Contact section (/contact)")
    chief_executive_title: str | None = Field(..., description="Title of the Chief Executive Contact, found in Contact section (/contact)")
    chief_executive_phone: str | None = Field(..., description="Phone number of the Chief Executive Contact, found in Contact section (/contact)")
    chief_executive_email: str | None = Field(..., description="Email of the Chief Executive Contact, found in Contact section (/contact)")
    registration_enquiries_contact_name: str | None = Field(..., description="Name of the Registration Enquiries Contact, found in Contact section (/contact)")
    registration_enquiries_title: str | None = Field(..., description="Title of the Registration Enquiries Contact, found in Contact section (/contact)")
    registration_enquiries_phone: str | None = Field(..., description="Phone number of the Registration Enquiries Contact, found in Contact section (/contact)")
    registration_enquiries_email: str | None = Field(..., description="Email of the Registration Enquiries Contact, found in Contact section (/contact)")
    public_enquiries_contact_name: str | None = Field(..., description="Name of the Public Enquiries Contact, found in Contact section (/contact)")
    public_enquiries_title: str | None = Field(..., description="Title of the Public Enquiries Contact, found in Contact section (/contact)")
    public_enquiries_phone: str | None = Field(..., description="Phone number of the Public Enquiries Contact, found in Contact section (/contact)")
    public_enquiries_email: str | None = Field(..., description="Email of the Public Enquiries Contact, found in Contact section (/contact)")
    address: str | None = Field(..., description="Physical address of the Registered Training Organisation Head office, found in Addresses section (/addresses)")
    qualifications: list[Qualifications] = Field(..., description="List of qualifications in the format 'Code, Title, Status, Start Date, End Date, Delivery Notification(list)', found in Qualifications section (/qualifications)")
    courses: list[Courses] = Field(..., description="List of courses in the format 'Code, Title, Status, Start Date, End Date, Delivery Notification(list)', found in Courses section (/courses)")

class URL_Model(BaseModel):
    abn: str | None = Field(..., description="Australian Business Number e.g '40009668553', found in Summary section (/summary)")
    web_address: str | None = Field(..., description="The url web address of the Registered Training Organisation e.g 'http://aim.com.au/', found in Summary section (/summary)")

URL_INSTRUCTION_TO_LLM = """
You are an expert-level AI specializing in extracting structured educational data from a government listing for Australian Registered Training Organizations website.
Your task is to analyze the RTO on thE input url and populate a detailed JSON object with two details: the ABN and the Web Address.
1) Extract the ABN as a string of digits in a no-space format, e.g "40009668553".
For example:
If the html is <a target="_blank" rel="nofollow" class="mint-link" to="https://abr.business.gov.au/search.aspx?SearchText=42 950 261 731" href="https://abr.business.gov.au/search.aspx?SearchText=42 950 261 731">42 950 261 731<span class="external-icon"><span class="mint-icon" aria-hidden="true"><span aria-hidden="true" class="icon material-icons">arrow_outward</span><!----></span><span class="visually-hidden">Opens in new window or tab</span></span></a>
Extract the element text '42 950 261 731' and return it as a string in the JSON output as '42950261731', following the schema below.
2) Extract the RTO's web address information as a url/href.
For example:
if the html is <a title="Visit the website for Impact Community Services Limited" target="_blank" rel="nofollow" class="mint-link" to="http://www.impact.org.au" href="http://www.impact.org.au"><span class="d-none d-lg-inline">http://www.impact.org.au</span><span class="d-lg-none">Visit</span><span class="external-icon"><span class="mint-icon" aria-hidden="true"><span aria-hidden="true" class="icon material-icons">arrow_outward</span><!----></span><span class="visually-hidden">Opens in new window or tab</span></span></a>
Extract the url 'http://www.impact.org.au' and return it as a string in the JSON output, following the schema below.

🧾 Format Example (Return your data in this exact structure):
Generated json (the only output you should return):
{
    "ABN": "",
    "Web Address": ""
}

🔒 Strict Instructions:
JSON Only: Your entire response must be a single, valid JSON object. Do not include any text, explanations, or markdown formatting before or after the JSON.
Full Page Scan: You MUST analyze the entire page content. Identify all relevant distinct information sections, whether they are presented as tabs, accordions, tables or scroll-to headings, and process the information within each before generating your output.
Data Accuracy Rule: If you cannot find a specific data point explicitly mentioned on the page or its allowed linked pages, you MUST use a null value. If a permitted secondary link cannot be accessed, rely only on information from the primary page. DO NOT infer, guess, or invent data.
Empty Values: If information is not found, use "", [], null, or false as appropriate.

"""

# Your INSTRUCTION_TO_LLM remains the same
INSTRUCTION_TO_LLM = """
You are an expert-level AI specializing in extracting structured educational data from a government listing for Australian Registered Training Organizations website.
Your task is to analyze the RTO on these 5 urls and populate a detailed JSON object with the details.
Extract all of the RTOs information from the urls based on the schema below (the urls will be provided in the input):
(Make sure to visit all relevant sections of each RTO page based on the urls to collect the data: Summary, Contacts, Addresses, Qualifications, Courses; without confusing them with other sections like Units or Skill Sets.)

Data     Data to Scrape  Section or Source URL Suffix
Code     The Organisation Code itself.   /summary
Legal name   The Legal Name of the organisation. /summary
Business name   The Business Name of the organisation.   /summary
Status   The current registration Status.    /summary
ABN  The Australian Business Number (ABN) as a string of digits.   /summary
ACN  The Australian Company Number (ACN) as a string of digits.    /summary
RTO Type     The RTO Type.   /summary
Web address  The url for the web address for the RTO.   /summary
Registration Manager     The name of the Registration Manager.   /summary
Initial Registration Date    The Initial Registration Date.  /summary
Start Date   The "Start date" of the current registration period.    /summary
End Date     The "End date" of the current registration period.  /summary
Legal Authority    The Legal Authority of the RTO.   /summary
Chief Executive...  Scrape the Name, Title, Phone, and Email for the "Chief Executive" contact. /contacts
Registration Enquiries...   Scrape the Name, Title, Phone, and Email for the "Registration Enquiries" contact.   /contacts
Public Enquiries...  Scrape the Name, Title, Phone, and Email for the "Public Enquiries" contact.    /contacts
Address  Only the head address. /addresses
Qualification 1  The code, title, status, start date, end date and delivery notification of the first qualification listed.   /qualifications
Qualification 2  The code, title, status, start date, end date and delivery notification of the second qualification listed.  /qualifications
...Qualification N  Continue extracting all qualifications, e.g "Advanced Diploma of Leadership and Management"
Each qualification should contain: "Code, Title, Status, Start Date, End Date, Delivery Notification".
Course 1     The code, title, status, start date, end date and delivery notification of the first course listed.  /courses
Course 2     The code, title, status, start date, end date and delivery notification of the second course listed. /courses
...Course N  Continue extracting all courses, e.g "Advanced Diploma of Digital Marketing".
Each course should be in the format: "Code, Title, Status, Start Date, End Date, Delivery Notification".
Do not include any other information or sections at all, like data from the 'Units Section' or the 'Skill sets' Section.

🔒 Strict Instructions:
JSON Only: Your entire response must be a single, valid JSON object. Do not include any text, explanations, or markdown formatting before or after the JSON.
Full Page Scan: You MUST analyze the entire page content. Identify all relevant distinct information sections, whether they are presented as tabs, accordions, tables or scroll-to headings, and process the information within each before generating your output.
Data Accuracy Rule: If you cannot find a specific data point explicitly mentioned on the page or its allowed linked pages, you MUST use a null value. If a permitted secondary link cannot be accessed, rely only on information from the primary page. DO NOT infer, guess, or invent data.
Empty Values: If information is not found, use "", [], null, or false as appropriate.
⭐ CRITICAL INSTRUCTION: HTML Formatting for Descriptions
This rule governs how you handle text-heavy content. For the fields listed below, you MUST convert the original webpage's formatting into a clean HTML string instead of plain text.
Applicable Fields: This rule applies to: Course Overview, Entry Pathways & General Requirements, Prerequisite Description, Subject Description, and all other Description fields in the schema (e.g., within Work Placement, Funding Types, RPL, etc.).
Replicate Structure: Faithfully reproduce the structure of the source content (headings, paragraphs, lists).
Allowed Tags Only: Your entire HTML string must only use the following tags: <h1>, <h2>, <p>, <i>, <span>, <table>, <li>, <ol>, <ul>, <a> and <div>.
No CSS or Attributes: Do NOT include any <style> blocks or inline style="..." attributes. Do not add any other attributes (like id, target).
Mandatory Classes: You MUST add the following classes to these specific tags whenever you use them. No other classes are allowed.
When you create a <table>, it MUST be wrapped in a <div class="table-wrapper">.
Every <ul> tag MUST be written as <ul class="li-wrapper">.
Every <ol> tag MUST be written as <ol class="o-li-wrapper">.
⭐ CRITICAL INSTRUCTION: Parsing Top-Level Links
For the `web_address` field, the input text will contain markdown links in the format `[link text](http://www.impact.org.au/)`.
You MUST extract ONLY the URL from inside the parentheses e.g 'http://www.impact.org.au/'. If the URL is not present, return null.
⭐ CRITICAL INSTRUCTION: Exact JSON Schema Adherence
This is your most important instruction. The JSON you return MUST use the exact keys, casing, spacing, and structure shown in the "Format Example" below.
Any deviation is a failure. For example, Fee Items is correct; FeeItems is incorrect. PDF Present is correct; PDFPresent is incorrect.
Pay extremely close to every key name in the provided schema.
⭐ CRITICAL INSTRUCTION: Address
Extract only the head/main address from Addresses.
⭐ CRITICAL INSTRUCTION: Web Address
Extract the exact url provided of the web address. Do not leave it as a null value if a url is provided.
⭐ CRITICAL INSTRUCTION: Registration Manager
Extract the exact url provided of the registration manager. Do not leave it as a null value if a url is provided.
⭐ CRITICAL INSTRUCTION: ACN
Extract it as a string digits in a no-space format, e.g "40009668553" (read it as digits not a url).
⭐ CRITICAL INSTRUCTION: ACN
Extract it as a string of digits in a no-space format, e.g "0009668553".
⭐ CRITICAL INSTRUCTION: Phone Numbers
Extract all phone numbers as a string of digits in a no-space format, e.g "0298765432".
Extract it as a string of digits in a no-space format, e.g "0009668553".
⭐ CRITICAL INSTRUCTION: Qualifications
Return a list of qualifications, each in the format “Code, Title, Status (current or non-current), Start Date, End Date, Delivery Notification”, all found in a table in the Qualifications section. Return delivery notification as a list as such:
If ‘NATIONAL’, return “NSW, VIC, QLD, SA, WA, TAS, NT, ACT”.
Do not confuse qualifications data with courses data, units data, or skill sets data.
Return the list of qualifications data in the same single json output with all the other data.
⭐ CRITICAL INSTRUCTION: Courses
Return a list of courses, each in the format “Code, Title, Status (current or non-current), Start Date, End Date, Delivery Notification”, all found in a table in the Courses section. Return delivery notification as a list as such that:
If ‘VIC’, return “VIC”, if NSW, return “NSW”, if ‘NATIONAL’, return “NSW, VIC, QLD, SA, WA, TAS, NT, ACT”.
Do not confuse courses data with qualifications data, units data, or skill sets data.
Return the list of courses data in the same single json output with all the other data.

🧾 Format Example (Return your data in this exact structure):
Generated json (the only output you should return):
{
    "Code": "",
    "Legal Name": "",
    "Business Name": "",
    "Status": "",
    "ABN": "",
    "ACN": "",
    "RTO Type": "",
    "Web Address": "",
    "Registration Manager": "",
    "Initial Registration Date": "",
    "Start Date": "",
    "End Date": "",
    "Legal Authority": "",
    "Chief Executive Contact Name": "",
    "Chief Executive Title": "",
    "Chief Executive Phone": "",
    "Chief Executive Email": "",
    "Registration Enquiries Contact Name": "",
    "Registration Enquiries Title": "",
    "Registration Enquiries Phone": "",
    "Registration Enquiries Email": "",
    "Public Enquiries Contact Name": "",
    "Public Enquiries Title": "",
    "Public Enquiries Phone": "",
    "Public Enquiries Email": "",
    "Address": "",
    "Qualifications": [{
        "Code": "",
        "Title": "",
        "Status": "",
        "Start Date": "",
        "End Date": "",
        "Delivery Notification": []
    }],
    "Courses": [{
        "Code": "",
        "Title": "",
        "Status": "",
        "Start Date": "",
        "End Date": "",
        "Delivery Notification": []
    }]
}
"""

# ── 3. Configure the LLM ──────────────────────────────────────────────────
# llm_cfg = LLMConfig(
#     provider="gemini/gemini-2.0-flash",          # ✅ include model in the provider string
#     api_token=os.getenv('GEMINI_API_KEY'),
#     # base_url="https://api.deepseek.com/v1"
# )
llm_cfg = LLMConfig(
    provider="deepseek/deepseek-chat",          # ✅ include model in the provider string
    api_token=os.getenv('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com"
)

# ── 4. attach the extraction strategy ────────────────────────────────────
llm_strategy = LLMExtractionStrategy(
    llm_config=llm_cfg,
    schema=RTO_Model.model_json_schema(),      
    extraction_type="schema",
    instruction=INSTRUCTION_TO_LLM,
    chunk_token_threshold=1000,
    apply_chunking=False,
    overlap_rate=0.0,
    input_format="markdown",
)

crawl_cfg = CrawlerRunConfig(
    extraction_strategy=llm_strategy,
    cache_mode=CacheMode.DISABLED,
    remove_overlay_elements=True,
    exclude_external_links=True,
    page_timeout=300000,
)

url_strategy = LLMExtractionStrategy(
    llm_config=llm_cfg,
    schema=URL_Model.model_json_schema(),      
    extraction_type="schema",
    instruction=URL_INSTRUCTION_TO_LLM,
    chunk_token_threshold=1000,
    apply_chunking=False,
    overlap_rate=0.0,
    input_format="html",
)

url_cfg = CrawlerRunConfig(
    extraction_strategy=url_strategy,
    cache_mode=CacheMode.DISABLED,
    remove_overlay_elements=True,
    exclude_external_links=True,
    page_timeout=300000,
)

browser_cfg = BrowserConfig(
    headless=False, 
    verbose=True, 
    text_mode=False,
)

async def url_scrape():
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(URLS_TO_SCRAPE[0], config=url_cfg)

        if result.success:            
            data = json.loads(result.extracted_content)
            print("✅ extracted", len(data), "items")
            for p in data[:10]: print(p)
            return data[0]
            
        else:
            print("❌ error:", result.error_message)
            print(llm_strategy.show_usage())   # token cost insight

# ── 5. Main script logic ─────────────────────────────────────────────────
async def main():
    """
    Runs the two-step process:
    1. Crawls all target URLs to aggregate their content.
    2. Sends the combined content to the LLM for final, structured extraction.
    """
    print("🎯 Starting Step 1: Crawling and Aggregating Content...")

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        results = await crawler.arun_many(URLS_TO_SCRAPE, config=crawl_cfg)
        result = results[-1]

        if result.success:          
            data = json.loads(result.extracted_content)
            data_fix = await url_scrape()
            data[0]['ABN'] = data_fix['ABN']
            data[0]['Web Address'] = data_fix['Web Address']
            print("✅ extracted", len(data), "items")
            for p in data[:10]: print(p)
            
        else:
            print("❌ error:", result.error_message)
            print(llm_strategy.show_usage())   # token cost insight


if __name__ == "__main__":
    asyncio.run(main())