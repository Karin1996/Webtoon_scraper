import requests
from bs4 import BeautifulSoup
import json
from pprint import pprint
import pandas as pd
import numpy as np
import time
from tqdm import tqdm

url = "https://www.webtoons.com/en/dailySchedule"
total_webtoons = 0
#How many webtoons to scrape. If None get all the webtoons the scraper can find
amount_to_scrape = None
#Set of the genres
genres = set()
#Set with hrefs for the individual webtoons
hrefs = set()


#define function
def ConvertToNumber(fakeNum):
    number = ''

    #Get if the number contains B, M, K or ,
    if "," in fakeNum:
        number = int(fakeNum.replace(",", ""))
    if "K" in fakeNum:
        number = float(fakeNum.replace("K", ""))
        number = int(number * 1000)
    if "M" in fakeNum:
        number = float(fakeNum.replace("M", ""))
        number = int(number * 1000000)
    if "B" in fakeNum:
        number = float(fakeNum.replace("B", ""))
        number = int(number * 1000000000)

    return number


#Get response
response = requests.get(url)
#All the html on the page
all_info = BeautifulSoup(response.content, "html.parser")


#Get the amount of webtoons scraped
total_results = len(all_info.find_all("a", class_="daily_card_item"))


#Get all the genres
genre_results = all_info.find_all("p", class_="genre")
#for each genre add it to the set
for genre in genre_results:
    genres.add(genre.text)

#Define dictionary with the correct genres
webtoon_dictionary = {}
for entry in genres:
    webtoon_dictionary[entry] = {"total_webtoons": 0, "average_subscribers": [], "median_subscribers": [], "average_grade": [], "median_grade": [], "completed": 0, "average_chapters": [], "median_chapters": []}


#Get all the hrefs, add to list (for getting grading and chapters later on)
for tag in all_info.find_all("a", class_="daily_card_item", href= True):
    hrefs.add(tag["href"])

counter = 0
#For each href check information
for href in tqdm(hrefs):
    #if there is a specific amount of webtoons to scrape, scrape that
    if amount_to_scrape:
        if counter == amount_to_scrape:
            break    
    counter += 1

    get_individual_webtoon_response = requests.get(href)
    get_individual_webtoon_info = BeautifulSoup(get_individual_webtoon_response.content, "html.parser")
    
    #Get page content per webtoon
    page_content = get_individual_webtoon_info.find("div", class_="cont_box")

    webtoon_genre = page_content.find("h2", class_="genre")
    webtoon_genre = webtoon_genre.text
   
    #Get subscriber count of this specific webtoon
    webtoon_subscribers = page_content.find("span", class_="ico_subscribe")
    webtoon_subscribers = webtoon_subscribers.find_next_sibling("em")
    webtoon_subscribers = ConvertToNumber(webtoon_subscribers.text)

    #Get grade of this specific webtoon
    webtoon_grade = page_content.find("em", id="_starScoreAverage")
    webtoon_grade = float(webtoon_grade.text)

    #Webtoon status. is completed or not
    status = page_content.find("p", class_="day_info")
    status = status.text.lower()
    
    #Add information to correct genre in dictionary
    for key in webtoon_dictionary:
        if key == webtoon_genre:
            webtoon_dictionary[key]["total_webtoons"] += 1
            webtoon_dictionary[key]["average_subscribers"] += [webtoon_subscribers]
            webtoon_dictionary[key]["average_grade"] += [webtoon_grade]
            webtoon_dictionary[key]["median_subscribers"] += [webtoon_subscribers]
            webtoon_dictionary[key]["median_grade"] += [webtoon_grade]

            if status == "completed":
                webtoon_chapters = page_content.find("span", class_="tx")
                webtoon_chapters = int(webtoon_chapters.text.replace("#", ""))
                webtoon_dictionary[key]["completed"] += 1
                webtoon_dictionary[key]["average_chapters"] += [webtoon_chapters] 
                webtoon_dictionary[key]["median_chapters"] += [webtoon_chapters]  
    
    #print(counter, amount_to_scrape)
    time.sleep(0.5)


#Calculate averages and medians from information in dictionary arrays
for key in webtoon_dictionary:
    
    if webtoon_dictionary[key]["total_webtoons"] > 0:
        #Median likes in this genre
        webtoon_dictionary[key]["median_subscribers"] = round(np.median(webtoon_dictionary[key]["median_subscribers"]))
        #Average likes in this genre
        webtoon_dictionary[key]["average_subscribers"] = round(sum(webtoon_dictionary[key]["average_subscribers"]) / webtoon_dictionary[key]["total_webtoons"])

        #Median grade in this genre
        webtoon_dictionary[key]["median_grade"] = round(float(np.median(webtoon_dictionary[key]["median_grade"])), 2)

        #Average grade in this genre
        webtoon_dictionary[key]["average_grade"] = round(sum(webtoon_dictionary[key]["average_grade"]) / webtoon_dictionary[key]["total_webtoons"], 2)
    
    if webtoon_dictionary[key]["completed"] > 0:
        #Median chapters in this genre
        webtoon_dictionary[key]["median_chapters"] = round(np.median(webtoon_dictionary[key]["median_chapters"]))
        #Average chapters in this genre (only completed webtoons) (if webtoon is "completed" add chapter count to list, then calculate average)
        webtoon_dictionary[key]["average_chapters"] = round(sum(webtoon_dictionary[key]["average_chapters"]) / webtoon_dictionary[key]["completed"])



#Save to a json file
with open("webtoon_information.json", "w") as file:
    json.dump(webtoon_dictionary, file)

#Save to a CSV file
data_frame = pd.DataFrame({
    "Genre": webtoon_dictionary.keys(),
    "Total Webtoons": [row["total_webtoons"] for row in webtoon_dictionary.values()],
    "Average Subscribers": [row["average_subscribers"] for row in webtoon_dictionary.values()],
    "Median Subscribers": [row["median_subscribers"] for row in webtoon_dictionary.values()],
    "Average Grade": [row["average_grade"] for row in webtoon_dictionary.values()],
    "Median Grade": [row["median_grade"] for row in webtoon_dictionary.values()],
    "Total Completed": [row["completed"] for row in webtoon_dictionary.values()],
    "Average Chapters": [row["average_chapters"] for row in webtoon_dictionary.values()],
    "Median Chapters": [row["median_chapters"] for row in webtoon_dictionary.values()],
})
data_frame["Average Subscribers"] = data_frame["Average Subscribers"].apply(lambda x: "" if x == [] else x)
data_frame["Average Grade"] = data_frame["Average Grade"].apply(lambda x: "" if x == [] else x)
data_frame["Average Chapters"] = data_frame["Average Chapters"].apply(lambda x: "" if x == [] else x)

data_frame["Median Subscribers"] = data_frame["Median Subscribers"].apply(lambda x: "" if x == [] else x)
data_frame["Median Grade"] = data_frame["Median Grade"].apply(lambda x: "" if x == [] else x)
data_frame["Median Chapters"] = data_frame["Median Chapters"].apply(lambda x: "" if x == [] else x)

data_frame.to_csv("webtoon_information.csv", header=True, index=False)
