def playyds(play):
    if "]" in play:
        words = play[:-1].split(" ")
    else:
        words = play.split(" ")
    try:
        if "yards (" in play:
            return words[words.index("yards") - 1]
        elif "yards." in play:
            return words[words.index("yards.") - 1]
        elif "yards," in play:
            return words[words.index("yards,") - 1]
        elif "yards" in play:
            return words[words.index("yards") - 1]
        else:
            return 0
    except Exception:
        print play, words
        return 0


def playtype(play):
    # if "END" in play:
    #     return("End", -999)
    if "INTERCEPT" in play:
        return ("Pass - Interception", -150)
    elif "FUMBLE" in play:
        if "pass" in play:
            return("Pass - Fumble", -140)
        else:
            return("Run - Fumble", -130)
    elif "kick" in play or "punt" in play or "field goal" in play or "extra point" in play:
        return ("Kick", -999)
    elif "pass incomplete" in play:
        return ("Pass - Incomplete", -110)
    elif "pass" in play:
        return ("Pass", playyds(play))
    elif "Timeout" in play:
        return ("Timeout", -999)
    elif "spike" in play or "kneel" in play:
        return ("Time Manage", -999)
    elif "sack" in play:
        return ("SACK!", playyds(play))
    else:
        return ("Run", playyds(play))