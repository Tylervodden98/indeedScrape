import csv
from bs4 import BeautifulSoup
import cloudscraper
import datetime


def get_url(position,location):
    url_template = "https://ca.indeed.com/jobs?q={}&l={}&fromage=14"
    url = url_template.format(position,location)
    return url


url_template = "https://ca.indeed.com/jobs"
#get raw HTML
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
           "Referer": "https://ca.indeed.com",
           "Connection": "keep-alive",
           "Accept-Language": "en-US,en;q=0.9,lt;q=0.8,et;q=0.7,de;q=0.6"}


#Finding the Job Title
def get_record(card):
    print(card)
    title = card.select("h2 a span")
    print(title)
    job_title = title[0].get('title')
    print(job_title)
    # Getting URL For Job
    url_job = 'https://ca.indeed.com' + card.select("h2 a")[0].get('href')
    print(url_job)
    # Find Company Names
    company_name = card.find("span", "companyName").text.strip()
    print(company_name)
    # Find Company Location
    company_location = card.find("div", "companyLocation").text
    print(company_location)
    # Find Job Summary Snippet
    try:
        job_summary = card.find("div", "job-snippet").li.text.strip()
    except AttributeError:
        job_summary = ""
    print(job_summary)
    # Find posted date
    post_date = card.find("span", "date").text.strip()
    print(post_date)
    # Get Todays date to compare
    today_date = datetime.date.today().strftime("%Y-%m-%d")
    print(today_date)
    # For salary
    try:
        salary_job = card.find("div svg").get('aria-label')
    except AttributeError:
        salary_job = ""
    print(salary_job)

    record = (job_title, company_name, company_location, post_date, today_date, job_summary, salary_job, url_job)
    return record


#Getting next pages
def fetch_data(position, location):
    records = []
    url = get_url(position=position, location=location)
    while True:
        # use scraper to bypass indeed checks
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        cards = soup.find_all('div', 'job_seen_beacon')

        for card in cards:
            record = get_record(card)
            records.append(record)

        print(records)

        try:
            url = 'https://ca.indeed.com' + soup.find('a',{'aria-label':'Next Page'}).get('href')
        except AttributeError:
            break

    return records


queries = ["Python Developer", "Android Developer", "Java Developer", "Software Developer", "Software Intern", "IT Intern"
    , "Mobile Developer", "Software Engineer"]

for query in queries:
    records = fetch_data(query, 'Toronto, ON')
    with open(f'results_{query.replace(" ", "_")}.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Job Title', 'Company', 'Location', 'PostDate', 'ExtractDate', 'Summary', 'Salary', 'JobUrl'])
        writer.writerows(records)