import requests
from bs4 import BeautifulSoup
import csv

# Define the search query and parameters
search_query = 'IBM'
page_limit = 3  # Number of pages to scrape
results_per_page = 10  # Google Scholar displays 10 results per page

# Define headers to mimic a web browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
}

# Open a CSV file to write the results
with open('google_scholar_results.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    # Write headers to the CSV file
    writer.writerow(['Link', 'Title', 'Authors'])

    # Loop through the specified number of pages
    for page in range(0, page_limit * results_per_page, results_per_page):
        # Construct the URL for the current page
        url = f"https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q={search_query}&start={page}"
        
        # Send a GET request to the URL
        response = requests.get(url, headers=headers)
        
        # Parse the content of the response using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all search result elements
        results = soup.find_all('div', class_='gs_ri')

        # Loop through each search result element
        for result in results:
            # Extract the link, title, and authors from the search result
            link = result.find('h3', class_='gs_rt').find('a')['href'] if result.find('h3', class_='gs_rt') else None
            title = result.find('h3', class_='gs_rt').text.strip() if result.find('h3', class_='gs_rt') else None
            authors = result.find('div', class_='gs_a').text.strip() if result.find('div', class_='gs_a') else None
            
            # Write the extracted data to the CSV file
            writer.writerow([link, title, authors])

