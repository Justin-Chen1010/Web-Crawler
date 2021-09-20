import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
import unicodedata
import re
import matplotlib.pyplot as plt
import json
import csv


# Webcrawler was taken and edited from the workshops to match the purpose of this assignment.

page_limit = 200 #changed limit to 200 just incase need to do more tests

#Specify the initial page to crawl
base_url = 'http://comp20008-jh.eng.unimelb.edu.au:9889/main/'
seed_item = 'index.html'

seed_url = base_url + seed_item
page = requests.get(seed_url)
soup = BeautifulSoup(page.text, 'html.parser')

headline = []
review_text = []
visited_urls = [] 
pages_visited = 1

#Remove index.html
links = soup.findAll('a')
seed_link = soup.findAll('a', href=re.compile("^index.html"))
to_visit_relative = [l for l in links if l not in seed_link]

# Resolve to absolute urls
to_visit = []
for link in to_visit_relative:
    to_visit.append(urljoin(seed_url, link['href']))
    
#Find all outbound links on succsesor pages and explore each one 
while (to_visit):
    # Impose a limit to avoid breaking the site 
    if pages_visited == page_limit :
        break
        
    # consume the list of urls
    link = to_visit.pop(0)

    # need to concat with base_url, an example item <a href="catalogue/sharp-objects_997/index.html">
    page = requests.get(link)
    
    # scraping code goes here
    soup = BeautifulSoup(page.text, 'html.parser')
    
    # mark the item as visited, i.e., add to visited list, remove from to_visit
    visited_urls.append(link)
    
    new_links = soup.findAll('a')
    for new_link in new_links :
        new_item = new_link['href']
        new_url = urljoin(link, new_item)
        if new_url not in visited_urls and new_url not in to_visit:
            to_visit.append(new_url)
        
    pages_visited = pages_visited + 1
    
    review_text_elem =soup.find_all(id='articleDetail') #Create a list for article text
    for item in review_text_elem:
        review_text.append(item.text)
    headline_elem = soup.find_all(class_='headline') #Create a list of headlines
    for item in headline_elem:
        headline.append(item.text)

Task_1 = list(zip(visited_urls, headline))
Task_1_data = pd.DataFrame(Task_1, columns = ["URL", "Headline"])
Task_1_data.to_csv('task1.csv', index = False)


#Task 2

tennis_athletes = []
searchStr =  ""
with open ('tennis.json', 'r') as f:
    Data = json.load(f)
for athlete in Data :
    tennis_athletes.append(athlete['name']) #append all names into Name 1| Name 2 style for matching
    searchStr += athlete['name']
    searchStr += '|'
searchStr = searchStr[:-1]

articles = list(zip(visited_urls, headline, review_text))
article_table = pd.DataFrame(articles, columns = ["URLS", "Headline", "Article"]) #Only to visualize


check_validity_url = []
check_validity_headline = []
check_validity_player = []
check_validity_score = []
score_search = r"(\(?[0-9]+[\/\-][0-9]+\)?.){2,10}" #Regex to match the scores looking for 2-10 repetitions


for (current_url, current_headline, article) in articles:
    if (re.search(searchStr, current_headline, re.IGNORECASE)): 
        #searching for name in headline, unlikely to have complete score in title
        result = re.search(searchStr, current_headline, re.IGNORECASE)
        check_validity_url.append(current_url)
        check_validity_player.append(result.group(0))
        check_validity_headline.append(current_headline)

        #searching for name in article first then matching to see if there is a valid score, if there is proceed.
    elif re.search(searchStr, article, re.IGNORECASE) and re.search(score_search, article):
        result = re.search(searchStr, article, re.IGNORECASE)
        score = re.search(score_search, article)
        score = score.group(0)
        score = score.strip('.') # This gets rid of the extra . and spaces that my regex allowed
        score = score.strip(',')
        score = score.strip()
        check_validity_url.append(current_url)
        check_validity_player.append(result.group(0))
        check_validity_score.append(score) # Append all the matches results
        check_validity_headline.append(current_headline)

    else: 
        continue


filter_1_articles = list(zip(check_validity_url, check_validity_headline, check_validity_player, check_validity_score))
filter_1_table = pd.DataFrame(filter_1_articles, columns = ["URLS", "Headline", "Player", "Score"]) #Only to visualize

valid_url = []
valid_headline = []
valid_player = []
valid_score = []
is_tiebreaker = "\([0-9]+[\/\-][0-9]+\)"
is_number = "[0-9]+"
game_valid = 0
point_difference = 0
game_difference = 0
game_difference_list = []

for (current_url, current_headline, current_player, current_score) in filter_1_articles:
    for score in current_score:
        no_tiebreaker_score = re.sub(is_tiebreaker, "", current_score) #Tiebreakers don't factor into game difference
        split_score = no_tiebreaker_score.split()
        point_difference = 0
        for game in split_score: #Checking game validity by score difference
            values = re.findall(is_number, str(game))
            score_a = int(values[0])
            score_b = int(values[-1])
            game_diff = score_a - score_b
            point_difference += game_diff
            if (game_diff == 0):
                game_valid = 0
                continue
            elif (((score_a == 6) or (score_b == 6)) and abs(game_diff) >=2):
                game_valid = 1 #Checks game score for win via 6-4, 6-2, 6-0 etc.
            elif (((score_a == 7) or (score_b == 7)) and abs(game_diff) <=2):
                game_valid = 1 #Checks game score for win via tiebreaker 7-6, 6-7 etc.
            elif (abs(game_diff) == 2):
                game_valid = 1
            else:
                game_valid = 0
                continue
    if (game_valid == 1): #If the game is valid append all valid game data
        game_difference = abs(point_difference)
        game_difference_list.append(game_difference)
        valid_url.append(current_url)
        valid_headline.append(current_headline)
        valid_player.append(current_player)
        valid_score.append(current_score)
        game_valid = 0
        game_difference = 0



Task_2 = list(zip(valid_url, valid_headline, valid_player, valid_score))
Task_2_data = pd.DataFrame(Task_2, columns = ["URL", "Headline", "Player", "Score"])
Task_2_data.to_csv('task2.csv', index = False)                           

#Task 3

Task_3 = list(zip(valid_player, game_difference_list))
Task_3_data_processing = pd.DataFrame(Task_3, columns = ["Player", "game_difference"])

#Make new lists to store information
unique_player = []
average_score_list = []
URLS =[]
grouped = Task_3_data_processing.groupby(["Player"])
for group_name, df_group in grouped:

    score_difference = 0
    average_score = 0
    entries = 0
    for row_index, row in df_group.iterrows():
        score_difference += row.game_difference #Gets total score difference
        entries += 1 

    average_score = (score_difference / entries) #Take the total score difference and divide by entries
    average_score_list.append(average_score)
    unique_player.append (row.Player)
    URLS.append(entries)

task_3_final = list(zip(unique_player, average_score_list))
task_3_pd = pd.DataFrame(task_3_final, columns = ["Player", "avg_game_difference"])
task_3_pd.to_csv("task3.csv", index = False)

#Task 4

task_4_data = list(zip(unique_player, URLS))
task_4_pd = pd.DataFrame(task_4_data, columns = ["Player", "Article_for_Player"])

sorted_pd = task_4_pd.sort_values('Article_for_Player', ascending = False)
sorted_pd = sorted_pd[:5] #slice into top 5

#code used to make graph for task 4

import matplotlib.pyplot as plt
import calendar
from numpy import arange

player = sorted_pd.Player
Number_of_Article_for_Player = sorted_pd.Article_for_Player
plt.bar(arange(len(Number_of_Article_for_Player)),Number_of_Article_for_Player)
plt.xticks( arange(len(player)),player, rotation=30)
plt.ylabel('Amount of Articles about Player')
plt.title("Most frequently wrote about Players")
plt.savefig("task4.png", dpi = 300, bbox_inches = 'tight')
plt.show()

#Task 5

winrate= []
player_order= []
SearchPlayer = ""
for player in unique_player:
    SearchPlayer += player
    SearchPlayer += '|'
SearchPlayer = SearchPlayer[:-1]

#Make a Name 1| Name 2 string and search for the unique players in the JSON file, then append their win pct.
for athlete in Data :
    if (re.search(SearchPlayer, athlete['name'], re.IGNORECASE )):
        winrate.append(athlete['wonPct'])
        result = re.search(SearchPlayer, athlete['name'], re.IGNORECASE )
        player_order.append(result.group(0)) #need to remake player list according to matching order.
task_5_wr = list(zip(player_order, winrate))
task_5_wr_df = pd.DataFrame(task_5_wr, columns = ['Player', 'Winrate'])
task_5_wr_df = task_5_wr_df.sort_values(by = 'Player', ascending = True) #Sort in Alphabetical Order
task_5_wr_df['avg_game_difference'] = average_score_list
task_5_wr_df['Player'] = unique_player #Fix capitalization error, this data is then moved to make plots

#code used to make the scatter plot for task 5

task_5_wr_df = task_5_wr_df.sort_values(by = 'Winrate', ascending = True)
scatter_plot = task_5_wr_df.plot.scatter(x = 'avg_game_difference', y = 'Winrate')

for x,y,z in zip(task_5_wr_df.avg_game_difference, task_5_wr_df.Winrate, task_5_wr_df.Player):
    printed = 0
    for player in (z):
        label = z
        if printed == 0:
            plt.annotate(label, (x,y), textcoords="offset points", xytext=(5,-5),ha='left') 
            # (x,y) is point to label, ha is horizontal allignment etc.
            printed = 1


plt.title("Player's Winrate and Average Game Difference")
plt.xlabel('Average Game Difference')
plt.ylabel('Winrate in %')
plt.savefig("task5.png", dpi = 300, bbox_inches = 'tight')
plt.show()