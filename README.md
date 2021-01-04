QuickFS Scraping
============================

This project should be used as a tool to gather
financial data from us market traded equities. The
main source for scraping the data is a site called
[QuickFS](https://quickfs.net/).

An account is necessary, and API keys should be 
retrieved for API scraping and one for web scraping.
Be aware that excessive web scraping can cause
being blocked from QuickFS. Also know that the free
membership has a limited amount of quotes. Excessive
api scraping can result in exceeding the daily quota.

### setup: 
```bash
pip install -r requirements.txt

quickfs_data > quickfs_keys.json : change key values
```

### Usage:
```bash
quickfs_scraping > process.py: to execute the code

```
Copyright & License
-------------------

  * Copyright 2021, Diego Heer
  * License: MIT
