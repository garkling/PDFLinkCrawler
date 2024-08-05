## A simple PDF link crawler

# Init
Create a virtual environment: 
- `ENV_NAME=<env_name>`
- `python3 -m venv $ENV_NAME`
- `source $ENV_NAME/bin/activate`
- `pip install -r requirements.txt`

# Important settings
- `ROBOTSTXT_OBEY = True` - always keep `True`
- `DOWNLOAD_DELAY = 0.1` - `100ms` delay between request, adjust
- `DEFAULT_URL_SCHEME_ON_MISSING = "https://"` - you can change to `http://`

# Run
In the `pdfcrawler` directory in the virtual env: 
- `scrapy crawl pdfs -o <savefilename>.[json|jsonl] -a start_urls="<your_url1>","<your_url2>" -a all_subdomains=[True|False]`
  - `start_urls` are your entry URLs to begin with
    - you can specify multiple by a comma
    - you can omit the scheme and the trailing `//`, as well as `www` because it is a subdomain itself if you don't need it

  - `all_subdomains` indicates whether to ignore passed subdomains in `start_urls` and consider only the main domain (defaults to `False`)
  - `<savefilename>.[json|jsonl]` are the output file with PDF links - you can choose `.json` or `.jsonl` (`jsonlines`) 
    - prefer `.jsonl` if you need to append new links to the file from different processes

Examples:
1. `scrapy crawl pdfs -o dektec_pdfs.json -a start_urls="www.dektec.com" -a all_subdomains=True`
2. `scrapy crawl pdfs -o sot_pdfs.json -a start_urls="https://seaofthieves.fandom.com/wiki/Fishing" -a all_subdomains=False`


# TODO List
- [x] The default crawler
- [ ] An LLM integration
- [ ] A RDS auto-upload
