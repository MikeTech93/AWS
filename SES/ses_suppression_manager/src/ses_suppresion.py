import csv
import boto3
import botocore
from fuzzywuzzy import fuzz

# create ses client
client = boto3.client('sesv2')

# function to get all email addresses on SES suppression list and include the reason
def get_suppression_list():
    """
    Description:
        Retrieves all email addresses on the SES suppression list and their associated reasons.

    Returns:
        A list of dictionaries containing email addresses, reasons, and last update times. Each dictionary has the following keys:
            - 'EmailAddress': (str) the email address on the suppression list
            - 'Reason': (str) the reason why the email address was added to the suppression list
            - 'LastUpdateTime': (str) the date and time when the suppression list entry was last updated in the format YYYY-MM-DD HH:MM:SS
            - 'MessageID': (str) the ID of the message that caused the email address to be added to the suppression list (if available)
    """
    # Set the initial pagination token to an empty string
    next_token = ""

    # Create an empty list to store all the entries
    entries = []

    # Loop through all the pages of the suppression list
    while True:
        # Fetch the next page of the suppression list
        response = client.list_suppressed_destinations(NextToken=next_token) if next_token else client.list_suppressed_destinations()

        # Extract the entries from the response and append them to the list
        entries += [{
            'EmailAddress': entry['EmailAddress'],
            'Reason': entry['Reason'],
            'LastUpdateTime': entry['LastUpdateTime'].strftime('%Y-%m-%d %H:%M:%S'),
            'MessageID': entry.get('Attributes', {}).get('MessageId')
        } for entry in response['SuppressedDestinationSummaries']]

        # Check if there are more pages
        next_token = response.get('NextToken')
        if not next_token:
            break

    # Return the list of entries
    return entries

def search_suppression_list(email_address, fuzzy_search=False):
    """
    Description:
        Search the SES suppression list for a given email address.

    Args:
        email_address (str): The email address to search for. This arg accepts wildcards (*)
        fuzzy_search (bool, optional): Whether to perform a fuzzy search if there are no exact or partial matches. Default is False.

    Returns:
        list: A list of dictionaries, see get_suppression_list() for full details.
    """
    # Get the suppression list
    suppression_list = get_suppression_list()

    # Check for exact matches
    exact_matches = [entry for entry in suppression_list if entry['EmailAddress'] == email_address]

    # If there are exact matches, return them
    if exact_matches:
        return exact_matches

    # Remove wildcards from search term
    search_term = email_address.replace('*', '')

    # Check for partial matches
    partial_matches = [entry for entry in suppression_list if search_term in entry['EmailAddress']]

    # If there are partial matches, return them
    if partial_matches:
        return partial_matches

    # If fuzzy search is disabled, return None
    if not fuzzy_search:
        return {"message": "No matches found, try enabling fuzzy search with fuzzy_search=True"}

    # Perform a fuzzy search
    fuzzy_matches = []
    for entry in suppression_list: 
        similarity = fuzz.partial_ratio(search_term, entry['EmailAddress'])
        if similarity >= 70:
            fuzzy_matches.append(entry)

    # If there are fuzzy matches, return them
    if fuzzy_matches:
        return fuzzy_matches

    # If there are no matches, return None
    return {"message": "No matches found whilst performing the fuzzy search"}

def remove_from_suppression_list(email_address):
    """
    Description:
        Removes an email address from the SES suppression list.

    Args:
        email_address (str): The email address to remove from the suppression list.

    Returns:
        dict: A dictionary containing the following keys:
            - 'RemovedEmailAddress': (str) the email address that was removed from the suppression list
            - 'Message': (str) a message indicating the status of the operation
    """

    try:
        response = client.delete_suppressed_destination(EmailAddress=email_address)
        return {
            'RemovedEmailAddress': email_address,
            'Message': response['ResponseMetadata']['HTTPStatusCode']
        }
    
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'NotFoundException':
            return {
                'RemovedEmailAddress': None,
                'Message': f'{email_address} was not found on the suppression list'
            }
        else:
            return {
                'RemovedEmailAddress': None,
                'Message': f'An unknown error occurred when trying to remove {email_address}'
            }

def remove_from_suppression_list_csv(file_path, dry_run=True):
    """
    Removes email addresses listed in a CSV file from the SES suppression list.

    Args:
        file_path (str): The file path of the CSV file. emails need to be in a column named 'email'.
        dry_run (bool): A flag indicating whether to perform a dry run (default: True).

    Returns:
        a new .csv file called results.csv to the current directory containing the results of the operation
    """

    # Retrieve all email addresses on the suppression list
    suppression_list = get_suppression_list()

    # Create a list to store the results
    results = []

    # Create a CSV reader that is case insensitive
    class CaseInsensitiveDictReader(csv.DictReader):
        def __init__(self, f, fieldnames=None, restkey=None, restval=None, dialect="excel", *args, **kwds):
            csv.DictReader.__init__(self, f, fieldnames, restkey, restval, dialect, *args, **kwds)
            self.fieldnames = [field.lower() for field in self.fieldnames]

    # Open the CSV file and iterate over its rows
    with open(file_path, newline='') as csvfile:
        reader = CaseInsensitiveDictReader(csvfile)
        for row in reader:
            email_address = row['email']

            print(f'Starting processing {email_address}')

            # Check if the email address is on the suppression list
            present_on_suppression_list = False
            suppression_reason = None 
            for entry in suppression_list:
                if email_address == entry['EmailAddress']:
                    present_on_suppression_list = True
                    suppression_reason = entry['Reason']
                    break

            # Remove the email address from the suppression list if not doing a dry run
            removed = False
            if not dry_run and present_on_suppression_list:
                result = remove_from_suppression_list(email_address)
                if result['RemovedEmailAddress']:
                    removed = True

            # Append the result to the list of results
            results.append({
                'email': email_address,
                'present on suppression list': present_on_suppression_list,
                'suppression reason': suppression_reason,
                'removed': removed
            })

    # Write the results to a new CSV file
    with open('results.csv', 'w', newline='') as csvfile:
        fieldnames = ['email', 'present on suppression list', 'suppression reason', 'removed']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    return {
        'Message': 'results.csv generated - see the current directory for the file'
    }