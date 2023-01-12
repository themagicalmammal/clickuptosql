# ClickUp to SQL
[![DeepSource](https://deepsource.io/gh/themagicalmammal/clickuptosql.svg/?label=active+issues&show_trend=true&token=opRzze8gP9JJbKX_SR5u4zfF)](https://deepsource.io/gh/themagicalmammal/clickuptosql/?ref=repository-badge)
[![DeepSource](https://deepsource.io/gh/themagicalmammal/clickuptosql.svg/?label=resolved+issues&show_trend=true&token=opRzze8gP9JJbKX_SR5u4zfF)](https://deepsource.io/gh/themagicalmammal/clickuptosql/?ref=repository-badge)

Replicate ClickUp Database to a SQL Table.

Developed by [Dipan Nanda](https://github.com/themagicalmammal) (c) 2023

## Example of Usage

```python
from clickuptosql import Migrate2Sql
from etl_encrypt import get_clickup_api_key
from sqlalchemy.types import NVARCHAR

spaces = None
attributes = None 
# None selects every attribute by default
# spaces = [<-- LIST OF SPACE_ID'S -->]
# attributes = [<-- LIST OF ATTRIBUTES -->]

api_key = '<-- YOUR API KEY -->'
server = '<-- SERVER NAME -->'  
database = '<-- DATABASE NAME -->'
username = '<-- YOUR USERNAME -->'
password = '<-- YOUR PASSWORD -->'
driver = '<-- SQL DRIVER -->'
sql_string = f'{username}:{password}@{server}/{database}?driver={driver}'
dtype = {'id': NVARCHAR(length=50)}

helper = Migrate2Sql(clickup_api_token=api_key, spaces=spaces, optimise=True, 
                     attribute_values=attributes, sql_connection=sql_string, dtype=dtype)
helper.start()

```

## Changelog
Go [here](CHANGELOG.md) to checkout the complete changelog.

## License
#### This is under GNU GPL v3.0 License
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
