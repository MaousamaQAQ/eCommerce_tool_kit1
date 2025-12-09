This project is used to crawl product, price, availability, and ID number data from OTTO.

Necessary files:
The source file is otto_crawl.py
The virtual environment is venv
The target webpage file is links.xlsx
The browser driver is chromedriver.exe

The folder containing the executable file is dist (operation staff only need to focus on this folder)
The necessary files in the dist folder include:
links.xlsx - Used to store the links that need to be crawled
chromedriver.exe - Used to access webpages (no manual action required)
otto_crawl.exe - Double-click to run
The output file will be saved in the same folder, with the format Time.csv

Notes:
If the webpage cannot be accessed due to network issues, please enable VPN or adjust the network environment.