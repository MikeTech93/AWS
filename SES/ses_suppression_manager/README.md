## How to start using the scripts
```bash
# Create virtual environment
python -m virtualenv .venv

# Enter virtual environment
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Uncomment line of code in main.py you want to run

# Execute main.py e.g.
aws-vault exec my_profile  -- python main.py
```

## How to start development
```bash
# Create virtual environment
python -m virtualenv .venv

# Enter virtual environment
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

## Example usage
```python
# Import functions
from src.ses_suppresion import search_suppression_list, get_suppression_list

# Get exact match
response = search_suppression_list("name@domain.com")
print(response)

# Search with wildcards
response = search_suppression_list("*@domain.com")
print(response)

# Fuzzy search (Useful to check if a user mistyped their email)
response = search_suppression_list("@dmain.com", fuzzy_search=True)
print(response)

# Remove single user from suppresion list
response = remove_from_suppression_list('name@domain.com')
print(response)

# Remove list of users from csv from suppresion list, return results to a new csv
# Column containing emails needs to be titled "email"
respone = remove_from_suppression_list_csv(remove_these.csv, dry_run=True):
print(response)
```