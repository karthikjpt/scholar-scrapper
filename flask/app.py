from flask import Flask, render_template, request, send_file, make_response, session
import csv
import io
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Define the file paths
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Define functions for filtering and processing data (as in your original code)
def process_row(row):
    row['Working days'] = int(row['Working days'])
    return row

def filter_days_24_or_more(worker):
    return int(worker['Working days']) >= 24

def filter_days_25_or_more_spinning_knitting(worker):
    return int(worker['Working days']) >= 25 and worker['Department'] in ['SPINNING', 'KNITING OPERATOR']

def scrape_google_scholar(query, page_limit=1):
    results_per_page = 10  # Google Scholar displays 10 results per page
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
    }

    all_results = []

    for page in range(0, page_limit * results_per_page, results_per_page):
        url = f"https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q={query}&start={page}"

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        results = soup.find_all('div', class_='gs_ri')

        for result in results:
            h3_element = result.find('h3', class_='gs_rt')
            link = h3_element.find('a')['href'] if h3_element and h3_element.find('a') else None
            title = h3_element.text.strip() if h3_element else None

            authors_element = result.find('div', class_='gs_a')
            authors = authors_element.text.strip() if authors_element else "Authors information not available"

            all_results.append({'Link': link, 'Title': title, 'Authors': authors})


    return all_results

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/web', methods=['GET', 'POST'])
def web():
    if request.method == 'POST':
        search_query = request.form['search_query']
        page_limit = int(request.form.get('page_limit', 1))  # Get the number of pages from the form

        scraped_data = scrape_google_scholar(search_query, page_limit=page_limit)

        # Render results.html with the search results, query, and page limit
        return render_template('results.html', results=scraped_data, query=search_query, page_limit=page_limit)

    return render_template('web.html')

@app.route('/uploadfile', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "No file part"

    file = request.files['file']
    if file.filename == '':
        return "No selected file"

    if file:
        file.save(app.config['UPLOAD_FOLDER'] + 'workers.csv')

        try:
            with open(app.config['UPLOAD_FOLDER'] + 'workers.csv', mode='r') as uploaded_file:
                reader = csv.DictReader(uploaded_file)
                data = [process_row(row) for row in reader]

            report_1 = list(filter(filter_days_24_or_more, data))
            report_2 = list(filter(filter_days_25_or_more_spinning_knitting, data))

            for worker in report_1:
                worker['Incentive'] = '1000'

            for worker in report_2:
                worker['Special Incentive'] = '500'

            combined_reports = {worker['ID']: worker for worker in report_1 + report_2}.values()
            processed_data = list(filter(lambda worker: worker.get('Incentive') == '1000', combined_reports))
            processed_data.sort(key=lambda x: int(x['ID']))

            for index, worker in enumerate(processed_data, start=1):
                worker['S.no'] = str(index)

            csv_buffer = io.BytesIO()
            csv_data = io.StringIO()
            fieldnames = ['S.no', 'ID', 'Workers', 'Department', 'Working days', 'Incentive', 'Special Incentive', 'Signature']
            writer = csv.DictWriter(csv_data, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(processed_data)
            csv_buffer.write(csv_data.getvalue().encode())
            csv_buffer.seek(0)

            return send_file(csv_buffer, as_attachment=True, download_name='incentive.csv', mimetype='text/csv')

        except Exception as e:
            return f"An error occurred: {e}"

    return "File uploaded and processed successfully"

@app.route('/upload_form')
def upload_form():
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)

