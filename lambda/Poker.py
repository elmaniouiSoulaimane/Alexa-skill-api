import random
from collections import defaultdict
import itertools

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Player:
    def __init__(self,name,position,holeCards,chips,hand,action,myprice,isFold):
        #nom de joueur
        self.name = name
        #position de joueur
        self.position = position
        #les deux premières cartes 
        self.holeCards = holeCards
        #solde de joueur
        self.chips = chips
        #main de joueur
        self.hand = hand
        self.action = action
        # la somme ajouté par le joueur
        self.myprice = myprice
        #Cet attribut indique si un joueur quitte le jeu ou non
        self.isFold = isFold
    #cette fonction permet de calculer la somme des prix que chaque joueur ajoute
    # on a utiliser cette fonction pour calculer le "Pot" de jeux
    def getPrice(self,players):
        somme = 0
        for player in players:
            somme = somme + player.myprice
        return somme
    # cette fonction pour afficher les actions possible pour le joueur
    def available_actions(self,last_palyer_action,nbrCheck):
        if (last_palyer_action ==  "check" ) or (last_palyer_action == "flop") or (last_palyer_action == "turn") or (last_palyer_action == "river") or (last_palyer_action == "fold" and nbrCheck != 0):
            return ["check","raise","fold"]
        elif (last_palyer_action == "raise") or (last_palyer_action == "fold") or (last_palyer_action == "call") or (last_palyer_action == "bet"):
            return ["raise", "call","fold"]
        else:
            return []
    #cette fonction return l'indice d'un joueur dans la liste
    def getIndexPlayerInPlayers(self,players,player):
        for p in players:
            if player.name == p.name :
                return players.index(p)
    #cette fonction pour rejouer il fait rénisialiser un certaine variables
    def Replay(self,players):
        for player in players:
            #pour rendre tous les joueurs a le jeu
            player.isFold = False
            #supprimer les "hole cards" et aussi le main de joueur
            player.myprice = 0
            player.holeCards.clear()
            #player.hand.clear()
        #changer les positions des joueurs
        players[1].position = "DEALER"
        players[2].position = "SMALL BLIND"
        players[3].position = "BIG BLIND"
        players[4].position = "POSITION 4"
        players[0].position = "POSITION 5"
        l = players[1:]+[players[0]]
        players.clear()
        for e in l:
            players.append(e)
    #cette fonction permet de faire le traitement de "call"
    def Call(self,players,player,infs,small_blind):
        if(infs.last_raise>player.chips):
            return False
        else:
            if(self.getIndexPlayerInPlayers(self,players,player)==1 and infs.call_for_smallBlind == 0):
                #player.chips = player.chips-infs.last_raise+small_blind
                #player.myprice = player.myprice + infs.last_raise-small_blind
                player.chips = player.chips-infs.last_raise+player.myprice
                player.myprice = infs.last_raise
                infs.call_for_smallBlind = 1
            else:
                player.chips = player.chips-infs.last_raise+player.myprice
                player.myprice = infs.last_raise
            return True
    #cette fonction permet de faire le traitement de "Fold"
    def Fold(self,players,player,deck):
        player.isFold = True
        deck.append(player.holeCards[0])
        deck.append(player.holeCards[1])
        player.holeCards.clear()
    ##cette fonction return la liste des joueur encore exist dans le jeux
    def getListOfExistPlayers(self,players):
        existPlayers = []
        for player in players:
            if player.isFold == False:
                existPlayers.append(player)
        return existPlayers
   #cette fonction permet de faire le traitement de "raise"
    def Raise(self,player,valueOfraise,infs):
        #il faut tester si le solde suffisant pour faire le traitement
        if((valueOfraise+infs.last_raise)<=player.chips):
             # et apré on doit rénisialiser les valeurs de "chips:solde de joueur" et la somme ajouté et affecter une nouvel valeur a "last_raise"
            infs.last_raise = infs.last_raise+valueOfraise
            player.chips = 2000 - valueOfraise
            player.myprice = infs.last_raise
            return True
        else:
            return False
    ########################
    ##fonction returne le bon action 
    def getActionOfCurrentPlayer(self,player,flopCards,availableActions):
        action = ""
        x = random.uniform(0,1)
        #si x entre 0.7 et 1 on générer l'action de maniére aléatoie si non on utilise les probabilité
        if(x > 0.7):
            i =  random.randint(0,len(availableActions)-1)
            action = availableActions[i]
        else:
            #si non on va affecter a cards les cartes disponible a chaque joueur
            cards = player.holeCards+flopCards
            #si la taille de la liste est 2 
            if len(cards) == 2:
                l = [cards[0].value,cards[1].value]
                l.sort()
                #si les deux carte ont meme numero ou bien sont con on va faire "raise" si non on va faire "call","check" ou "fold"
                if(l[0] == l[1] or l[0] == l[1]-1):
                    action = "raise"
                else:
                    availableActions.remove("raise")
                    i =  random.randint(0,len(availableActions)-1)
                    action = availableActions[i]
                    availableActions.append("raise")
            #si non on va calculer le best_hand a le joeur et on va calculer le score de ce hand
            else:
                best5Cards = Cards.get_best_hand(Cards,cards)
                score = Cards.score_hand(Cards,best5Cards)[0]
                if(score>50):
                    action = "raise"
                elif (score>5 and score<=50):
                    if 'call' not in availableActions:
                        action = "check"
                    else:
                        action = "call"
                else:
                    if 'check' not in availableActions:
                        action = "fold"
                    else:
                        action = "check"
        return action
    #cette fonction nous permet de gérer l'action d'un joueur 
    def play(self,availableActions,players,player,infs,deck,small_blind,lastsActions,holeCardsName,flopCards):
        #bestAction : c'est le bon action pour le joueur
        bestAction = self.getActionOfCurrentPlayer(self,player,flopCards,availableActions)
        action = ""
        # si l'action est : Fold
        if bestAction == "fold":
            #l'appel a la fonction Fold
            self.Fold(self,players,player,deck)
            #supprimer 'hole Cards' de l'apl de l'application
            holeCardsName[2*players.index(player)]="empty"
            holeCardsName[2*players.index(player)+1]="empty"
            #affecter a l'action de joueur "fold"
            action = "fold"
        #si l'action est 'raise'
        elif bestAction == "raise":
            #fait l'appel a fonction raise
            points_to_raise = random.choice([50,100,150,200])
            var = self.Raise(self, player, points_to_raise, infs)
            #cette fonction returne Vraie si tout se passe bien sinon returne Faux
            # au cas ou Faux le joueur sera quité le jeu
            if var == False:
                self.Fold(self,players,player,deck)
                holeCardsName[2*players.index(player)]="empty"
                holeCardsName[2*players.index(player)+1]="empty"
                action = "fold"
            else:
                infs.nbrCheck = 0
                action = "raise"
        #si l'action est 'call'
        elif bestAction == "call":
            #fait l'appel a fonction call
            var = self.Call(self,players,player,infs,small_blind)
            #cette fonction returne Vraie si tout se passe bien sinon returne Faux
            # au cas ou Faux le joueur sera quité le jeu
            if var == False:
                self.Fold(self,players,player,deck)
                holeCardsName[2*players.index(player)]="empty"
                holeCardsName[2*players.index(player)+1]="empty"
                action = "fold"
            else:
                infs.nbrCheck = 0
                action = "call"
        elif bestAction == "check":
            infs.nbrCheck = infs.nbrCheck+1
            action = "check"
        #lastsActions : C'est la liste contenant l'action de chaque joueur à afficher au joueur principal
        #donc chaque fois on ajoute le nom de joueur et son action a cette liste
        lastsActions.append([player.name,action])
        return action
    ###################""
    # cette fonction returner les informations sur le joueur qu'a gagné si je suis faire "fold"
    def winPlayerIfIfold(self,players,flopCards,deck):
        playersExist = self.getListOfExistPlayers(self,players)
        price = self.getPrice(self,players)
        if (len(flopCards) == 0):
            ThreeflopCards = Cards.flopCards(Cards,deck)
            for i in range(3):
                flopCards.append(ThreeflopCards[i])
            flopCards.append(Cards.getRandomCards(Cards,deck))
            flopCards.append(Cards.getRandomCards(Cards,deck))
        elif (len(flopCards) == 3):
            flopCards.append(Cards.getRandomCards(Cards,deck))
            flopCards.append(Cards.getRandomCards(Cards,deck))
        elif (len(flopCards) == 4):
            flopCards.append(Cards.getRandomCards(Cards,deck))
        for player in playersExist:
            cards = player.holeCards+flopCards
            player.hand = Cards.get_best_hand(Cards,cards)
        theWinPlayer = Cards.getWinOne(Cards,playersExist)
        self.addPricetoPlayer(self,players,theWinPlayer.name,price)
        handType = Cards.score_hand(Cards,theWinPlayer.hand)
        return (theWinPlayer,handType)
    #Cette fonction génère aléatoirement les positions des joueurs dans le tableau
    def roles_players(self,players):
        ord_players = []
        n =  random.randint(0,4)
        if n == 0:
            players[0].position = "DEALER"
            players[1].position = "SMALL BLIND"
            players[2].position = "BIG BLIND"
            players[3].position = "POSITION 4"
            players[4].position = "POSITION 5"
        if n == 1:
            ord_players=[]
            players[1].position = "DEALER"
            ord_players.append(players[1])
            players[2].position = "SMALL BLIND"
            ord_players.append(players[2])
            players[3].position = "BIG BLIND"
            ord_players.append(players[3])
            players[4].position = "POSITION 4"
            ord_players.append(players[4])
            players[0].position = "POSITION 5"
            ord_players.append(players[0])
            players.clear()
            for player in ord_players:
                players.append(player)
        if n == 2:
            ord_players=[]
            players[2].position = "DEALER"
            ord_players.append(players[2])
            players[3].position = "SMALL BLIND"
            ord_players.append(players[3])
            players[4].position = "BIG BLIND"
            ord_players.append(players[4])
            players[0].position = "POSITION 4"
            ord_players.append(players[0])
            players[1].position = "POSITION 5"
            ord_players.append(players[1])
            players.clear()
            for player in ord_players:
                players.append(player)
        if n == 3:
            ord_players=[]
            players[3].position = "DEALER"
            ord_players.append(players[3])
            players[4].position = "SMALL BLIND"
            ord_players.append(players[4])
            players[0].position = "BIG BLIND"
            ord_players.append(players[0])
            players[1].position = "POSITION 4"
            ord_players.append(players[1])
            players[2].position = "POSITION 5"
            ord_players.append(players[2])
            players.clear()
            for player in ord_players:
                players.append(player)
        if n == 4:
            ord_players=[]
            players[4].position = "DEALER"
            ord_players.append(players[4])
            players[0].position = "SMALL BLIND"
            ord_players.append(players[0])
            players[1].position = "BIG BLIND"
            ord_players.append(players[1])
            players[2].position = "POSITION 4"
            ord_players.append(players[2])
            players[3].position = "POSITION 5"
            ord_players.append(players[3])
            players.clear()
            for player in ord_players:
                players.append(player)
    def getMyPosition(self,players):
        for player in players:
            if(player.name == "me"):
                return [player.position,players.index(player)]
    #Cette fonction ajoute un montant au joueur Nous utilisons cette fonction pour ajouter la valeur du prix au joueur gagnant
    def addPricetoPlayer(self,players,name,price):
        for player in players:
            if name == player.name :
                player.chips = player.chips + price
    #Pour tester que tous les utilisateurs ont payé le même montant
    def testAllPrice(self,players):
        prices  = []
        for player in players :
            prices.append(player.myprice)
        #SOULAIMANE---SI TOUS LES JOUEURS AVAIT LE MEME PRIT
        if prices.count(prices[0]) == len(prices):
            logger.info("the prices are the following : {}".format(prices.count(prices[0])))
            return True
        else:
            return False
    #cette fonction retourne l'etape suivant
    #def getNextStep(lisPlayers,cmp_round,nbrCheck):
        
class Cards(object):
    #Chaque carte est représentée par un chiffre et une lettre pour simplifier les chiffres entre (0-12) et les lettres entre (0-3)
    def __init__(self,value,suit):
        self.value = value
        self.suit = suit
    def __repr__(self):
        value_name = ""
        suit_name = ""
        if self.value == 0:
            value_name = "Two"
        if self.value == 1:
            value_name = "Three"
        if self.value == 2:
            value_name = "Four"
        if self.value == 3:
            value_name = "Five"
        if self.value == 4:
            value_name = "Six"
        if self.value == 5:
            value_name = "Seven"
        if self.value == 6:
            value_name = "Eight"
        if self.value == 7:
            value_name = "Nine"
        if self.value == 8:
            value_name = "Ten"
        if self.value == 9:
            value_name = "Jack"
        if self.value == 10:
            value_name = "Queen"
        if self.value == 11:
            value_name = "King"
        if self.value == 12:
            value_name = "Ace"
        if self.suit == 0:
            suit_name = "Diamonds"
        if self.suit == 1:
            suit_name = "Clubs"
        if self.suit == 2:
            suit_name = "Hearts"
        if self.suit == 3:
            suit_name = "Spades"
        return value_name + " of " + suit_name
    ## Cette fonction attribue à chaque joueur les deux premières cartes face cachée(Hole Cards)
    def HoleCards(self,deck,players):
        deck.shuffle()
        for player in players:
            for i in range(2):
                player.holeCards.append(deck[i])
                deck.remove(deck[i])
    def flopCards(self,deck):
        deck.shuffle()
        flops = []
        for i in range(3):
            flops.append(deck[i])
            deck.remove(deck[i])
        return flops
    #returne une carte aleatoire
    def getRandomCards(self,deck):
        deck.shuffle()
        card = deck[0]
        deck.remove(deck[0])
        return card
    """
    I give scores from 0 to 135. This is so because there are 10 different types of hands in Poker and 14 different numbers in every suit, so the scores go like this:
    Hand Type → Score
    High card → 0 to 14
    Pair → 15 to 29
    Two Pair → 30 to 44
    3 of a Kind → 45 to 59
    Straight → 60 to 74
    Flush → 75 to 89
    Full House → 90 to 104
    Four of a Kind → 105 to 1
    Straight Flush →120 to 134
    Royal Flush →135
    """
    def check_four_of_a_kind(self,hand):
        values = [i.value for i in hand]
        for i in values:
            if values.count(i) == 4:
                four = i
            elif values.count(i) == 1:
                card = i
        score = 105 + four + card/100
        return score

    def check_full_house(self,hand):
        values = [i.value for i in hand]
        for i in values:
            if values.count(i) == 3:
                full = i
            elif values.count(i) == 2:
                p = i
        score = 90 + full + p/100  
        return score

    def check_three_of_a_kind(self,hand):
        values = [i.value for i in hand]
        cards = []
        for i in values:
            if values.count(i) == 3:
                three = i
            else: 
                cards.append(i)
        score = 45 + three + max(cards) + min(cards)/1000
        return score

    def check_two_pair(self,hand):
        values = [i.value for i in hand]
        pairs = []
        cards = []
        for i in values:
            if values.count(i) == 2:
                pairs.append(i)
            elif values.count(i) == 1:
                cards.append(i)
                cards = sorted(cards,reverse=True)
        score = 30 + max(pairs) + min(pairs)/100 + cards[0]/1000
        return score
    #check pair with score (0<score<135)
    def check_pair(self,hand):    
        values = [i.value for i in hand]
        pair = []
        cards  = []
        for i in values:
            if values.count(i) == 2:
                pair.append(i)
            elif values.count(i) == 1:    
                cards.append(i)
                cards = sorted(cards,reverse=True)
        score = 15 + pair[0] + cards[0]/100 + cards[1]/1000 + cards[2]/10000
        return score
    #evalute hand 
    def score_hand(self,hand):
        letters = [h.suit for h in hand] # We get the suit for each card in the hand
        numbers = [card.value for card in hand]  # We get the number for each card in the hand
        rnum = [numbers.count(i) for i in numbers]  # We count repetitions for each number
        rlet = [letters.count(i) for i in letters]  # We count repetitions for each letter
        dif = max(numbers) - min(numbers) # The difference between the greater and smaller number in the hand
        handtype = ''
        score = 0
        if 5 in rlet:
            if sorted(numbers) ==[8,9,10,11,12]:
                handtype = 'royal_flush'
                score = 135
            elif dif == 4 and max(rnum) == 1:
                handtype = 'straight_flush'
                score = 120 + max(numbers)
            elif 4 in rnum:
                handtype = 'four of a kind'
                score = self.check_four_of_a_kind(self,hand)
            elif sorted(rnum) == [2,2,3,3,3]:
                handtype = 'full house'
                score = self.check_full_house(self,hand)
            elif 3 in rnum:
                handtype = 'three of a kind'
                score = self.check_three_of_a_kind(self,hand)
            elif rnum.count(2) == 4:
                handtype = 'two pair'
                score = self.check_two_pair(self,hand)
            elif rnum.count(2) == 2:
                handtype = 'pair'
                score = self.check_pair(self,hand)
            else:
                handtype = 'flush'
                score = 75 + max(numbers)/100
        elif 4 in rnum:
            handtype = 'four of a kind'
            score = self.check_four_of_a_kind(self,hand)
        elif sorted(rnum) == [2,2,3,3,3]:
            handtype = 'full house'
            score = self.check_full_house(self,hand)
        elif 3 in rnum:
            handtype = 'three of a kind' 
            score = self.check_three_of_a_kind(self,hand)
        elif rnum.count(2) == 4:
            handtype = 'two pair'
            score = self.check_two_pair(self,hand)
        elif rnum.count(2) == 2:
            handtype = 'pair'
            score = self.check_pair(self,hand)
        elif dif == 4:
            handtype = 'straight'
            score = 65 + max(numbers)
        else:
            handtype= 'high card'
            n = sorted(numbers,reverse=True)
            score = n[0] + n[1]/100 + n[2]/1000 + n[3]/10000 + n[4]/100000
        return [score,handtype]
    #get best hand 
    def get_best_hand(self,cards):
        max = cards[:5]
        for hand in list(itertools.combinations(cards,5)):
            if(self.score_hand(self,hand)[0]>self.score_hand(self,max)[0]):
                max = hand
        return max
    #get best hand of all hands
    def getWinOne(self,players):
        win = players[0]
        for player in players:
            if(self.score_hand(self,player.hand)[0]>self.score_hand(self,win.hand)[0]):
                win = player
        return win

class StandarDeck(list):
    #génération de carte
    def __init__(self):
        super().__init__()
        suits = list(range(4))
        values = list(range(13))
        [[self.append(Cards(i,j)) for j in suits]for i in values]
    #mélanger les cartes
    def shuffle(self):
        random.shuffle(self)