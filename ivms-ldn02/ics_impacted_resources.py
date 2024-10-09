import json, requests, re, csv, os, configparser, shutil, pandas as pd
from slack_sdk.web import WebClient
from slack_sdk.errors import SlackApiError
from datetime import datetime, timedelta
requests.packages.urllib3.disable_warnings() # verify=False throws warnings otherwise

def read_configs(filename, header, value):
    config = configparser.ConfigParser()
    config.read(filename)

    # Access the API key
    value = config[header][value]
    return value

def generate_scorecard_report_section_to_csv(pack_id, pack, badge_owner):
    file_name = f"{pack}_{badge_owner.upper()}_Scorecard"
    custom_pack_id = str(pack_id)
    data = {
          "resource_scope": {
            "scope_type": "divvyorganizationservice",
            "resource_group_filters": {
              "azure_resource_group_ids": [],
              "custom_resource_group_ids": []
            },
              "organization_service_filters":{
                  "organization_service_ids": [],
                  "badges": [["owner", f"{badge_owner}"]]
              }
          },
          "insight_filters": {
            "severity": [], # 1 = Info, 2 = Low, 3 = Medium, 4 = High, 5 = Critical
            "insight_ids": [],
            "resource_types": []
          }
        }
    headers = {
        'Content-Type': 'application/json;charset=UTF-8',
        'Accept': 'application/json',
        'Api-Key': api_key
    }
    response = requests.post(
        url=base_url + f'/v2/compliance/score-card/export-data?pack_ids=custom:{custom_pack_id}',
        data=json.dumps(data),
        verify=False,
        headers=headers
    )
    # print(json.dumps(response.json(), indent=4))  # Debug
    # input("Press enter")
    data = response.json()
    scorecard_section = data.get("scorecard", {}).get("section", {})
    # print(scorecard_section)
    data_directory = data_path
    output_csv_file_path = os.path.join(data_directory, f'{file_name}.csv')

    # Create the data directory if it does not exist
    os.makedirs(data_directory, exist_ok=True)

    # Open the CSV file for writing
    with open(output_csv_file_path, mode='w', newline='') as csv_file:
        # Define the fieldnames (headers)
        fieldnames = ['Standard', 'Severity', 'Project', 'Compliance','Pack Name','Owner']
        # Create a DictWriter object
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        # Write the headers
        csv_writer.writeheader()

        # Iterate over the items in scorecard_section
        for standard, values in scorecard_section.items():
            severity = values.get('severity', 'N/A')
            for project, compliance in values.items():
                try:
                    compliance_conversion = compliance.replace("%", "")
                    compliance_conversion = float(compliance_conversion)/100
                except:
                    compliance_conversion = None
                if project != 'severity':  # Skip the severity key
                    csv_writer.writerow({
                        'Standard': standard,
                        'Severity': severity,
                        'Project': project,
                        'Compliance': compliance_conversion,
                        'Pack Name' : pack,
                        'Owner' : badge_owner.upper()
                    })
    print(f"<generate_scorecard_report_section_to_csv> {file_name} saved as a csv in {data_directory}")

def generate_impacted_resources_report_to_csv(pack_id, pack, badge_owner):
    file_name = f"{pack}_{badge_owner.upper()}_Impacted"
    custom_pack_id = str(pack_id)
    data = {
          "resource_scope": {
            "scope_type": "divvyorganizationservice",
            "resource_group_filters": {
              "azure_resource_group_ids": [],
              "custom_resource_group_ids": []
            },
              "organization_service_filters":{
                  "organization_service_ids": [],
                  "badges": [["owner", f"{badge_owner}"]]
              }
          },
          "insight_filters": {
            "severity": [], # 1 = Info, 2 = Low, 3 = Medium, 4 = High, 5 = Critical
            "insight_ids": [],
            "resource_types": []
          }
        }
    headers = {
        'Content-Type': 'application/json;charset=UTF-8',
        'Accept': 'application/json',
        'Api-Key': api_key
    }
    response = requests.post(
        url=base_url + f'/v2/compliance/score-card/export-data?pack_ids=custom:{custom_pack_id}',
        data=json.dumps(data),
        verify=False,
        headers=headers
    )
    # print(json.dumps(response.json(), indent=4))  # Debug
    data = response.json()
    # scorecard_section = data.get("scorecard", {}).get("section", {})
    impacted_resources = data.get("impacted_resources", {})

    data_directory = data_path
    output_csv_file_path = os.path.join(data_directory, f'{file_name}.csv')

    # Create the data directory if it does not exist
    os.makedirs(data_directory, exist_ok=True)

    # Open the CSV file for writing
    with open(output_csv_file_path, mode='w', newline='') as csv_file:
        # Define the fieldnames (headers)
        fieldnames = ['Account Cluster Name', 'Account Cluster ID', 'Namespace Name', 'Resource Type','Name', 'Insight', 'Provider ID', 'Provider UUID', 'Severity', 'Direct Link','Pack Name', 'Owner']
        # Create a DictWriter object
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        # Write the headers
        csv_writer.writeheader()

        for key, resources in impacted_resources.items():
            for resource in resources:
                account_cluster_name = resource.get('account_cluster_name')
                account_cluster_id = resource.get('account_cluster_id')
                namespace_name = resource.get('namespace_name')
                resource_type = resource.get('resource_type')
                name = resource.get('name')
                insight = resource.get('insight')
                provider_id = resource.get('provider_id')
                provider_uuid = resource.get('provider_uuid')
                severity = resource.get('severity')
                direct_link = resource.get('direct_link')
                csv_writer.writerow({
                    'Account Cluster Name':account_cluster_id,
                    'Account Cluster ID': account_cluster_id,
                    'Namespace Name': namespace_name,
                    'Resource Type': resource_type,
                    'Name': name,
                    'Insight': insight,
                    'Provider ID': provider_id,
                    'Provider UUID': provider_uuid,
                    'Severity': severity,
                    'Direct Link': direct_link,
                    'Pack Name': pack,
                    'Owner': badge_owner.upper()
                })

    print(f"<generate_impacted_resources_report_to_csv> {file_name} saved as a csv in {data_directory}")

def list_insights():
    data = {}
    headers = {
        'Content-Type': 'application/json;charset=UTF-8',
        'Accept': 'application/json',
        'Api-Key': api_key
    }
    response = requests.get(
        url=base_url + '/v2/public/insights/list',
        data=json.dumps(data),
        verify=False,
        headers=headers
    )
    json_data = response.json()
    # Open the CSV file for writing
    data_directory = data_path
    output_csv_file_path = os.path.join(data_directory, f'insights.csv')
    with open(output_csv_file_path, mode='w', newline='', encoding='utf-8') as csv_file:
        # Define the fieldnames (headers)
        fieldnames = ['Insight ID', 'Name', 'Description', 'Severity', 'Custom Severity', 'Meta Data', 'Supported Clouds', 'Notes']
        # Create a DictWriter object
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        # Write the headers
        csv_writer.writeheader()
        for item in json_data:
            insight_id = item.get("insight_id")
            name = item.get("name")
            description = item.get("description")
            severity = item.get("severity")
            custom_severity = item.get("custom_severity")
            meta_data = item.get("meta_data")
            supported_clouds = item.get("supported_clouds")
            notes = item.get("notes")
            csv_writer.writerow({
                'Insight ID': insight_id,
                'Name': name,
                'Description': description,
                'Severity': severity,
                'Custom Severity': custom_severity,
                'Meta Data': meta_data,
                'Supported Clouds': supported_clouds,
                'Notes': notes
            })

    print(f"<list_insights> Data successfully written to {output_csv_file_path}")
    return output_csv_file_path

def enrich_findings(packs_file, insights_file):
    file_a = packs_file
    file_b = insights_file
    file_a_updated = enrich_update_path

    # Read CSV B into a dictionary
    b_data = {}
    with open(file_b, mode='r', newline='', encoding='utf-8') as file_b:
        reader = csv.DictReader(file_b)
        for row in reader:
            b_data[row['Name']] = row['Notes']

    # Read CSV A and append notes from B
    a_data = []
    with open(file_a, mode='r', newline='', encoding='utf-8') as file_a:
        reader = csv.DictReader(file_a)
        fieldnames = reader.fieldnames + ['Notes']  # Add a new field for notes
        for row in reader:
            standard_value = row['Insight']
            row['Notes'] = b_data.get(standard_value, '')  # Get notes from B or empty if no match
            a_data.append(row)

    # Write the updated data back to a new CSV file
    with open(file_a_updated, mode='w', newline='', encoding='utf-8') as file_out:
        writer = csv.DictWriter(file_out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(a_data)

    print(f"<enrich_findings> The updated CSV file has been written as '{file_a_updated}'.")


def merge_csv_files(data_directory, output_csv_file,endswith, startswith):
    # List all CSV files in the directory
    csv_files = [f for f in os.listdir(data_directory) if f.endswith(endswith) and f.startswith(startswith)]

    # Open the output CSV file for writing
    with open(output_csv_file, mode='w', newline='') as output_file:
        csv_writer = csv.writer(output_file)

        # Variable to track if the header has been written
        header_written = False

        for csv_file in csv_files:
            print(csv_file)
            csv_path = os.path.join(data_directory, csv_file)

            # Open each input CSV file for reading
            with open(csv_path, mode='r', newline='') as input_file:
                csv_reader = csv.reader(input_file)

                # Get the header from the first file and write it to the output file
                header = next(csv_reader)
                if not header_written:
                    csv_writer.writerow(header)
                    header_written = True

                # Write the rest of the rows from each input file to the output file
                for row in csv_reader:
                    csv_writer.writerow(row)
    print(f"<merge_csv_files> {output_csv_file} was created.")

def scorecard_and_impacted(owner):
    # Will get the score percentages
    for o in owner:
        generate_scorecard_report_section_to_csv("11","InfoSec GKE Pack - Mandatory", o)
        generate_scorecard_report_section_to_csv("10","InfoSec GKE Pack - Recommended", o)
        generate_scorecard_report_section_to_csv("7","InfoSec GCP Pack - Mandatory", o)
        generate_scorecard_report_section_to_csv("8","InfoSec GCP Pack - Recommended", o)
    data_directory = data_path
    output_csv_file = f'{data_path}/ICS_scorecards_merged.csv'
    merge_csv_files(data_directory, output_csv_file, '_Scorecard.csv','InfoSec')
    # Will get the findings
    for o in owner:
        generate_impacted_resources_report_to_csv("11","InfoSec GKE Pack - Mandatory", o)
        generate_impacted_resources_report_to_csv("10","InfoSec GKE Pack - Recommended", o)
        generate_impacted_resources_report_to_csv("7","InfoSec GCP Pack - Mandatory", o)
        generate_impacted_resources_report_to_csv("8","InfoSec GCP Pack - Recommended", o)
    output_csv_file = f'{data_path}/ICS_impacted_merged.csv'
    merge_csv_files(data_directory, output_csv_file, '_Impacted.csv','InfoSec')
    return output_csv_file

def find_latest_timestamped_folder(directory):
    # Regular expression to match timestamp in folder names (YYYY_MM_DD_HH_MM)
    timestamp_pattern = r"(\d{4}_\d{2}_\d{2}_\d{2}_\d{2})"

    latest_folder = None
    latest_timestamp = None

    # Iterate through the directory to find folders with a timestamp
    for foldername in os.listdir(directory):
        folder_path = os.path.join(directory, foldername)

        # Check if it's a directory and contains a timestamp
        if os.path.isdir(folder_path):
            match = re.search(timestamp_pattern, foldername)
            if match:
                # Parse the timestamp into a datetime object
                timestamp_str = match.group(1)
                timestamp = datetime.strptime(timestamp_str, "%Y_%m_%d_%H_%M")

                # Compare with the latest timestamp
                if latest_timestamp is None or timestamp > latest_timestamp:
                    latest_timestamp = timestamp
                    latest_folder = folder_path

    return latest_folder



def move_files_to_timestamped_dir_can_copy(directory, exclude_files, copy_files):
    """
    Moves files to a timestamped directory, while copying specific files.

    Args:
    - directory (str): The path to the directory containing the files.
    - exclude_files (list): List of filenames to exclude from moving or copying.
    - copy_files (list): List of filenames to copy instead of moving.

    Example usage:
    - exclude_files = ['ignore_this_file.csv']
    - copy_files = ['important_report.csv', 'another_file.txt']
    - move_files_to_timestamped_dir('/path/to/your/directory', exclude_files, copy_files)
    """

    # Get the current timestamp and format it as YYYY_MM_DD_HH_MM
    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M")

    # Create a new directory based on the timestamp
    timestamped_dir = os.path.join(directory, timestamp)
    os.makedirs(timestamped_dir, exist_ok=True)

    # Iterate over all files in the directory
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        # Check if it's a file and not in the exclude list
        if os.path.isfile(file_path) and filename not in exclude_files:
            destination_path = os.path.join(timestamped_dir, filename)

            # Copy files that are in the copy_files list
            if filename in copy_files:
                shutil.copy2(file_path, destination_path)
                print(f"<move_files_to_timestamped_dir> Copied '{filename}' to '{timestamped_dir}'")
            else:
                # Move files that are not in the copy_files list
                shutil.move(file_path, destination_path)
                print(f"<move_files_to_timestamped_dir> Moved '{filename}' to '{timestamped_dir}'")

    print(f"<move_files_to_timestamped_dir> All files moved/copied to {timestamped_dir} except {exclude_files}.")



def find_latest_timestamped_folder(directory):
    # Regular expression to match timestamp in folder names (YYYY_MM_DD_HH_MM)
    timestamp_pattern = r"(\d{4}_\d{2}_\d{2}_\d{2}_\d{2})"

    latest_folder = None
    latest_timestamp = None

    # Iterate through the directory to find folders with a timestamp
    for foldername in os.listdir(directory):
        folder_path = os.path.join(directory, foldername)

        # Check if it's a directory and contains a timestamp
        if os.path.isdir(folder_path):
            match = re.search(timestamp_pattern, foldername)
            if match:
                # Parse the timestamp into a datetime object
                timestamp_str = match.group(1)
                timestamp = datetime.strptime(timestamp_str, "%Y_%m_%d_%H_%M")

                # Compare with the latest timestamp
                if latest_timestamp is None or timestamp > latest_timestamp:
                    latest_timestamp = timestamp
                    latest_folder = folder_path

    return latest_folder


def find_file_in_folder(folder_path, search_term="previous"):
    # Iterate over files in the folder to search for the specified term in the name
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        # Check if it's a file and if the filename contains the search term
        if os.path.isfile(file_path) and search_term in filename:
            print(f"<find_file_in_folder> Found file: {filename}")
            return file_path

    print(f"<find_file_in_folder> No file containing '{search_term}' found in {folder_path}")
    return None


def find_latest_folder_and_search_file(directory, search_term="previous"):
    # Example usage
    # latest_file = find_latest_folder_and_search_file('/path/to/your/directory', 'previous')
    # Find the latest timestamped folder
    latest_folder = find_latest_timestamped_folder(directory)

    if latest_folder:
        print(f"<find_latest_folder_and_search_file> Latest folder found: {latest_folder}")
        # Search for the file within the latest folder
        return find_file_in_folder(latest_folder, search_term)
    else:
        print(f"<find_latest_folder_and_search_file> No timestamped folder found in {directory}")
        return None


def find_all_timestamped_folders(directory):
    # Regular expression to match timestamp in folder names (YYYY_MM_DD_HH_MM)
    timestamp_pattern = r"(\d{4}_\d{2}_\d{2}_\d{2}_\d{2})"

    timestamped_folders = []

    # Iterate through the directory to find folders with a timestamp
    for foldername in os.listdir(directory):
        folder_path = os.path.join(directory, foldername)

        # Check if it's a directory and contains a timestamp
        if os.path.isdir(folder_path):
            match = re.search(timestamp_pattern, foldername)
            if match:
                # Parse the timestamp into a datetime object
                timestamp_str = match.group(1)
                timestamp = datetime.strptime(timestamp_str, "%Y_%m_%d_%H_%M")
                timestamped_folders.append((timestamp, foldername, folder_path))

    return timestamped_folders


def keep_latest_n_folders(directory, n):
    # Example usage
    # keep_latest_n_folders('/path/to/your/directory', 3)
    # Find all timestamped folders
    timestamped_folders = find_all_timestamped_folders(directory)

    # Sort folders by timestamp in descending order
    timestamped_folders.sort(reverse=True, key=lambda x: x[0])  # Sort by timestamp

    # Keep the latest n folders
    folders_to_keep = timestamped_folders[:n]
    folders_to_remove = timestamped_folders[n:]  # The rest will be removed

    # Print folders to keep
    print(f"<keep_latest_n_folders> Keeping the latest {n} folders:")
    for _, foldername, folder_path in folders_to_keep:
        print(f" - {foldername}")

    # Remove the folders that are not in the 'keep' list
    for _, foldername, folder_path in folders_to_remove:
        # Recursively delete the folder and its contents
        shutil.rmtree(folder_path)
        print(f"<keep_latest_n_folders> Removed: {foldername}")

def send_slack_message(channel, message):
    # pip install slack-sdk
    token = slack_token
    client = WebClient(token)
    try:
        response = client.chat_postMessage(
            channel=channel,
            text=message
        )
        print("<send_slack_message> Message sent successfully: ", response["ts"])
        return channel, response["ts"]  # Return channel ID and timestamp as a tuple
    except SlackApiError as e:
        print(f"Error posting message: {e}")
        return None, None  # Return None if there was an error

def compare_and_mark_findings(recent_csv, previous_csv,concat_max, output_csv):
    # This will compare two csv using a concat function, the contact max is the number of columns to concat.
    # compare_and_mark_findings('recent.csv', 'previous.csv', 12, 'comparison_result.csv')
    # Read the CSVs
    recent_df = pd.read_csv(recent_csv)
    previous_df = pd.read_csv(previous_csv)

    # Concatenate columns 1 to 12 to create a comparison key
    recent_df['key'] = recent_df.iloc[:, 0:concat_max].astype(str).agg(''.join, axis=1)
    previous_df['key'] = previous_df.iloc[:, 0:concat_max].astype(str).agg(''.join, axis=1)

    # Initialize "Finding Status" column with default "Existing" status
    recent_df['Finding Status'] = 'Existing'

    # Mark "New" findings (in recent but not in previous)
    recent_only = ~recent_df['key'].isin(previous_df['key'])
    recent_df.loc[recent_only, 'Finding Status'] = 'New'

    # Mark "Remediated" findings (in previous but not in recent)
    previous_only = ~previous_df['key'].isin(recent_df['key'])
    remediated = previous_df.loc[previous_only].copy()
    remediated['Finding Status'] = 'Remediated'

    # Combine both recent and remediated findings
    result = pd.concat([recent_df, remediated], ignore_index=True)

    # Drop the 'key' column as it's no longer needed
    result = result.drop(columns=['key'])

    # Write the result to a new CSV file
    result.to_csv(output_csv, index=False)
    print(f'<compare_and_mark_findings> Compared results output {output_csv}')
    return output_csv

def filter_dedup_and_append_remediated(input_csv, column, value, output_csv=None):
    """
    Filters rows from input_csv based on the specified column and value, deduplicates,
    and appends new unique rows to output_csv, skipping duplicates.

    Args:
    - input_csv (str): Path to the input CSV file.
    - column (str): The column to filter on.
    - value (str): The value to filter for.
    - output_csv (str, optional): Path to the output CSV file. Defaults to 'remediated_historical.csv'.

    Example usage:
    - filter_dedup_and_append_remediated('comparison_result.csv', 'Finding Status', 'Remediated')
    """

    # Determine the directory of the input file
    input_dir = os.path.dirname(os.path.abspath(input_csv))

    # Set output file in the same directory as the input if not provided
    if output_csv is None:
        output_csv = os.path.join(input_dir, 'remediated_historical.csv')

    # Read the input CSV
    df = pd.read_csv(input_csv)

    # Filter rows where the specified column has the specified value (e.g., 'Finding Status' is 'Remediated')
    remediated_df = df[df[column] == value].copy()

    # Add a 'Date Added' column with the current date (without time)
    remediated_df['Date Added'] = datetime.now().strftime('%Y-%m-%d')

    # Check if the output file exists
    if os.path.exists(output_csv):
        # Read the existing file to keep previous data
        existing_df = pd.read_csv(output_csv)

        # Deduplicate based on all columns except 'Date Added'
        common_columns = [col for col in remediated_df.columns if col != 'Date Added']

        # Identify new entries that are not already in the existing output file
        new_entries = pd.merge(remediated_df, existing_df, on=common_columns, how='left', indicator=True)
        new_entries = new_entries[new_entries['_merge'] == 'left_only'].drop(columns=['_merge'])

        # Append new entries to the existing output file
        if not new_entries.empty:
            new_entries.to_csv(output_csv, mode='a', header=False, index=False)
            print(f"Appended {len(new_entries)} new rows to {output_csv}.")
        else:
            print("No new entries to append. All rows already exist in the output file.")
    else:
        # If no output file exists, save the new data directly to the output CSV
        remediated_df.to_csv(output_csv, index=False)
        print(f"Created {output_csv} and added {len(remediated_df)} rows.")

    return output_csv


def null_column_for_value(csv_file_path, column_for_value, what_value, column_to_null):
    # Will look in a csv for a specific value and null out another value from a column
    # null_column_for_value(r"C:\py\infosec-scripts\scripts\data\ICS\ICS_remediation_historical - Copy.csv", 'Finding Status', 'Remediated', 'Notes')
    # Load the CSV into a DataFrame
    df = pd.read_csv(csv_file_path)

    # Set "Notes" to None where "Finding Status" equals "remediated"
    df.loc[df['Finding Status'] == 'Remediated', 'Notes'] = None

    # Overwrite the original file with the updated DataFrame
    df.to_csv(csv_file_path, index=False)
    print(f'<null_column_for_value> {csv_file_path} column {column_to_null} was Nulled out')

    return df

def filter_recent_entries(csv_file_path, column, days):
    #This will review a csvfile in a specific column and only keep then entiries for the specified time
    # filter_recent_entries(r"C:\py\infosec-scripts\scripts\data\ICS\ICS_remediation_historical - Copy.csv", 'Date Added', 45)
    # Load the CSV into a DataFrame
    df = pd.read_csv(csv_file_path)

    # Convert the 'Date Added' column to datetime
    df[column] = pd.to_datetime(df[column])

    # Get today's date
    today = datetime.today()

    # Calculate the date 45 days ago
    cutoff_date = today - timedelta(days=days)

    # Get the original number of rows
    original_row_count = len(df)

    # Filter the rows where 'Date Added' is within the last 45 days
    filtered_df = df[df['Date Added'] >= cutoff_date]

    # Get the number of rows removed
    rows_removed = original_row_count - len(filtered_df)

    # Overwrite the original CSV file with the filtered data
    filtered_df.to_csv(csv_file_path, index=False)

    # Print the number of rows removed
    print(f"<filter_recent_entries> Number of rows removed: {rows_removed}")

    return filtered_df

def combine_and_dedup(csv_file_path1, csv_file_path2, output_file_path):
    # combine_and_dedup('file1.csv', 'file2.csv', 'output.csv')
    # Load both CSV files into DataFrames
    df1 = pd.read_csv(csv_file_path1)
    df2 = pd.read_csv(csv_file_path2)

    # Combine the two DataFrames
    combined_df = pd.concat([df1, df2])

    # Remove duplicates
    deduped_df = combined_df.drop_duplicates()

    # Save the deduplicated DataFrame to the specified output file
    deduped_df.to_csv(output_file_path, index=False)

    return deduped_df

def sendto_google_cloud2(filename, bucket_name, blob_name):
    from google.cloud import storage
    storage_client = storage.Client.from_service_account_json(google_path)
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(filename)
    print(f"<sendto_google_cloud2> {blob_name} data uploaded to google")



###--- MAIN SECTION ---###
# Configurable Variables
owner = ["MS","CS","TPC","sfc","SEEDs"]
excluding_move = []
copy_files = ['ICS_remediation_historical.csv']
slack_channel = 'cs_test'
script_running_location = 'London Scan Engine'
days_to_keep_in_historical = 45

#Static Variables
data_path = 'data/ICS'
slack_token = read_configs('../config.ini', 'Slack', 'SLACK_API_KEY')
api_key = read_configs('../config.ini', 'Rapid7', 'ICS_KEY')
base_url = read_configs('../config.ini', 'Rapid7', 'ICS_BASE_URL')
enrich_update_path = f'{data_path}/ICS_impacted_complete_pre_compare.csv' # Do not change filename
bucket_name = "infosec_dashboard_v3"
google_path = "../gc.json"
send_to_google = f'{data_path}/ICS_impacted_complete.csv'


try:
    channel_id, response_ts = send_slack_message(slack_channel, f'`<ICS Dashboard Data>` Running ICS dashboard information ({script_running_location})')
    print(f'Pulling data from owner {owner}')
    enrich_input_a = scorecard_and_impacted(owner)
    print('Pulling insights to add fix to findings')
    enrich_input_b = list_insights()
except Exception as e:
    print(f"An error occurred: {str(e)}")
    send_slack_message(slack_channel, '`<ICS Dashboard Data>` There was an issue with pulling from ICS')
try:
    print('Adding fix to findings')
    enrich_findings(enrich_input_a, enrich_input_b)
    print('Finding previous report from dated folders')
    latest_previous = find_latest_folder_and_search_file(data_path, search_term="ICS_impacted_complete")
    print('Comparing from previous findings and added finding status column')
    cleanup_notes_impacted = compare_and_mark_findings(enrich_update_path,latest_previous, 12, output_csv=f'{data_path}/ICS_impacted_complete_pre_combined.csv')
    print('Nulling notes on remediated findings on current report')
    null_column_for_value(cleanup_notes_impacted, 'Finding Status', 'Remediated', 'Notes')
    print('Creating historical remediation file')
    cleanup_notes_historical = filter_dedup_and_append_remediated(cleanup_notes_impacted, 'Finding Status', 'Remediated', f'{data_path}/ICS_remediation_historical.csv')
    print('Nulling notes on remediated findings on historical report')
    null_column_for_value(cleanup_notes_historical, 'Finding Status', 'Remediated', 'Notes')
    print(f'Removing entries in historical older than {str(days_to_keep_in_historical)} days')
    filter_recent_entries(cleanup_notes_historical, 'Date Added',days_to_keep_in_historical)
    print(f'Combining and deduping on {cleanup_notes_impacted}, {cleanup_notes_historical}')
    combine_and_dedup(cleanup_notes_historical, cleanup_notes_impacted,f'{data_path}/ICS_impacted_complete.csv')
except Exception as e:
    print(f"An error occurred: {str(e)}")
    send_slack_message(slack_channel, '`<ICS Dashboard Data>` There was an issue comparing, deduping, combining, or enriching')
try:
    sendto_google_cloud2(send_to_google, bucket_name, "ICS_impacted_complete.csv")
    print('Moving files for archiving')
    move_files_to_timestamped_dir_can_copy(data_path, excluding_move, copy_files)
    previous_report = find_latest_folder_and_search_file(data_path,'ICS_impacted_complete')  # This will be for comparing latest previous to current
    keep_latest_n_folders(data_path, 6)  # This is to keep the latest 6 timestamped file names
    send_slack_message(slack_channel, '`<ICS Dashboard Data>` ICS report uploaded to google')
except Exception as e:
    print(f"An error occurred: {str(e)}")
    send_slack_message(slack_channel,'`<ICS Dashboard Data>` There was on ICS dashboard data generation')
