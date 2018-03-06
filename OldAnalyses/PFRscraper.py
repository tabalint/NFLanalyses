import datetime
def weekday(date):
    return datetime.datetime.strptime(date, '%b %d, %Y').strftime('%A')
    
def year(date):
    date = datetime.datetime.strptime(date, '%b %d, %Y')
    return str(date.year)
    
#Set up the overarching dataframe
import pandas as pd
output = pd.DataFrame(0, index=[0], columns=["Game Code","Year","Week","Game Date","Game Weekday","Game Time","Team","Opponent","Home/Away","Points","W/L","First Downs","Rush Att","Rush Yds","Rush TDs","Pass Cmp","Pass Att","Pass Yd","Pass TD","Pass Int","Sacked","Sacked Yds","Fumbles","Fumbles Lost","Turnovers","Penalties","Penalty Yds","3rd Down Conv.","4th Down Conv.","TOP"])
    
#Set up BeautifulSoup
from bs4 import BeautifulSoup
import urllib2, httplib

baseurl = "http://www.pro-football-reference.com"
loopyear = 2016
# Start the megaloop for the year specified
for gameweek in range(1,18):
    print "Entering week " + str(gameweek)
    # Set up the URL for the week of games and read the data into BS
    url = "http://www.pro-football-reference.com/years/" + str(loopyear) + "/week_" + str(gameweek) + ".htm"
    content = urllib2.urlopen(url).read()
    soup = BeautifulSoup(content, 'lxml')

    # Start the loop for each game on the page
    n=0
    for game in soup.find_all(class_="date"):
        # Start an empty dataframe
        tempDF = pd.DataFrame(0, index=["Away","Home"], columns=["Game Code","Year","Week","Game Date","Game Weekday","Game Time","Team","Opponent","Home/Away","Points","W/L","First Downs","Rush Att","Rush Yds","Rush TDs","Pass Cmp","Pass Att","Pass Yd","Pass TD","Pass Int","Sacked","Sacked Yds","Fumbles","Fumbles Lost","Turnovers","Penalties","Penalty Yds","3rd Down Conv.","4th Down Conv.","TOP"])
        gameyear = loopyear
        
        #Start the DFs with the basic info
        uniqueCode = str(gameyear) + "%02d" %gameweek + "%02d" %(n+1)
        tempDF.loc["Away","Game Code"], tempDF.loc["Home","Game Code"] = uniqueCode, uniqueCode
        tempDF.loc["Away", "Year"], tempDF.loc["Home","Year"] = gameyear, gameyear
        tempDF.loc["Away", "Week"], tempDF.loc["Home","Week"] = gameweek, gameweek
        tempDF.loc["Away", "Game Date"], tempDF.loc["Home", "Game Date"] = game.text, game.text
        tempDF.loc["Away", "Game Weekday"], tempDF.loc["Home", "Game Weekday"] = weekday(game.text), weekday(game.text)
    
        
        #Go to the actual game data in the soup, for away team
        data = game.next_sibling.next_sibling
        #Now start adding the game data to the temp DF
        tempDF.loc["Away", "Team"], tempDF.loc["Home", "Opponent"] = data.find("td").string, data.find("td").string
        tempDF.loc["Away", "Home/Away"] = "Away"
        tempDF.loc["Away", "Points"] = int(data.find("td").next_sibling.next_sibling.string)
        
        #Save the link to the game while we go past it
        gamelink = data.find(class_="right gamelink").a.get('href')
        
        #Go to home team's data
        data2 = game.next_sibling.next_sibling.next_sibling.next_sibling
        tempDF.loc["Away", "Opponent"], tempDF.loc["Home", "Team"] = data2.find("td").string, data2.find("td").string
        tempDF.loc["Home", "Home/Away"] = "Home"
        tempDF.loc["Home", "Points"] = int(data2.find("td").next_sibling.next_sibling.string)
        
        #Calculate winner/loser
        if tempDF.loc["Away", "Points"] > tempDF.loc["Home","Points"]:
            tempDF.loc["Away", "W/L"], tempDF.loc["Home", "W/L"] = "W", "L"
        elif tempDF.loc["Home", "Points"] > tempDF.loc["Away","Points"]:
            tempDF.loc["Home", "W/L"], tempDF.loc["Away", "W/L"] = "W", "L"
        else: tempDF.loc["Home", "W/L"], tempDF.loc["Away", "W/L"] = "T", "T"
        #Check for OT
        if data2.find("td").next_sibling.next_sibling.next_sibling.next_sibling.string.strip() == 'OT':
            tempDF.loc["Away", "W/L"] = tempDF.loc["Away", "W/L"] + "/OT"
            tempDF.loc["Home", "W/L"] = tempDF.loc["Home", "W/L"] + "/OT"
            
        # All data from the week's page is now imported into the DF
        ###
        # Now open the game's specific page to get more in-depth box score info
        try:
            gameContent = urllib2.urlopen(baseurl+gamelink).read()
        except httplib.IncompleteRead as e:
            print "Error with game " + gamelink
            gameContent = e.partial
        gameSoup = BeautifulSoup(gameContent, 'lxml')
        
        #Try to load the game time; if it doesn't work, re-load the data
        # (This happens sometimes, the page loaded isn't a full page. This seems to catch all errors)
        try:
            gametime = gameSoup.find("div", {'class' : 'scorebox_meta'}).find("div").next_sibling.next_sibling.text.split(': ')[1]
        except:
            try:
                gameContent = urllib2.urlopen(baseurl+gamelink).read()
            except httplib.IncompleteRead as e:
                print "Error with game " + gamelink
                gameContent = e.partial
            gametime = gameSoup.find("div", {'class' : 'scorebox_meta'}).find("div").next_sibling.next_sibling.text.split(': ')[1]
        
        #Get the time of the game from the game page
        tempDF.loc["Away", "Game Time"], tempDF.loc["Home", "Game Time"] = gametime, gametime
        
        #This page is a GIANT PAIN IN THE ASS and it won't find the actual table, just the commented fake one
        #So we make the commented fake one into a real Soup
        for x in gameSoup.find_all('div', {'id' : 'all_team_stats'}):
            y = x.find('div', class_="placeholder")
            tableSoup = str(y.next_sibling.next_sibling)
        soup2 = BeautifulSoup(tableSoup, 'html.parser')
        
        #Get First Downs
        tempDF.loc["Away", "First Downs"] = int(soup2.find("tbody").find("th", text="First Downs").next_sibling.text)
        tempDF.loc["Home", "First Downs"] = int(soup2.find("tbody").find("th", text="First Downs").next_sibling.next_sibling.text)
        
        #Rushing Stats "Rush Att","Rush Yds","Rush TDs"
        #Away
        rush = soup2.find("tbody").find("th", text="Rush-Yds-TDs").next_sibling.text.split("-")
        #Sometimes FOR NO REASON there are multiple -s in a row. Catch this:
        if '' in rush: rush.remove('')
        tempDF.loc["Away", "Rush Att"], tempDF.loc["Away", "Rush Yds"], tempDF.loc["Away", "Rush TDs"] = int(rush[0]), int(rush[1]), int(rush[2])
        #Home
        rush = soup2.find("tbody").find("th", text="Rush-Yds-TDs").next_sibling.next_sibling.text.split("-")
        if '' in rush: rush.remove('')
        tempDF.loc["Home", "Rush Att"], tempDF.loc["Home", "Rush Yds"], tempDF.loc["Home", "Rush TDs"] = int(rush[0]), int(rush[1]), int(rush[2])
        
        #Pass Stats "Pass Cmp","Pass Att","Pass Yd","Pass TD","Pass Int"
        passing = soup2.find("tbody").find("th", text="Cmp-Att-Yd-TD-INT").next_sibling.text.split("-")
        #Sometimes FOR NO REASON there are multiple -s in a row. Catch this:
        if '' in passing: passing.remove('')
        tempDF.loc["Away", "Pass Cmp"], tempDF.loc["Away", "Pass Att"], tempDF.loc["Away", "Pass Yd"], tempDF.loc["Away", "Pass TD"], tempDF.loc["Away", "Pass Int"] = int(passing[0]), int(passing[1]), int(passing[2]), int(passing[3]), int(passing[4])
        passing = soup2.find("tbody").find("th", text="Cmp-Att-Yd-TD-INT").next_sibling.next_sibling.text.split("-")
        if '' in passing: passing.remove('')
        tempDF.loc["Home", "Pass Cmp"], tempDF.loc["Home", "Pass Att"], tempDF.loc["Home", "Pass Yd"], tempDF.loc["Home", "Pass TD"], tempDF.loc["Home", "Pass Int"] = int(passing[0]), int(passing[1]), int(passing[2]), int(passing[3]), int(passing[4])
        
        #Sack Stats "Sacked","Sacked Yds",
        sacks = soup2.find("tbody").find("th", text="Sacked-Yards").next_sibling.text.split("-")
        tempDF.loc["Away", "Sacked"], tempDF.loc["Away", "Sacked Yds"] = int(sacks[0]), int(sacks[1])
        sacks = soup2.find("tbody").find("th", text="Sacked-Yards").next_sibling.next_sibling.text.split("-")
        tempDF.loc["Home", "Sacked"], tempDF.loc["Home", "Sacked Yds"] = int(sacks[0]), int(sacks[1])
        
        #Fumble Stats "Fumbles","Fumbles Lost","Turnovers",
        fumbles = soup2.find("tbody").find("th", text="Fumbles-Lost").next_sibling.text.split("-")
        tempDF.loc["Away", "Fumbles"], tempDF.loc["Away", "Fumbles Lost"] = int(fumbles[0]), int(fumbles[1])
        fumbles = soup2.find("tbody").find("th", text="Fumbles-Lost").next_sibling.next_sibling.text.split("-")
        tempDF.loc["Home", "Fumbles"], tempDF.loc["Home", "Fumbles Lost"] = int(fumbles[0]), int(fumbles[1])
        #All Turnovers
        tempDF.loc["Away", "Turnovers"] = tempDF.loc["Away", "Fumbles Lost"] + tempDF.loc["Away", "Pass Int"]
        tempDF.loc["Home", "Turnovers"] = tempDF.loc["Home", "Fumbles Lost"] + tempDF.loc["Home", "Pass Int"]
        
        #Penalty Stats "Penalties","Penalty Yds",
        pen = soup2.find("tbody").find("th", text="Penalties-Yards").next_sibling.text.split("-")
        tempDF.loc["Away", "Penalties"], tempDF.loc["Away", "Penalty Yds"] = int(pen[0]), int(pen[1])
        pen = soup2.find("tbody").find("th", text="Penalties-Yards").next_sibling.next_sibling.text.split("-")
        tempDF.loc["Home", "Penalties"], tempDF.loc["Home", "Penalty Yds"] = int(pen[0]), int(pen[1])
        
        #Other Stats "3rd Down Conv.","4th Down Conv.","TOP"
        tempDF.loc["Away", "3rd Down Conv."] = soup2.find("tbody").find("th", text="Third Down Conv.").next_sibling.text
        tempDF.loc["Home", "3rd Down Conv."] = soup2.find("tbody").find("th", text="Third Down Conv.").next_sibling.next_sibling.text
        tempDF.loc["Away", "4th Down Conv."] = soup2.find("tbody").find("th", text="Fourth Down Conv.").next_sibling.text
        tempDF.loc["Home", "4th Down Conv."] = soup2.find("tbody").find("th", text="Fourth Down Conv.").next_sibling.next_sibling.text
        tempDF.loc["Away", "TOP"] = soup2.find("tbody").find("th", text="Time of Possession").next_sibling.text
        tempDF.loc["Home", "TOP"] = soup2.find("tbody").find("th", text="Time of Possession").next_sibling.next_sibling.text
        #
        n+=1
        output = output.append(tempDF, ignore_index=True)
        if n>len(soup.find_all(class_="date")): break

output.iloc[1:].to_csv('boxscoreBLAHBLAHBLAH' + str(loopyear) + '.csv')
print 'boxscoreBLAHBLAHBLAH' + str(loopyear) + '.csv'