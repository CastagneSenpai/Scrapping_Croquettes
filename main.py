import os
import requests
import csv
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
import matplotlib.pyplot as plt

# Function that return the text of an URL.
def get_page_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print("Échec de la requête à l'URL :", url)
        return None

# Function that return the price in HTML tag "our_price_display" from an URL.
def get_fixed_price_element(url):
    pageContent = get_page_content(url)
    soup = BeautifulSoup(pageContent, 'lxml')
    return soup.find('span', id="our_price_display")

# Function that return the price in HTML tag "our_price_display" from an URL after javascript execution.
def get_dynamic_price_element(url):
    options = Options()
    options.add_argument("--log-level=3")
    options.add_argument("--silent") 
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    driver = webdriver.Chrome(options=options) 
    driver.get(url)
    pageContent = driver.page_source
    driver.quit()

    soup = BeautifulSoup(pageContent, 'lxml')
    return soup.find('span', id="our_price_display")

# Function that announce the dynamic & static prices in french for a dog name.
def announce_price(dogname, dynamic_price, fixed_price):
    return f"Le double pack de croquette de {dogname} est actuellement de {dynamic_price} ({fixed_price} avant rafraîchissement)."

# Function that open the historical price stored in historicalPriceFile, and check if the new dynamic price have to be stored or not.
def historical_price(dogName, url, price, historicalPriceFile):
    if os.path.exists(historicalPriceFile):
        with open(historicalPriceFile, "r", encoding='utf-8') as csvfile:
            hasToWrite = True
            for row in reversed(list(csv.reader(csvfile))):
                if (row[1] == dogName and row[3] == price and datetime.strptime(row[0], "%Y/%m/%dT%H:%M:%S").date() == datetime.now().date()): 
                    hasToWrite = False
                
    if not os.path.exists(historicalPriceFile) or hasToWrite:
        print(f"Mise à jour du fichier pour {dogName}.")
        with open(historicalPriceFile, 'a', encoding='utf-8') as fichier_html:
            fichier_html.write(datetime.now().strftime("%Y/%m/%dT%H:%M:%S") + ',' + dogName + ',' + url + ',' + price +'\n')

# Function that create of plot display based on historical price file
def display_prices(csv_file_path):
    df = pd.read_csv(csv_file_path, header=None, names=['Date', 'Chien', 'URL', 'Prix'])
    df['Date'] = pd.to_datetime(df['Date'])
    chiens = df['Chien'].unique()

    for chien in chiens:
        df_chien = df[df['Chien'] == chien]
        plt.plot(df_chien['Date'], df_chien['Prix'], label=chien)
    
    plt.xlabel('Date')
    plt.ylabel('Prix (€)')
    plt.title('Évolution des prix des croquettes par chien')
    plt.legend()
    plt.grid(True)
    plt.show()



############################# MAIN program #############################
def main():
    os.system('cls')
    current_directory = os.path.dirname(os.path.abspath(__file__))
    historicalPriceFile = os.path.join(current_directory, "prix_croquettes.csv")
    petsonic_urls = {
        "Randy": "https://www.petsonic.fr/croquettes-orijen-original-pour-chiens-114kg-pack-economique-x2.html",
        "Garry": "https://www.petsonic.fr/croquettes-orijen-senior-pour-chiens-114kg-pack-economique-x2.html"
    }

    for dogname, url in petsonic_urls.items():
        fixed_price_element = get_fixed_price_element(url)
        dynamic_price_element = get_dynamic_price_element(url)
        print(announce_price(dogname, dynamic_price_element.text, fixed_price_element.text))
        historical_price(dogname, url, dynamic_price_element.text, historicalPriceFile)            
    display_prices(historicalPriceFile)


# Call the main method properly
if __name__ == "__main__":
    main()