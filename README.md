# ClickUp to Excel
[![DeepSource](https://deepsource.io/gh/themagicalmammal/clickuptoexcel.svg/?label=active+issues&show_trend=true&token=opRzze8gP9JJbKX_SR5u4zfF)](https://deepsource.io/gh/themagicalmammal/clickuptoexcel/?ref=repository-badge)
[![DeepSource](https://deepsource.io/gh/themagicalmammal/clickuptoexcel.svg/?label=resolved+issues&show_trend=true&token=opRzze8gP9JJbKX_SR5u4zfF)](https://deepsource.io/gh/themagicalmammal/clickuptoexcel/?ref=repository-badge)

Replicate ClickUp Database using Excel.

Developed by [Dipan Nanda](https://github.com/themagicalmammal) (c) 2023

## Example of Usage

```python
from clickuptoexcel import Migrate2Excel

location = 'C:/Data/'
attributes = None
api_key = """<YOUR_API_KEY>"""
helper = Migrate2Excel(location=location, clickup_api_token=, attribute_values=attributes)
"""
:param string location: specify where you would want the database to be replicated
:param list attributes: list of attributes that you want in your excel files
:param string api_key: your Clickup API Token
"""
helper.start()
```

## Changelog
Go [here](CHANGELOG.md) to checkout the complete changelog.

## License
#### This is under GNU GPL v3.0 License
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
