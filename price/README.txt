This project is used to crawl product price, discount, and tag data from Amazon.it.
It is specifically designed for the Amazon Italy marketplace.

Necessary files:
The source file is crawler.py
The virtual environment is venv
The target webpage file is link.xlsx

The folder containing the executable file is dist (operation staff only need to focus on this folder)
The necessary files in the dist folder include:
link.xlsx - Used to store the links to be crawled. You only need to modify the ASINs in the first column; the second column contains a formula that automatically generates the links. Please make sure the number of links matches the number of rows in the ASIN column (empty or incorrect values in the ASIN column will not cause errors; the corresponding rows in the exported file will simply be empty).
crawler.exe - Double-click to run. After launch, a black window (terminal) will appear first, followed by the browser opening automatically. You must then perform a manual operation in the browser (initialisation): change the postcode to an Italian postcode (no login required). Sometimes the postcode does not refresh due to network issues; simply refresh the page and re-enter the postcode. After confirming the postcode is updated, return to the terminal and press Enter to proceed. The crawler will then run automatically.

The output file will be saved in the same folder and named price.csv (if a price.csv already exists, the new file will overwrite the old one).

Notes:

1. If the title column in the output file is empty, it means the script did not enter the product page correctly. Possible causes include: network issues, product issues (out of stock or removed by Amazon).
2. If the title column has data but the price column is empty, it means the network is fine but the product is temporarily out of stock.
3. If a large batch of consecutive products returns no data, it is very likely a network issue. Please try restarting the program or switching to a different network.
4. After the crawler starts fetching webpages, do not perform any operations on the chromedriver window to avoid errors (you may minimise it). If you need to stop the program, simply click the X in the top-right corner of the terminal.