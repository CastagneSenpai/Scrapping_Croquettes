import os
import requests
import csv
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
import matplotlib.pyplot as plt

def get_page_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print("Échec de la requête à l'URL :", url)
        return None

def get_price_element(soup):
    return soup.find('span', id="our_price_display")

def announce_price(nom, title, dynamic_price, fixed_price):
    return f"Le prix du produit \"{title}\" pour {nom} est actuellement de {dynamic_price} ({fixed_price} avant rafraîchissement)."

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

def display_prices(csv_file_path):
    # Charger le fichier CSV dans un DataFrame pandas
    df = pd.read_csv(csv_file_path, header=None, names=['Date', 'Chien', 'URL', 'Prix'])

    # Convertir la colonne 'Date' en format datetime
    df['Date'] = pd.to_datetime(df['Date'])

    # Extraire les noms des chiens uniques
    #df = df.sort_values(by=['Date'])
    chiens = df['Chien'].unique()

    # Tracer la courbe des prix pour chaque chien
    for chien in chiens:
        df_chien = df[df['Chien'] == chien]
        df_chien = df_chien.sort_values(by='Date')
        plt.plot(df_chien['Date'], df_chien['Prix'], label=chien)
    
    # Ajouter des légendes et des titres
    plt.xlabel('Date')
    plt.ylabel('Prix (€)')
    plt.title('Évolution des prix des croquettes par chien')
    plt.legend()
    plt.grid(True)

    # Afficher le graphique
    plt.show()


def main():
    os.system('cls')
    petsonic_urls = {
        "Randy": "https://www.petsonic.fr/croquettes-orijen-original-pour-chiens-114kg-pack-economique-x2.html",
        "Garry": "https://www.petsonic.fr/croquettes-orijen-senior-pour-chiens-114kg-pack-economique-x2.html"
    }

    current_directory = os.path.dirname(os.path.abspath(__file__))
    historicalPriceFile = os.path.join(current_directory, "prix_croquettes.csv")

    for name, url in petsonic_urls.items():
        page_content = get_page_content(url)
        if page_content:
            soup = BeautifulSoup(page_content, 'lxml')
            fixed_price_element = get_price_element(soup)

            options = Options()
            options.add_argument("--log-level=3")
            options.add_argument("--silent")  # Désactiver les messages de Chrome
            options.add_argument('headless')
            options.add_argument('window-size=1920x1080')
            options.add_argument("disable-gpu")
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            driver = webdriver.Chrome(options=options) 
            driver.get(url)
            page_content = driver.page_source
            driver.quit()

            soup = BeautifulSoup(page_content, 'lxml')
            dynamic_price_element = get_price_element(soup)
            
            #card_price = get_card_price(driver)
            phrase_annonce_du_prix = announce_price(name, soup.title.string, dynamic_price_element.text, fixed_price_element.text)
            print(phrase_annonce_du_prix)

            if fixed_price_element and dynamic_price_element:
                historical_price(name, url, dynamic_price_element.text, historicalPriceFile)
            
    display_prices(historicalPriceFile)

if __name__ == "__main__":
    main()
