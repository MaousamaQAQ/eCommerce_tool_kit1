This project is used to crawl, via SellerSprite, the following data for any Amazon product (with permission) on any marketplace (including competitor products - as long as the ASIN is available):
Category BSR rank, 7-day BSR growth, 7-day BSR growth rate, parent-level sales volume, growth rate, parent-level revenue, child-level sales volume, child-level revenue, and price data (see the SellerSprite "Competitor Analysis" page for detailed field definitions).

Necessary files:
The source file is price.py
The virtual environment is venv
The browser driver is chromedriver.exe
The credentials file is Ap.txt
The ASIN configuration folder is the Asin folder
The output folder is download

The folder containing the executable file is dist (operation staff only need to focus on this folder)
The necessary files in the dist folder include:
Asin folder - Stores ASIN lists for 5 marketplaces. Each file is named as MarketplaceAsin.xlsx (if you want to check the IT marketplace, simply add, replace, or delete ASINs in the first column of ITAsin.xlsx)
Ap.txt - Stores SellerSprite credentials, with the first line being the account and the second line being the password
chromedriver.exe - Used to access the webpage (no manual operation required)
price.exe - The executable file. Double-click to run. A black window (terminal) will appear first, then after about 10 seconds, a UI window will pop up for marketplace selection (multiple marketplaces can be selected at once). Note: Do not enable headless mode, or SellerSprite will detect it and the crawler will fail to retrieve data.
download folder - Used to store program output files, named as Country_Date_Time.csv

Notes:
1. SellerSprite can only output ASINs that have available data on the platform. Some ASINs may not be retrievable if SellerSprite has not collected them.
2. SellerSprite may occasionally match a product incorrectly (this is rare. If it happens, stop querying that ASIN, remove it from the ASIN list, and report the issue to SellerSprite support).
3. SellerSprite's data may have a delay of around 2 days. It is not suitable for high-frequency price updates during promotions, and is only recommended for daily operational price tracking.
4. After the crawler begins fetching webpages, do not operate the chromedriver window to avoid errors (you may minimise it). If you need to terminate the program, click the X in the top-right corner of the terminal.