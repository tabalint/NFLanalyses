""" There's a UK game show called pointless, in which 4 pairs compete to win a cash prize.
If you don't win the first game you appear on, you can appear in the next game, but if
you fail twice or win either time, you're out. One of the hosts (Richard Osman) remarked
once that they had 4 new players, and that that was a rare occurrence. I thought that it
surely couldn't be, so I built this.

This script randomly simulates games of Pointless. After the 10th game, it begins counting
how many new teams (labelled here as "players") are in that game.
"""

import uuid
import random


# Class for a Player object, has a name and a number of games played that starts at 1
class Player:
    def __init__(self, name):
        self.name = name
        self.games_played = 0

    def increment_games(self):
        self.games_played += 1
        return self


# Given a list of players, add a new Player to it
def addPlayer(player_list):
    player_list.append(Player(uuid.uuid4()))
    return player_list


# For verification between games - remove any players who have played 2 games
# and add new players up to the limit of 4
def checkPlayers(player_list):
    for player in player_list:
        if player.games_played == 2:
            player_list.remove(player)
    if len(player_list) < 4:
        return checkPlayers(addPlayer(player_list))
    return player_list


numNewPlayers = {0: 0, 1: 0, 2: 0, 3: 0}  # dict to keep track of number of times X new players occurs
games_limit = 100000000
curPlayers = []
for n in range(4):
    curPlayers = addPlayer(curPlayers)

winners = {0: 0, 1: 0, 2: 0, 3: 0}

for game in range(0, games_limit):
    curPlayers = checkPlayers(curPlayers)
    if game > 10:
        numOld = sum(list(map(lambda x: x.games_played, curPlayers)))
        numNewPlayers[3 - numOld] += 1
    winner = random.randint(0, 3)
    winners[winner] += 1
    curPlayers.pop(winner)
    curPlayers = [x.increment_games() for x in curPlayers]

print(numNewPlayers)
print(winners)
