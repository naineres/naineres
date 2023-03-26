#!/bin/bash

url="https://www.blockchainevent.fr/crypto/matic-polygon/"

# GET request to the webpage
html_content=$(curl -s "$url")

timestamp=$(date +"%Y-%m-%d %H:%M:%S")

price=$(echo "$html_content" | grep -oP '(?<=<span class="cryptowp-text-price-amount">)[^<]+')
echo "$timestamp;$price" >> prices.csv


capitalisation=$(echo "$html_content" | grep -oP '(?<=<span class="cryptowp-text-market-cap-amount">)[^<]+')
echo "$timestamp;$capitalisation" >> capitalisation.csv
