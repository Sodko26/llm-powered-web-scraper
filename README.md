# 🏛 RTO Big Data Web Scraper & AI-Powered Crawler

An **automated data extraction pipeline** that scrapes, cleans, and validates **Registered Training Organisation (RTO)** data from [training.gov.au](https://training.gov.au).  

This project combines **traditional scraping** (Selenium, BeautifulSoup, Playwright) with **LLM-powered crawling** for **JavaScript-heavy content**, enabling large-scale, up-to-date, and structured educational course datasets.

---

## ✨ Features

- 📊 **Processes 4,000+ RTOs** and **15,000+ courses** in one execution  
- 🔄 **Automated pagination & deep crawling** from gov pages to official RTO sites  
- 🤖 **LLM-assisted data extraction** with:
  - **Gemini 2.5 Flash** – cost-efficient (<90k tokens/op)
  - **DeepSeek R1** – semantic verification & keyword matching  
- 🖥 **Hybrid HTML/Markdown/JSON parsing** for dynamic content
- 🗂 **CSV & JSON output** for backend/API pipelines
- 🧹 **Data cleaning & normalization** with pandas
- ⚡ Headless browser mode for faster execution

---

## 🛠 Technologies Used

### Scraping & Automation

- **Python 3.11+**
- **Selenium** – DOM scraping & interactions
- **BeautifulSoup4** – HTML parsing
- **Playwright** – JavaScript-rendered content scraping
- **Crawl4AI** – AI-guided crawling & sub-URL targeting

### AI Models

- **Gemini 2.5 Flash** – Structured extraction from complex layouts
- **DeepSeek-R1** – Course existence & metadata verification

### Data Processing & Export

- **pandas** – Data cleaning & transformation
- **CSV** – Government schema-compatible export
- **JSON** – API-ready format

---

## 📂 Workflow

1. **Load Input CSV**  
   - Columns: `Code`, `Web Address`
   
2. **Phase 1 – Government Scraping**  
   For each code, scrape:
   - `/summary` – Organisation details
   - `/contacts` – Contact info
   - `/addresses` – Physical/postal addresses
   - `/qualifications` – Offered qualifications  

3. **Phase 2 – AI Verification**  
   - Visit each RTO’s official website  
   - Search for each course using **LLM keyword prompts**  
   - Flag discrepancies & missing courses

4. **Phase 3 – Cleaning & Structuring**  
   - Normalize dates, addresses, contact info  
   - Remove duplicates  
   - Match to CSV schema

5. **Output**  
   - Final **CSV**
   - Summary report of broken links & mismatches

---

## 🔧 Getting Started

```bash
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

