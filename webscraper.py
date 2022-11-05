import requests
from bs4 import BeautifulSoup
import json
from pprint import pprint

url = "https://www.webtoons.com/en/dailySchedule"
total_webtoons = 0
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
    webtoon_dictionary[entry] = {"total_webtoons": 0, "average_subscribers": [], "average_grade": [], "completed": 0, "average_chapters": []}



#Get all the hrefs, add to list (for getting grading and chapters later on)
for tag in all_info.find_all("a", class_="daily_card_item", href= True):
    hrefs.add(tag["href"])

counter = 0
#TODO: Disable counter
#For each href check information
for href in hrefs:
    counter += 1
    if counter == 50:
        break
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

            if status == "completed":
                webtoon_chapters = page_content.find("span", class_="tx")
                webtoon_chapters = int(webtoon_chapters.text.replace("#", ""))
                webtoon_dictionary[key]["completed"] += 1
                webtoon_dictionary[key]["average_chapters"] += [webtoon_chapters]   
    print(counter)


#Calculate averages from information in dictionary arrays
for key in webtoon_dictionary:
    
    if webtoon_dictionary[key]["total_webtoons"] > 0:
        #Average likes in this genre
        webtoon_dictionary[key]["average_subscribers"] = round(sum(webtoon_dictionary[key]["average_subscribers"]) / webtoon_dictionary[key]["total_webtoons"], 2)
        #Average grade in this genre
        webtoon_dictionary[key]["average_grade"] = round(sum(webtoon_dictionary[key]["average_grade"]) / webtoon_dictionary[key]["total_webtoons"], 2)
    
    if webtoon_dictionary[key]["completed"] > 0:
        #Average chapters in this genre (only completed webtoons) (if webtoon is "completed" add chapter count to list, then calculate average)
        webtoon_dictionary[key]["average_chapters"] = round(sum(webtoon_dictionary[key]["average_chapters"]) / webtoon_dictionary[key]["completed"])


#Save to a json file
with open("webtoon_information.json", "w") as file:
    json.dump(webtoon_dictionary, file)


