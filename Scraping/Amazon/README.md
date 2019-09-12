## Folder architecture:
===================
Must contains:
- ./urls (folder)
- mapSite.py
- extractLinks.py
- run.py

## Usage:
=====
- run first mapSite.py : Map the website with urls of categories to be scraped and save it to ./urls/category_links.json [cf. docstring in file]
- then extractLinks.py : Will navigate through the categories pages and extract product's urls and save it to ./urls/url_list.csv
- finally run.py : Will scrap the content of each page product from urls list and save it to ./backup.csv