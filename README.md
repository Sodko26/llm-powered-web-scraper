🏛 RTO Big Data Web Scraper & AI-Powered Crawler

An automated data extraction pipeline designed to scrape, clean, and validate Registered Training Organisation (RTO) data from the official training.gov.au portal.
This system combines traditional scraping (Selenium, BeautifulSoup, Playwright) with LLM-powered crawling for dynamic JavaScript-heavy pages, enabling large-scale collection of structured, up-to-date educational course data.

✨ Features

Multi-source scraping: Training.gov.au → RTO websites for cross-verification

4,000+ universities & 15,000+ courses processed per execution

Automated pagination & sub-link crawling

LLM-driven content parsing with:

Gemini 2.5 Flash – optimized for cost-efficient extraction (<90,000 tokens/op)

DeepSeek R1 – for natural language keyword validation & course confirmation

Hybrid HTML/Markdown/JSON parsing to bypass JavaScript rendering issues

CSV + JSON export for easy backend ingestion

Data cleaning pipeline using pandas for normalization

Headless browser support for speed & scalability

🛠 Technologies Used

Scraping & Automation

Python 3.11+

Selenium – DOM scraping & interaction

BeautifulSoup4 – HTML parsing

Playwright – JavaScript-rendered content scraping

Crawl4AI – AI-guided multi-layer crawling & field targeting

AI Models

Gemini 2.5 Flash – Structured data extraction from complex layouts

Deepseek-R1 – Keyword/semantic verification of course listings

Data Processing & Output

pandas – Cleaning, structuring, and exporting

CSV – Final cleaned datasets for backend import

JSON – Structured export for API pipelines

📂 Project Workflow

Load Input List
A CSV containing RTO Code and Web Address.

Phase 1: Government Data Scrape

Visit training.gov.au detail pages for each code:

/summary
/contacts
/addresses
/qualifications


Extract structured RTO info (legal name, ABN, status, courses, etc.).

Phase 2: AI-Powered Web Verification

Visit each RTO’s official website.

Search for each course code/title using LLM-powered crawling.

Flag discrepancies between government and official site.

Phase 3: Data Cleaning & Structuring

Normalize addresses, phone formats, date fields.

Deduplicate qualification lists.

Standardize naming conventions.

Output

Final CSV (matching training.gov.au schema)

Summary Report: broken links, course mismatches, data gaps.

🚀 Getting Started
# 1. Clone the repository
git clone https://github.com/your-username/rto-big-data-scraper.git
cd rto-big-data-scraper

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Place your input CSV in /data/input.csv

# 5. Run the scraper
python scrape_rtos.py --input data/input.csv --output data/final_rtos.csv

📊 Example Output
Code	Legal Name	Business Name	Status	ABN	Web Address	Qualification 1	Qualification 2	...
0049	Australian Institute of Management	AIM VET	Current	40009668553	http://aim.com.au	Diploma of Leadership	Certificate IV in Business	...