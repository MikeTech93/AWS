from src.ses_suppresion import (
    search_suppression_list,
    get_suppression_list,
    remove_from_suppression_list,
    remove_from_suppression_list_csv,
)

response = None

# Example of how to call the functions

# Get exact match
# response = search_suppression_list('name@domain.com')

# Search with wildcards
# response = search_suppression_list('*@domain.com')

# Fuzzy search (Useful to check if a user mistyped their email)
# response = search_suppression_list('@dmain.com', fuzzy_search=True)

# delete 
# response = remove_from_suppression_list('name@domain.com')

# Remove single user from suppresion list
# response = remove_from_suppression_list('name@domain.com')

# Remove list of users from csv from suppresion list (column containing emails needs to be titled "email")
# response = remove_from_suppression_list_csv('remove_these.csv', dry_run=True)

print(response)