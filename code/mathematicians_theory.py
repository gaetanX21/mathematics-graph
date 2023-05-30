"""
This script creates the CSV files for the mathematicians' graph.

It uses the list of mathematicians obtained from Wikidata using previous queries, and then parses the Wikipedia pages of each mathematician to find the theories they contributed to.

The resulting nodes and edges are saved as CSV files.
"""

import requests
import re
from bs4 import BeautifulSoup
import csv
import pandas as pd


# we use the list of mathematicians obtained from Wikidata using previous queries
def lire_noms_excel(nom_fichier):
    df = pd.read_excel(nom_fichier)
    noms = df.iloc[:, 0].tolist()
    return noms


# we use the list of theories obtained from Wikidata using previous queries
def lire_noms_csv(nom_fichier):
    noms = []
    with open(nom_fichier, 'r', encoding='latin-1') as fichier:
        lecteur_csv = csv.reader(fichier)
        next(lecteur_csv)  # # we skip the first line
        for ligne in lecteur_csv:
            nom = ligne[0]
            noms.append(nom)
    return noms


# replace with your own path
nom_fichier_excel = 'C:/Users/DELL/Desktop/projet inf473G/mathematicians.xlsx'
mathematicians = lire_noms_excel(nom_fichier_excel)

# replace with your own path
nom_fichier_csv2 = 'C:/Users/DELL/Desktop/projet inf473G/nodes2.csv'
keywords = lire_noms_csv(nom_fichier_csv2)
dico = dict()


# this function return the theories which the mathematician contributed to
def searchdomain(mathematician):
    url = f"https://en.wikipedia.org/wiki/{mathematician.replace(' ', '_')}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    footer_div = soup.find('div', {'id': 'footer'})
    if footer_div is not None:
        footer_div.find('li', {'id': 'footer-places-statslink'}).decompose()

    text = soup.get_text()
    keywords_found = []
    for keyword in keywords:
        if keyword in text or keyword.lower() in text:
            keywords_found.append(keyword)

    return keywords_found


# we do this for all the mathematicians
for mathematician in mathematicians:
    L = searchdomain(mathematician)
    if len(L) > 0:
        dico[mathematician] = L


# we can now create the edges
dictionnaire = dico
df_nodes = pd.DataFrame({'Node': list(dictionnaire.keys())})
edges = []
for key, values in dictionnaire.items():
    for value in values:
        edges.append([key, value])
df_edges = pd.DataFrame(edges, columns=['Source', 'Target'])

# we can now save the dataframes in Excel files (we avoid CSV for now because of the encoding problems)
nom_fichier_nodes = "nodesmathematiciansexcel.xlsx"
nom_fichier_edges = "edgesmathematiciansexcel.xlsx"
df_nodes.to_excel(nom_fichier_nodes, index=False)
df_edges.to_excel(nom_fichier_edges, index=False)
