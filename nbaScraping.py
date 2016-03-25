import requests
import pandas as pd
import time
import bs4
import requests
import re
import unicodedata
from selenium import webdriver
import collections


class scrapePlayerData(object):
        def __init__(self):
            self.playerInfo = []
            self.playerData = None
            self.pageCount = 0
            self.pageUrl = 'http://stats.nba.com/league/player/#!/'
            self.browser = webdriver.Firefox()
            self.pattern = re.compile(r"^(?:\\.|[^/\\])*/((?:\\.|[^/\\])*)/")
            self.statsDict = collections.OrderedDict([('GP', None),('MIN', None),('FGM', None),('FGA', None),('FG%', None),('3PM', None),('3PA', None),('3P%', None),('FTM', None),('FTA', None),('FT%', None),('OREB', None),('DREB', None),('REB', None),('AST', None),('TOV', None),('STL', None),('BLK', None),('PTS', None),('FanDuel', None)])
            self.fantasyPlayerInfo = []


        def openBrowser(self):
            self.browser.get(self.pageUrl)
            self.scrapePlayerInfo()

        def nextPage(self):
            self.browser.find_element_by_css_selector('#main-container > div:nth-child(2) > div > div:nth-child(3) > div > div > div > div > div.ng-scope > div.table-pagination.ng-scope > div.page-nav.right').click()
            self.scrapePlayerInfo()


        def scrapePlayerInfo(self):
            self.pageCount = self.pageCount +1
            html = self.browser.page_source
            soup = bs4.BeautifulSoup(html, 'html.parser')
            for row in soup.find_all('tr', class_ = 'ng-scope'):
                playerTd = row.find('td' ,class_='first')
                teamTd = row.find('td', class_='text')
                try:
                   playerHref = str(playerTd.find('a').get('href'))
                   teamHref = str(teamTd.find('a').get('href'))
                   self.playerInfo.append({'Name': playerTd.string,'playerId': str(self.pattern.match(playerHref[12:23]).group(1)),'playerLink': 'http://stats.nba.com/player/#!' + playerTd.find('a').get('href'),'TeamName':teamTd.string, 'teamId': str(self.pattern.match(teamHref[10:25]).group(1))})
                except:
                    pass
            if self.pageCount < 1:
                self.nextPage()

            else:
                self.playerData = pd.DataFrame(self.playerInfo)
                self.pageCount = 0
                self.getFantasyInformation()

        def getFantasyInformation(self):
            for index,row in self.playerData.iterrows():
                placeHolderArray = []
                self.pageCount = self.pageCount  + 1
                if self.pageCount <=1:
                    self.browser.get('http://stats.nba.com/player/#!/' + str(row['playerId']) + '/fantasy')
                    print 'waiting...'
                    time.sleep(5)
                    soup = bs4.BeautifulSoup(self.browser.page_source, 'html.parser')
                    tables = soup.find_all('tr')
                    for table in tables:
                        for row in table.find_all('td'):
                            string = str(unicodedata.normalize('NFKD', row.text).encode('ascii', 'ignore').strip())
                            try:
                                placeHolderArray.append(float(string))
                            except:
                               try:
                                   newString = re.match(r"([^\s]+)", string).group(1)
                                   placeHolderArray.append(float(newString))
                               except:
                                   pass
                    N = 20
                    separatedList = [placeHolderArray[n:n+N] for n in range(0, len(placeHolderArray), N)]
                    for sublist in separatedList:
                        for x in range(0,len(sublist)):
                            self.statsDict.values()[x] = sublist[x]
                        self.fantasyPlayerInfo.append(self.statsDict)
                    print self.fantasyPlayerInfo



                    #     print table
                    # tables = soup.find_all('tr', class_= 'ng-scope')
                    # # for table in tables:
                    # #     for element in table.find_all('td'):
                    # #         print element.text
                    # # time.sleep(200)














start = scrapePlayerData()
start.openBrowser()



