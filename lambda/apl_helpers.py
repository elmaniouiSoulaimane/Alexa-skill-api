from utils import create_url

def apl_current(potValue, players, holeCardsName, myindex, myHoleIndex, flopCardsName):
    datasources = {
        "headlineTemplateData": {
            "type": "object",
            "objectId": "headlineSample",
            "properties": {
                "textContent": {
                    "potText": {
                        "type": "PlainText",
                        "text": "Pot : "+str(potValue) +"$"
                    },
                    "delearText":{
                        "type": "PlainText",
                        "text": players[0].name +":" +str(players[0].chips)+ "$-P:"+str(players[0].myprice)+"$"
                    },
                    "smallText":{
                        "type": "PlainText",
                        "text": players[1].name +":" +str(players[1].chips)+ "$-P:"+str(players[1].myprice)+"$"
                    },
                    "bigText":{
                        "type": "PlainText",
                        "text": players[2].name +":" +str(players[2].chips)+ "$-P:"+str(players[2].myprice)+"$"
                    },
                    "position4Text":{
                        "type":"PlainText",
                        "text": players[3].name +":" +str(players[3].chips)+ "$-P:"+str(players[3].myprice)+"$"
                    },
                    "position5Text":{
                        "type":"PlainText",
                        "text": players[4].name +":" +str(players[4].chips)+ "$-P:"+str(players[4].myprice)+"$"
                    }
                },
                "avatar1":create_url("Media/images/"+players[0].name+".png"),
                "avatar2":create_url("Media/images/"+players[1].name+".png"),
                "avatar3":create_url("Media/images/"+players[2].name+".png"),
                "avatar4":create_url("Media/images/"+players[3].name+".png"),
                "avatar5":create_url("Media/images/"+players[4].name+".png"),
                "hole1":create_url("Media/Cards/"+holeCardsName[0]+".png"),
                "hole2":create_url("Media/Cards/"+holeCardsName[1]+".png"),
                "hole3":create_url("Media/Cards/"+holeCardsName[2]+".png"),
                "hole4":create_url("Media/Cards/"+holeCardsName[3]+".png"),
                "hole5":create_url("Media/Cards/"+holeCardsName[4]+".png"),
                "hole6":create_url("Media/Cards/"+holeCardsName[5]+".png"),
                "hole7":create_url("Media/Cards/"+holeCardsName[6]+".png"),
                "hole8":create_url("Media/Cards/"+holeCardsName[7]+".png"),
                "hole9":create_url("Media/Cards/"+holeCardsName[8]+".png"),
                "hole10":create_url("Media/Cards/"+holeCardsName[9]+".png"),
                "hole"+str(myHoleIndex):create_url("Media/Cards/"+str(players[myindex].holeCards[0])+".png"),
                "hole"+str(myHoleIndex+1):create_url("Media/Cards/"+str(players[myindex].holeCards[1])+".png"),
                "myhole1":create_url("Media/Cards/"+str(players[myindex].holeCards[0])+".png"),
                "myhole2":create_url("Media/Cards/"+str(players[myindex].holeCards[1])+".png"),
                "flop1":create_url("Media/Cards/"+flopCardsName[0]+".png"),
                "flop2":create_url("Media/Cards/"+flopCardsName[1]+".png"),
                "flop3":create_url("Media/Cards/"+flopCardsName[2]+".png"),
                "turn":create_url("Media/Cards/"+flopCardsName[3]+".png"),
                "river":create_url("Media/Cards/"+flopCardsName[4]+".png"),
                "me":create_url("Media/images/me.png"),
                "bkgd_3":create_url("Media/images/background3.jpg"),
                "dealer_c":create_url("Media/images/dealer_c.png")
            }
        }
    }
    return datasources

def apl_current_win(winText, potValue, players, listHoleCards, flopCardsName):
    datasources = {
        "headlineTemplateData": {
            "type": "object",
            "objectId": "headlineSample",
            "properties": {
                "textContent": {
                    "winText":{
                        "type": "PlainText",
                        "text": winText
                    },
                    "potText": {
                        "type": "PlainText",
                        "text": "Pot : "+str(potValue) +"$"
                    },
                   "delearText":{
                        "type": "PlainText",
                        "text": players[0].name +":" +str(players[0].chips)+ "$-P:"+str(players[0].myprice)+"$"
                    },
                    "smallText":{
                        "type": "PlainText",
                        "text": players[1].name +":" +str(players[1].chips)+ "$-P:"+str(players[1].myprice)+"$"
                    },
                    "bigText":{
                        "type": "PlainText",
                        "text": players[2].name +":" +str(players[2].chips)+ "$-P:"+str(players[2].myprice)+"$"
                    },
                    "position4Text":{
                        "type":"PlainText",
                        "text": players[3].name +":" +str(players[3].chips)+ "$-P:"+str(players[3].myprice)+"$"
                    },
                    "position5Text":{
                        "type":"PlainText",
                        "text": players[4].name +":" +str(players[4].chips)+ "$-P:"+str(players[4].myprice)+"$"
                    }
                },
                "avatar1":create_url("Media/images/"+players[0].name+".png"),
                "avatar2":create_url("Media/images/"+players[1].name+".png"),
                "avatar3":create_url("Media/images/"+players[2].name+".png"),
                "avatar4":create_url("Media/images/"+players[3].name+".png"),
                "avatar5":create_url("Media/images/"+players[4].name+".png"),
                "hole1":create_url("Media/Cards/"+listHoleCards[0]+".png"),
                "hole2":create_url("Media/Cards/"+listHoleCards[1]+".png"),
                "hole3":create_url("Media/Cards/"+listHoleCards[2]+".png"),
                "hole4":create_url("Media/Cards/"+listHoleCards[3]+".png"),
                "hole5":create_url("Media/Cards/"+listHoleCards[4]+".png"),
                "hole6":create_url("Media/Cards/"+listHoleCards[5]+".png"),
                "hole7":create_url("Media/Cards/"+listHoleCards[6]+".png"),
                "hole8":create_url("Media/Cards/"+listHoleCards[7]+".png"),
                "hole9":create_url("Media/Cards/"+listHoleCards[8]+".png"),
                "hole10":create_url("Media/Cards/"+listHoleCards[9]+".png"),
                "myhole1":create_url("Media/Cards/empty.png"),
                "myhole2":create_url("Media/Cards/empty.png"),
                "flop1":create_url("Media/Cards/"+flopCardsName[0]+".png"),
                "flop2":create_url("Media/Cards/"+flopCardsName[1]+".png"),
                "flop3":create_url("Media/Cards/"+flopCardsName[2]+".png"),
                "turn":create_url("Media/Cards/"+flopCardsName[3]+".png"),
                "river":create_url("Media/Cards/"+flopCardsName[4]+".png"),
                "me":create_url("Media/images/me.png"),
                "bkgd_3":create_url("Media/images/background3.jpg")
            }
        }
    }
    return datasources

def apl_info(speak_output):
    datasources = {
        "headlineTemplateData": {
            "type": "object",
            "objectId": "headlineSample",
            "properties": {
                "textContent": {
                    "scoreText": {
                        "type": "PlainText",
                        "text":  speak_output
                    }
                },
                "imageContent":{
                    "background":create_url("Media/images/background.jpg"),
                    "about":create_url("Media/images/about.png")
                }
            }
        }
    }
    return datasources

def apl_about():
    datasources = {
        "headlineTemplateData": {
            "type": "object",
            "objectId": "headlineSample",
            "properties": {
                "textContent": {
                    "about_1":"Poker is a family of card games with many formulas and variations.",
                    "about_2":"It is practiced with several players with a deck generally of fifty-two cards and tokens representing the sums wagered.",
                    "about":"Poker is a family of card games with many formulas and variations. It is practiced with several players with a deck generally of fifty-two cards and tokens representing the sums wagered."
                },
                "imageContent":{
                    "background":create_url("Media/images/background.jpg"),
                    "about":create_url("Media/images/about.png")
                }
            }
        }
    }
    return datasources

def apl_home(coming_from='launch'):
    if coming_from == 'launch':
        home_1 = "Welcome to"
    else:
        home_1 = "Goodbye.."
    datasources = {
        "headlineTemplateData": {
            "type": "object",
            "objectId": "headlineSample",
            "properties": {
                "textContent": {
                    "home_1": home_1,
                    "home_2":"Smart Poker"
                },
                "imageContent":{
                    "background":create_url("Media/images/background.jpg"),
                    "home_1":create_url("Media/images/poker_PNG96.png"),
                    "home_2":create_url("Media/images/Aion-logo-2.png"),
                    "bckg_2":create_url("Media/images/background2.jpg")
                }
            }
        }
    }
    return datasources
