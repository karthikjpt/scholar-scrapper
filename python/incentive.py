import csv

# File paths
input_file_path = '/home/karthik/Desktop/STC/python/workers.csv'
output_file_path = '/home/karthik/Desktop/STC/python/incentive.csv'

# Define functions for filtering and processing data
def process_row(row):
    # Convert 'Working days' to integer
    row['Working days'] = int(row['Working days'])
    return row

def filter_days_24_or_more(worker):
    # Filter workers with 24 or more working days
    return int(worker['Working days']) >= 24

def filter_days_25_or_more_spinning_knitting(worker):
    # Filter workers with 25 or more working days in departments 'SPINNING' or 'KNITING OPERATOR'
    return int(worker['Working days']) >= 25 and worker['Department'] in ['SPINNING', 'KNITING OPERATOR']

try:
    # Read input CSV file and process the data
    with open(input_file_path, mode='r') as file:
        reader = csv.DictReader(file)
        data = [process_row(row) for row in reader]

    # Filter data for reports
    report_1 = list(filter(filter_days_24_or_more, data))
    report_2 = list(filter(filter_days_25_or_more_spinning_knitting, data))

    # Apply incentives
    for worker in report_1:
        worker['Incentive'] = '1000'

    for worker in report_2:
        worker['Special Incentive'] = '500'

    # Combine reports and remove duplicates using ID as a key
    combined_reports = {worker['ID']: worker for worker in report_1 + report_2}.values()
    processed_data = list(filter(lambda worker: worker.get('Incentive') == '1000', combined_reports))

    # Sort data based on 'ID' column in ascending order
    processed_data.sort(key=lambda x: int(x['ID']))

    # Update 'S.no' with new sequential numbers
    for index, worker in enumerate(processed_data, start=1):
        worker['S.no'] = str(index)

    # Write processed data to a new CSV file with reordered 'S.no'
    with open(output_file_path, mode='w', newline='') as file:
        fieldnames = ['S.no', 'ID', 'Workers', 'Department', 'Working days', 'Incentive', 'Special Incentive', 'Signature']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(processed_data)

    print(f"Processed data has been written to {output_file_path}")

except FileNotFoundError:
    print("File not found. Please check the file paths.")
except Exception as e:
    print(f"An error occurred: {e}")

