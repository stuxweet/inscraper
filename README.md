# InScraper - LinkedIn People Scraper

A simple scraper for LinkedIn using Selenium and Chrome.  
It captures employee names, descriptions, and profile links from a specified company and saves the data in a CSV file separated by semicolons.

> LinkedIn updates its code frequently, so this script might require constant updates.  
***  
## Installation

Git clone this repository:

```
$ git clone https://github.com/stuxweet/inscraper
$ cd inscraper
$ python -m pip install -r requirements.txt
```

## Usage

1. **Close all Chrome browser windows before running the script.** If Chrome is open, the script might throw an error.  
2. Copy the company's "people" page link and paste it as an argument, as shown in the example below:

```
$ python inscraper.py https://www.linkedin.com/company/<COMPANY-NAME>/people/
```

3. The first time you run the script, a Chrome window will open for you to log in to LinkedIn so the script can access the company’s people page data. Press `ENTER` after completing the login.  
4. From there, the script will harvest people data from the provided company URL.

After the scraping is complete, the employee information will be saved in a file named "linkedin_profiles.csv" in the same folder.

To log out or delete the profile used by the script, delete the `inscraperChromeProfile` folder.

## Output Example

```
https://linkedin.com/in/johndoe;John Doe;CEO at Doe Inc
https://linkedin.com/in/mary-2168521512;Mary Lee;Web Developer
```
***
## TO-DO
- add cross-browser support
- suppress useless warnings/infos messages