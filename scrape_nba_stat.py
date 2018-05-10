#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 22 18:51:04 2018
@author: wilsonchan

objective:
- open the web page which lists all teams
- i.e. http://stats.nba.com/teams/
  - iterate all teams
  - e.g. Boston, http://stats.nba.com/team/1610612738/
    - scrape url of all players from the team
      - iterate all player pages
      - scrape all traditional splits for current team (e.g. Boston)
- store all data into a csv file
"""

from selenium import webdriver
from bs4 import BeautifulSoup
import time
import csv

def chrome_webdriver():
    driver = webdriver.Chrome('/usr/local/bin/chromedriver')
    """
    installation of Chrome webdriver is required to call this driver
    http://chromedriver.chromium.org
    """
    return driver

class Team():
    '''class for NBA teams'''
    def __init__(self):
        self.name = ""
        self.link = ""
    def __str__(self):
        return 'getting '+self.name+"'s link\n" + self.link

class Player():
    '''class for NBA players'''
    def __init__(self):
        self.link = ""
        self.name = ""
        self.num = ""
        self.current_team = ""
        self.trad_split = [] #average gaming perforamce by year
    def __str__(self):
        return self.name+' '+self.num+' '+self.current_team+'\n'+self.link

def get_all_teams(url):
    """function which returns a list of Team objects"""
    team_list = []
    
    driver = chrome_webdriver()
    driver.get(url)
    #call driver, and get the url
    time.sleep(2)
    
    soup = BeautifulSoup(driver.page_source, 'lxml')
    div = soup.find('div', {'nba-with-data-divisions':'divisions'})
    #create the soup and targeted tag

    for a in div.find_all('a', class_='stats-team-list__link'):
        #iterate all NBA teams
        team = Team() #create Team object
        team.name = a.text.strip()
        team.link = 'http://stats.nba.com' + a['href']
        team_list.append(team) #append the Team object to list
        print(team.__str__()) #print out the team and its link
    
    driver.quit()
    #leave driver
    return team_list

def get_all_player_links(team_list):
    """function which returns a list of NBA player links"""
    player_link_list = []
    driver = chrome_webdriver()
    #call driver

    for team in team_list:
        #iterate a list of Team objects
        driver.get(team.link)
        #get the url of NBA team
        time.sleep(2)
        
        soup = BeautifulSoup(driver.page_source, 'lxml')
        div = soup.find('div', class_='nba-stat-table__overflow')
        #create the soup and targeted tag

        for tr in div.find_all('tr', {'data-ng-repeat':True}):
            #iterate all NBA player links for the NBA team
            link = 'http://stats.nba.com' + tr.find('a')['href']
            player_link_list.append(link)
            # print(tr.find('a').text) #print the player name
            # print(link)
            
    driver.quit()
    #leave driver
    return player_link_list

def get_info_all_player(player_link_list):
    """function which returns a list of Player objects"""
    player_list = []
    driver = chrome_webdriver()
    #call driver
    
    for player_link in player_link_list:
        #iterate all NBA player links
        split_list_all_years = []
        #list of lists to contain splits for this player
        
        driver.get(player_link)
        #get url
        time.sleep(4)
        
        soup = BeautifulSoup(driver.page_source, 'lxml')
        div = soup.find('div', class_='nba-stat-table__overflow')
        #create soup and targeted tag


        if div is not None:
        #check if there is any split data listed in the player link
        
            player = Player() #create Player object
            player.link = player_link
            player.name = soup.find('div', class_='player-summary__player-name' \
                    ).text.strip().replace('\n', ' ')
            player.num = soup.find('span', class_='player-summary__player-number').text
            player.current_team = div.find('td',class_='text').text
            #team played for current year
            #one player may play in more than one team over his NBA career
            
            for tr in div.find_all('tr', {'data-ng-repeat':True}):
                #iterate all years played by this player
                if player.current_team == tr.find('td',class_='text').text:
                #check if the year is played in player's current team
                    split_list_year = [] 
                    
                    for td in tr.find_all('td'):
                        #iterate all splits for this year
                        split_list_year.append(td.text)
                        #append the splits of this year to list
                        
                    split_list_all_years.append(split_list_year)
                    #append the splits for all years to the list of lists
                
            player.trad_split = split_list_all_years
            player_list.append(player)
            #append player Object to list

        print(player.__str__())
        #print basic information to observe progress
    
    driver.quit()
    #leave driver
    return player_list


def add_to_csv(player_list):
    """function to load NBA player data to csv file"""
    csvFile = open('player_list_with_tra_splits.csv', 'w')

    driver = chrome_webdriver()
    driver.get(all_player_list[0].link)
    time.sleep(2)
    
    soup = BeautifulSoup(driver.page_source, 'lxml')
    tr = soup.find('div', class_='nba-stat-table__overflow').find('tr')
    
    driver.quit()
    
    header = []
    for th in tr.find_all('th'):
        header.append(th.text)
        
    header.insert(0,'Num')
    header.insert(0,'Name')

    writer = csv.writer(csvFile)
    writer.writerow(header)

    for player in player_list:
        print(player.name)
        for year_index in range(0,len(player.trad_split)):
            row = player.trad_split[year_index].copy()
            #copy by value but NOT by reference
            row.insert(0,player.num)
            row.insert(0,player.name)
            writer.writerow(row)

"""start scrapping by calling the above functions with specified argument"""
url = 'http://stats.nba.com/teams/'
all_team = get_all_teams(url)
all_player_links = get_all_player_links(all_team)
all_player_list = get_info_all_player(all_player_links)
"""load data to text file"""
add_to_csv(all_player_list)

