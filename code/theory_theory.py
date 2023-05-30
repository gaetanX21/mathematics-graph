"""
This script creates the CSV files for the theories' graph.

It uses the glossary of areas of mathematics on Wikipedia to get the list of theories, and then uses the "Category" property at the end of Wikipedia pages to know which theories contain the other theories.

The resulting nodes and edges are saved as CSV files.
"""

import requests
from bs4 import BeautifulSoup
import csv


# the following code is used to extract the list of theories from the glossary of areas of mathematics on Wikipedia
url = "https://en.wikipedia.org/wiki/Glossary_of_areas_of_mathematics"
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")
glossary_class = soup.find(class_="glossary")
ids = [item.get("id") for item in glossary_class.find_all_next()]

# some words are not theories and are part of the source code of the page ; we remove those
cite_ref = []
for k in range(0, 16):
    a = f'cite_ref-{k}'
    cite_ref.append(a)

alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
            'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
toc = ['toc', 'toctitle', 'tocheading']
id = []
for item in ids:
    if item != None and item not in cite_ref and item not in alphabet and item not in toc and item != '':
        id.append(item)

# there is a part after "See also" that we don't want, so we truncate the list
c = 0
for k in range(len(id)):
    if id[k] == 'See_also':
        c = k
        break
id = id[:c]

# we must now remove all the underscores with the replace method
words_with_underscore = id
words_without_underscore = []
for word in words_with_underscore:
    word_without_underscore = word.replace("_", " ")
    words_without_underscore.append(word_without_underscore)


# now we want to know which theories contain the other theories. We do so using the "Category" property at the end of Wikipedia pages.
# we create a dictionary to store the relations between subtheories and theories, each key is a theory and the value is a list of theories it belongs to
keywords = words_without_underscore
dico = dict()

# the following two theories are problematic because they have a hyphen in their name, since they're not that important we simply get rid of them
keywords.remove("algebraic k-theory")
keywords.remove("c*-algebra theory")
for key in keywords:
    dico[key] = []


# returns the categories associated to a word
def get_categories(word):
    url = f'https://en.wikipedia.org/wiki/{word}'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    cat = soup.find('div', {'class': 'mw-normal-catlinks'})
    if cat == None:
        return [word]
    else:
        categories = cat.find_all('a')
        L = [category.text.lower() for category in categories]
        del (L[0])
        for category in L:
            if category == word:
                return [word]
        return L


# returns the categories associated to a category (not a word, but a category)
def get_categories2(word):
    url = f'https://en.wikipedia.org/wiki/Category:{word}'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    cat = soup.find('div', {'class': 'mw-normal-catlinks'})
    if cat == None:
        return [word]
    else:
        categories = cat.find_all('a')
        L = [category.text.lower() for category in categories]
        del (L[0])
        for category in L:
            if category == word:
                return [word]
        return L


# returns the categories associated to a word after two iterations, knowing that the categories found must be in the keywords list
def listefinale(key):
    C1 = get_categories(key)
    # we create a copy of C1 because we don't want to modify it while we're iterating over it
    copie1 = get_categories(key)
    I1 = []  # list of words to suppress from C1

    for i in range(len(copie1)):
        C2 = get_categories2(copie1[i])
        for c in C2:
            C1.append(c)
        if copie1[i] not in keywords:
            I1.append(copie1[i])

    for i in I1:
        C1.remove(i)
    copie2 = C1.copy()
    I2 = []

    # we do this another time
    for i in range(len(copie2)):
        C2 = get_categories2(copie2[i])
        for c in C2:
            C1.append(c)
        if copie2[i] not in keywords:
            I2.append(copie2[i])
    
    # now, we delete anything that's not in keywords
    for i in I2:
        C1.remove(i)

    copie3 = C1.copy()
    I3 = []
    for i in range(len(copie3)):
        if copie3[i] not in keywords:
            I3.append(copie3[i])

    for i in I3:
        C1.remove(i)

    # we get rid of the duplicates
    C1 = list(set(C1))
    if len(C1) > 1 and key.lower() in C1:
        C1.remove(key.lower())
    return C1


for key in dico.keys():
    dico[key] = listefinale(key)


# we can now create the edges and nodes CSV files
dictionnaire = dico

nodes_filename = 'nodes_theories.csv'
edges_filename = 'theory_theory.csv'

keys = list(dictionnaire.keys())  # all keys
elements = set()  # all elements
for liste_elements in dictionnaire.values():
    elements.update(liste_elements)

# writing to the CSV file for nodes
with open(nodes_filename, 'w', newline='') as nodes_file:
    writer = csv.writer(nodes_file)
    writer.writerow(['Node'])
    writer.writerows([[key] for key in keys])

# writing to the CSV file for edges
with open(edges_filename, 'w', newline='') as edges_file:
    writer = csv.writer(edges_file)
    writer.writerow(['Source', 'Target'])
    for key, liste_elements in dictionnaire.items():
        writer.writerows([[key, element] for element in liste_elements])
