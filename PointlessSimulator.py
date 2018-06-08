import uuid
import random


class Player:
    def __init__(self, name):
        self.name = name
        self.games_played = 0

    def increment_games(self):
        self.games_played += 1
        return self


def addPlayer(player_list):
    player_list.append(Player(uuid.uuid4()))
    return player_list


def checkPlayers(player_list):
    for player in player_list:
        if player.games_played == 2:
            player_list.remove(player)
    if len(player_list) < 4:
        return checkPlayers(addPlayer(player_list))
    return player_list


numNewPlayers = {0: 0, 1: 0, 2: 0, 3: 0}
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
