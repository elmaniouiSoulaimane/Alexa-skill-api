import logging
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.utils import get_supported_interfaces
from ask_sdk_model.interfaces.alexa.presentation.apl import RenderDocumentDirective

import json
import random
from Inf import Informations
from Poker import Player, Cards, StandarDeck
from utils import (getInfNextStep, toString, _load_apl_document, create_url, update_actions,
    update_actions_multi, current_situation)
from apl_helpers import apl_current, apl_current_win, apl_info, apl_about, apl_home
from ask_sdk.standard import StandardSkillBuilder
from ask_sdk_model import Response

from interfaces import interfaces
interfaces = interfaces()
sb = StandardSkillBuilder()

players = []
deck = []
flopCards = []
lastsActions = []
flopCardsName = ["empty"]*5
holeCardsName = ["default"]*10
myindex = 0
small_blind = 2
big_blind = 4
infs = Informations(4,0,0,0)
INIT_CHIPS = 2000

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        logger.info("In LaunchRequestHandler")
        speak_output = "Welcome to the Texas holdem poker game. Say 'ready' to start playing, or 'About Poker' if you want know more about the game. "
        sessionAttributes = handler_input.attributes_manager.session_attributes
        sessionAttributes["state"] = "default"
        sessionAttributes["lastaction"] = None
        sessionAttributes["last_output"] = "Say 'ready' to start playing. "
        
        interfaces.displayContent(handler_input)
        '''if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:
            handler_input.response_builder.add_directive(
                RenderDocumentDirective(
                    token="homeToken",
                    document=_load_apl_document("./templates/home.json"),
                    datasources = apl_home()
                )
            )'''
        handler_input.response_builder.set_should_end_session(False)
        return handler_input.response_builder.speak(speak_output).ask(speak_output).response


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        logger.info("In HelpIntentHandler")
        return AboutUsIntentHandler().handle(handler_input)


class PerflopIntentHandler(AbstractRequestHandler):
    """Code for preflop"""
    def can_handle(self,handler_input):
        return ask_utils.is_intent_name("PerflopIntent")(handler_input)
        
    def handle(self,handler_input):
        logger.info("In PerflopIntentHandler")
        sessionAttributes = handler_input.attributes_manager.session_attributes
        myState = sessionAttributes["state"]
        if myState == "default":
            sessionAttributes["state"] = "preflop"
            global players, deck, myindex, lastsActions, holeCardsName, flopCardsName, flopCards, infs
            players = [Player('Evan','',[],INIT_CHIPS,[],None,0,False),
                        Player('Tom','',[],INIT_CHIPS,[],None,0,False), 
                        Player('Sarah','',[],INIT_CHIPS,[],None,0,False), 
                        Player('Lucy','',[],INIT_CHIPS,[],None,0,False), 
                        Player('me','',[],INIT_CHIPS,[],None,0,False)]
            flopCardsName = ["empty"]*5
            holeCardsName = ["default"]*10
            flopCards.clear()
            infs = Informations(4,0,0,0)
            Player.roles_players(Player,players)
            logger.info(f"CHECKPOINT INFO: p0: {players[0].name}, p1: {players[1].name}, p2: {players[2].name}, p3: {players[3].name}, p4: {players[4].name}.")
            sessionAttributes["p_actions"] = [[players[0].name, ""], [players[1].name, ""], [players[2].name, ""], [players[3].name, ""], [players[4].name, ""]]#
            deck = StandarDeck()
            Cards.HoleCards(Cards,deck,players)
            myInf = Player.getMyPosition(Player,players)
            myindex = myInf[1]
            players[1].chips = players[1].chips-small_blind
            players[1].myprice = small_blind
            players[2].myprice = big_blind
            players[2].chips = players[2].chips-big_blind
            infs.last_raise = big_blind
            sessionAttributes["lastaction"] = "bet"
            availableActions = Player.available_actions(Player, sessionAttributes["lastaction"], infs.nbrCheck)
            lastsActions.clear()
            lastsActions.append([players[1].name,"bet"])
            lastsActions.append([players[2].name,"bet"])
            if myindex == 0:
                for player in players[3:]:
                    sessionAttributes["lastaction"] = Player.play(Player,availableActions,players,player,infs,deck,small_blind,lastsActions,holeCardsName,flopCards)
                    availableActions = Player.available_actions(Player,sessionAttributes["lastaction"],infs.nbrCheck)
                logger.info(f"getting last action {sessionAttributes['lastaction']}")
            elif myindex == 1:
                for player in players[3:]:
                    sessionAttributes["lastaction"] = Player.play(Player,availableActions,players,player,infs,deck,small_blind,lastsActions,holeCardsName,flopCards)
                    availableActions = Player.available_actions(Player,sessionAttributes["lastaction"],infs.nbrCheck)
                if players[1].isFold == False:
                    sessionAttributes["lastaction"] = Player.play(Player,availableActions,players,players[0],infs,deck,small_blind,lastsActions,holeCardsName,flopCards)
                
                logger.info(f"getting last action {sessionAttributes['lastaction']}")
            elif myindex == 2 :
                if lastsActions[0][0] == "me":
                    lastsActions.clear()
                for player in players[3:]:
                    sessionAttributes["lastaction"] = Player.play(Player,availableActions,players,player,infs,deck,small_blind,lastsActions,holeCardsName,flopCards)
                    availableActions = Player.available_actions(Player,sessionAttributes["lastaction"],infs.nbrCheck)
                for player in players[:2]:
                    sessionAttributes["lastaction"] = Player.play(Player,availableActions,players,player,infs,deck,small_blind,lastsActions,holeCardsName,flopCards)
                    availableActions = Player.available_actions(Player,sessionAttributes["lastaction"],infs.nbrCheck)
                listPlayers  = Player.getListOfExistPlayers(Player,players)
                infNextStep = getInfNextStep(listPlayers,infs)
                if len(infNextStep) != 0:
                    ########################----BUG FIXED----########################
                    #####NOT DISPLAYING THE PLAYERS ACTION WHEN ALL THE PLAYERS HAVE THE SAME BETTING AMOUNT
                    #####speak_output= infNextStep[0]
                    #####SOULAIMANE----THE FOLLOWING OUTPUT FIXES THE PROBLEM
                    listPlayers  = Player.getListOfExistPlayers(Player,players)
                    playersActions = toString(lastsActions, infs,listPlayers)
                    speak_output = f"{playersActions} {infNextStep[0]}"
                    #################################################################
                    sessionAttributes["state"] = infNextStep[1]
                logger.info(f"getting last action {sessionAttributes['lastaction']}")
            elif myindex == 4 :
                sessionAttributes["lastaction"] = Player.play(Player,availableActions,players,players[3],infs,deck,small_blind,lastsActions,holeCardsName,flopCards)
                logger.info(f"finally in 4")
            #SOULAIMANE------POSSIBLE USELESS CONDITION SINCE 
            if sessionAttributes["state"] == "preflop":
                availableActions = Player.available_actions(Player,sessionAttributes["lastaction"],infs.nbrCheck)
                listPlayers  = Player.getListOfExistPlayers(Player,players)
                playersActions = toString(lastsActions, infs,listPlayers)
                speak_output=f"{playersActions}  Your available actions are {availableActions[0]}, {availableActions[1]}, and {availableActions[2]}. "
            potValue =  Player.getPrice(Player,players)
            #SOULAIMANE------I DON'T UNDERSAND THE FOLLOWING OPERATION ON LINE 145
            myHoleIndex = 2*myindex + 1 
            if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:
                handler_input.response_builder.add_directive(
                    RenderDocumentDirective(
                        token="indexToken",
                        document=_load_apl_document("./templates/index.json"),
                        datasources = apl_current(potValue, players, holeCardsName, myindex, myHoleIndex, flopCardsName)
                    )
                )
            sessionAttributes["last_output"] = speak_output
        else:   
            speak_output="This is an invalid action. "
            sessionAttributes["last_output"] = ""
        handler_input.response_builder.speak(speak_output).set_should_end_session(False)
        return handler_input.response_builder.response

class AboutUsIntentHandler(AbstractRequestHandler):
    """Information about the game"""
    def can_handle(self,handler_input):
        return ask_utils.is_intent_name("AboutUsIntent")(handler_input)
    
    def handle(self,handler_input):
        logger.info("In AboutUsIntentHandler")
        sessionAttributes = handler_input.attributes_manager.session_attributes
        speak_output = "Poker is a family of card games with many formulas and variations. It is practiced with several players with a deck generally of fifty-two cards and tokens representing the sums wagered. "
        if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:
            handler_input.response_builder.add_directive(
                RenderDocumentDirective(
                    token="aboutToken",
                    document=_load_apl_document("./templates/aboutUs.json"),
                    datasources = apl_about()
                )
            )
        speak_output += sessionAttributes["last_output"]
        handler_input.response_builder.set_should_end_session(False)
        return handler_input.response_builder.speak(speak_output).ask(speak_output).response

class CallIntentHandler(AbstractRequestHandler):
    """Call intent handler"""
    def can_handle(self,handler_input):
        return ask_utils.is_intent_name("CallIntent")(handler_input)
    
    def handle(self,handler_input):
        logger.info("In CallIntentHandler")
        global deck, lastsActions, holeCardsName, infs, players
        #logger.info(f"CHECKPOINT first: lastsActions {lastsActions}")
        sessionAttributes = handler_input.attributes_manager.session_attributes
        sessionAttributes["p_actions"] = update_actions_multi(lastsActions, sessionAttributes["p_actions"])#############
        availableActions = Player.available_actions(Player, sessionAttributes["lastaction"], infs.nbrCheck)
        if "call" in availableActions:
            if(infs.last_raise<players[myindex].chips):
                if(myindex == 1 and infs.call_for_smallBlind == 0):
                    players[myindex].chips = players[myindex].chips - infs.last_raise+players[myindex].myprice
                    players[myindex].myprice = infs.last_raise
                    infs.call_for_smallBlind = 1
                else:
                    players[myindex].chips = players[myindex].chips - infs.last_raise+players[myindex].myprice
                    players[myindex].myprice = infs.last_raise
                sessionAttributes["lastaction"] = "call"
                sessionAttributes["p_actions"] = update_actions("me", "call", sessionAttributes["p_actions"])####
                lastsActions.clear()
                infs.nbrCheck = 0
                
                listPlayers  = Player.getListOfExistPlayers(Player,players)
                infNextStep = getInfNextStep(listPlayers,infs)
                logger.info(f"next iiiss = {infNextStep}")
                if len(infNextStep) != 0:
                    ## if ready to next round 
                    ########################----BUG FIXED----########################
                    #####NOT DISPLAYING THE PLAYERS ACTION WHEN ALL THE PLAYERS HAVE THE SAME BETTING AMOUNT
                    #####speak_output= infNextStep[0]
                    #####SOULAIMANE----THE FOLLOWING OUTPUT FIXES THE PROBLEM
                    listPlayers  = Player.getListOfExistPlayers(Player,players)
                    playersActions = toString(lastsActions, infs,listPlayers)
                    speak_output = f"{playersActions} {infNextStep[0]}"
                    #################################################################
                    sessionAttributes["state"] = infNextStep[1]
                else:
                    myState = sessionAttributes["state"]
                    availableActions = Player.available_actions(Player, sessionAttributes["lastaction"], infs.nbrCheck)
                    if myindex == 0:
                        for player in players[1:]:
                            if player.isFold == False:
                                sessionAttributes["lastaction"] = Player.play(Player,availableActions,players,player,infs,deck,small_blind,lastsActions,holeCardsName,flopCards)
                                sessionAttributes["p_actions"] = update_actions(player.name, sessionAttributes["lastaction"], sessionAttributes["p_actions"])####
                                logger.info(f"CHECKPOINT Y: p_actions {sessionAttributes['p_actions']}")####
                                availableActions = Player.available_actions(Player,sessionAttributes["lastaction"],infs.nbrCheck)
                            listPlayers  = Player.getListOfExistPlayers(Player,players)
                            infNextStep = getInfNextStep(listPlayers,infs)
                            if len(infNextStep) != 0:
                                ########################----BUG FIXED----########################
                                #####NOT DISPLAYING THE PLAYERS ACTION WHEN ALL THE PLAYERS HAVE THE SAME BETTING AMOUNT
                                #####speak_output= infNextStep[0]
                                #####SOULAIMANE----THE FOLLOWING OUTPUT FIXES THE PROBLEM
                                listPlayers  = Player.getListOfExistPlayers(Player,players)
                                playersActions = toString(lastsActions, infs,listPlayers)
                                speak_output = f"{playersActions} {infNextStep[0]}"
                                #################################################################
                                sessionAttributes["state"] = infNextStep[1]
                                break
                    elif myindex == 1:
                        var = True
                        for player in players[2:]:
                            if player.isFold == False:
                                sessionAttributes["lastaction"] = Player.play(Player,availableActions,players,player,infs,deck,small_blind,lastsActions,holeCardsName,flopCards)
                                sessionAttributes["p_actions"] = update_actions(player.name, sessionAttributes["lastaction"], sessionAttributes["p_actions"])####
                                logger.info(f"CHECKPOINT Y: p_actions {sessionAttributes['p_actions']}")####
                                availableActions = Player.available_actions(Player,sessionAttributes["lastaction"],infs.nbrCheck)
                            listPlayers  = Player.getListOfExistPlayers(Player,players)
                            infNextStep = getInfNextStep(listPlayers,infs)
                            if len(infNextStep) != 0:
                                ########################----BUG FIXED----########################
                                #####NOT DISPLAYING THE PLAYERS ACTION WHEN ALL THE PLAYERS HAVE THE SAME BETTING AMOUNT
                                #####speak_output= infNextStep[0]
                                #####SOULAIMANE----THE FOLLOWING OUTPUT FIXES THE PROBLEM
                                listPlayers  = Player.getListOfExistPlayers(Player,players)
                                playersActions = toString(lastsActions, infs,listPlayers)
                                speak_output = f"{playersActions} {infNextStep[0]}"
                                #################################################################
                                sessionAttributes["state"] = infNextStep[1]
                                var = False
                                break
                        if (var):
                            if players[0].isFold == False:
                                sessionAttributes["lastaction"] = Player.play(Player,availableActions,players,players[0],infs,deck,small_blind,lastsActions,holeCardsName,flopCards)
                                sessionAttributes["p_actions"] = update_actions(players[0], sessionAttributes["lastaction"], sessionAttributes["p_actions"])####
                                logger.info(f"CHECKPOINT Y: p_actions {sessionAttributes['p_actions']}")####
                            listPlayers  = Player.getListOfExistPlayers(Player,players)
                            infNextStep = getInfNextStep(listPlayers,infs)
                            if len(infNextStep) != 0:
                                ########################----BUG FIXED----########################
                                #####NOT DISPLAYING THE PLAYERS ACTION WHEN ALL THE PLAYERS HAVE THE SAME BETTING AMOUNT
                                #####speak_output= infNextStep[0]
                                #####SOULAIMANE----THE FOLLOWING OUTPUT FIXES THE PROBLEM
                                listPlayers  = Player.getListOfExistPlayers(Player,players)
                                playersActions = toString(lastsActions, infs,listPlayers)
                                speak_output = f"{playersActions} {infNextStep[0]}"
                                #################################################################
                                sessionAttributes["state"] = infNextStep[1]
                    elif myindex == 2 :
                        var = True
                        for player in players[3:]:
                            if player.isFold == False:
                                sessionAttributes["lastaction"] = Player.play(Player,availableActions,players,player,infs,deck,small_blind,lastsActions,holeCardsName,flopCards)
                                sessionAttributes["p_actions"] = update_actions(player.name, sessionAttributes["lastaction"], sessionAttributes["p_actions"])####
                                logger.info(f"CHECKPOINT Y: p_actions {sessionAttributes['p_actions']}")####
                                availableActions = Player.available_actions(Player,sessionAttributes["lastaction"],infs.nbrCheck)
                            listPlayers  = Player.getListOfExistPlayers(Player,players)
                            infNextStep = getInfNextStep(listPlayers,infs)
                            if len(infNextStep) != 0:
                                ########################----BUG FIXED----########################
                                #####NOT DISPLAYING THE PLAYERS ACTION WHEN ALL THE PLAYERS HAVE THE SAME BETTING AMOUNT
                                #####speak_output= infNextStep[0]
                                #####SOULAIMANE----THE FOLLOWING OUTPUT FIXES THE PROBLEM
                                listPlayers  = Player.getListOfExistPlayers(Player,players)
                                playersActions = toString(lastsActions, infs,listPlayers)
                                speak_output = f"{playersActions} {infNextStep[0]}"
                                #################################################################
                                sessionAttributes["state"] = infNextStep[1]
                                var = False
                                break
                        if (var):
                            for player in players[:2]:
                                if player.isFold == False:
                                    sessionAttributes["lastaction"] = Player.play(Player,availableActions,players,player,infs,deck,small_blind,lastsActions,holeCardsName,flopCards)
                                    sessionAttributes["p_actions"] = update_actions(player.name, sessionAttributes["lastaction"], sessionAttributes["p_actions"])####
                                    logger.info(f"CHECKPOINT Y: p_actions {sessionAttributes['p_actions']}")####
                                    availableActions = Player.available_actions(Player,sessionAttributes["lastaction"],infs.nbrCheck)
                                listPlayers  = Player.getListOfExistPlayers(Player,players)
                                infNextStep = getInfNextStep(listPlayers,infs)
                                if len(infNextStep) != 0:
                                    ########################----BUG FIXED----########################
                                    #####NOT DISPLAYING THE PLAYERS ACTION WHEN ALL THE PLAYERS HAVE THE SAME BETTING AMOUNT
                                    #####speak_output= infNextStep[0]
                                    #####SOULAIMANE----THE FOLLOWING OUTPUT FIXES THE PROBLEM
                                    listPlayers  = Player.getListOfExistPlayers(Player,players)
                                    playersActions = toString(lastsActions, infs,listPlayers)
                                    speak_output = f"{playersActions} {infNextStep[0]}"
                                    #################################################################
                                    sessionAttributes["state"] = infNextStep[1]
                                    break
                    elif myindex == 3 :
                        var = True
                        if players[4].isFold == False:
                            sessionAttributes["lastaction"] = Player.play(Player,availableActions,players,players[4],infs,deck,small_blind,lastsActions,holeCardsName,flopCards)
                            sessionAttributes["p_actions"] = update_actions(players[4], sessionAttributes["lastaction"], sessionAttributes["p_actions"])####
                            logger.info(f"CHECKPOINT Y: p_actions {sessionAttributes['p_actions']}")####
                            availableActions = Player.available_actions(Player,sessionAttributes["lastaction"],infs.nbrCheck)
                        listPlayers  = Player.getListOfExistPlayers(Player,players)
                        infNextStep = getInfNextStep(listPlayers,infs)
                        if len(infNextStep) != 0:
                            ########################----BUG FIXED----########################
                            #####NOT DISPLAYING THE PLAYERS ACTION WHEN ALL THE PLAYERS HAVE THE SAME BETTING AMOUNT
                            #####speak_output= infNextStep[0]
                            #####SOULAIMANE----THE FOLLOWING OUTPUT FIXES THE PROBLEM   
                            listPlayers  = Player.getListOfExistPlayers(Player,players)
                            playersActions = toString(lastsActions, infs,listPlayers)
                            speak_output = f"{playersActions} {infNextStep[0]}"
                            #################################################################
                            sessionAttributes["state"] = infNextStep[1]
                            var = False
                        if(var):
                            for player in players[:3]:
                                if player.isFold == False:
                                    sessionAttributes["lastaction"] = Player.play(Player,availableActions,players,player,infs,deck,small_blind,lastsActions,holeCardsName,flopCards)
                                    sessionAttributes["p_actions"] = update_actions(player.name, sessionAttributes["lastaction"], sessionAttributes["p_actions"])####
                                    logger.info(f"CHECKPOINT Y: p_actions {sessionAttributes['p_actions']}")####
                                    availableActions = Player.available_actions(Player,sessionAttributes["lastaction"],infs.nbrCheck)
                                listPlayers  = Player.getListOfExistPlayers(Player,players)
                                infNextStep = getInfNextStep(listPlayers,infs)
                                if len(infNextStep) != 0:
                                    ########################----BUG FIXED----########################
                                    #####NOT DISPLAYING THE PLAYERS ACTION WHEN ALL THE PLAYERS HAVE THE SAME BETTING AMOUNT
                                    #####speak_output= infNextStep[0]
                                    #####SOULAIMANE----THE FOLLOWING OUTPUT FIXES THE PROBLEM
                                    listPlayers  = Player.getListOfExistPlayers(Player,players)
                                    playersActions = toString(lastsActions, infs,listPlayers)
                                    speak_output = f"{playersActions} {infNextStep[0]}"
                                    #################################################################
                                    sessionAttributes["state"] = infNextStep[1]
                                    break
                    elif myindex == 4 :
                        for player in players[:4]:
                            if player.isFold == False:
                                sessionAttributes["lastaction"] = Player.play(Player,availableActions,players,player,infs,deck,small_blind,lastsActions,holeCardsName,flopCards)
                                sessionAttributes["p_actions"] = update_actions(player.name, sessionAttributes["lastaction"], sessionAttributes["p_actions"])####
                                logger.info(f"CHECKPOINT Y: p_actions {sessionAttributes['p_actions']}")####
                                availableActions = Player.available_actions(Player,sessionAttributes["lastaction"],infs.nbrCheck)
                            listPlayers  = Player.getListOfExistPlayers(Player,players)
                            infNextStep = getInfNextStep(listPlayers,infs)
                            if len(infNextStep) != 0:
                                ########################----BUG FIXED----########################
                                #####NOT DISPLAYING THE PLAYERS ACTION WHEN ALL THE PLAYERS HAVE THE SAME BETTING AMOUNT
                                #####speak_output= infNextStep[0]
                                #####SOULAIMANE----THE FOLLOWING OUTPUT FIXES THE PROBLEM
                                listPlayers  = Player.getListOfExistPlayers(Player,players)
                                playersActions = toString(lastsActions, infs,listPlayers)
                                speak_output = f"{playersActions} {infNextStep[0]}"
                                #################################################################
                                sessionAttributes["state"] = infNextStep[1]
                                break
                    if sessionAttributes["state"] == myState:
                        availableActions = Player.available_actions(Player,sessionAttributes["lastaction"],infs.nbrCheck)
                        listPlayers  = Player.getListOfExistPlayers(Player,players)
                        lastPlayersActions = toString(lastsActions, infs,listPlayers)
                        speak_output=f"{lastPlayersActions}  Your available actions are {availableActions[0]}, {availableActions[1]}, and {availableActions[2]}. "
                
                potValue =  Player.getPrice(Player,players)
                myHoleIndex = 2*myindex + 1 
                if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:
                    handler_input.response_builder.add_directive(
                        RenderDocumentDirective(
                            token="indexToken",
                            document=_load_apl_document("./templates/index.json"),
                            datasources = apl_current(potValue, players, holeCardsName, myindex, myHoleIndex, flopCardsName)
                        )
                    )
                sessionAttributes["last_output"] = speak_output
            else:
                players[myindex].isFold = True
                deck.append(players[myindex].holeCards[0])
                deck.append(players[myindex].holeCards[1])
                players[myindex].holeCards.clear()
                speak_output = "Your balance is insufficient. Say ready to restart. "
                sessionAttributes["state"] = "default"
                sessionAttributes["lastaction"] = None
                sessionAttributes["last_output"] = "Say ready to restart. "
                if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:
                    handler_input.response_builder.add_directive(
                        RenderDocumentDirective(
                            token="homeToken",
                            document=_load_apl_document("./templates/home.json"),
                            datasources = apl_home("call")
                        )
                    )
        else:
            speak_output = "This is an invalid action. "
            sessionAttributes["last_output"] = ""
        handler_input.response_builder.speak(speak_output).set_should_end_session(False)
        return handler_input.response_builder.response


class RaiseIntentHandler(AbstractRequestHandler):
    """Raise intent handler"""
    def can_handle(self,handler_input):
        return ask_utils.is_intent_name("RaiseIntent")(handler_input)
    
    def handle(self,handler_input):
        logger.info("In RaiseIntentHandler")
        sessionAttributes = handler_input.attributes_manager.session_attributes
        global infs, lastsActions, holeCardsName, deck, players
        myState = sessionAttributes["state"]
        sessionAttributes["p_actions"] = update_actions_multi(lastsActions, sessionAttributes["p_actions"])#############*
        if myState != "default":
            slots = handler_input.request_envelope.request.intent.slots
            raiseValue = slots["raiseValue"].value
            
            if (int(raiseValue)+infs.last_raise > players[myindex].chips):#################
                speak_output = "You don't have enough money! Please try again. "
            elif(int(raiseValue)%50 != 0):
                speak_output = "Please raise a multile of 50. "

            else:
                infs.last_raise += int(raiseValue)#####
                players[myindex].myprice = infs.last_raise ######
                players[myindex].chips = 2000 - players[myindex].myprice####
                sessionAttributes["lastaction"] = "raise"
                lastsActions.clear()
                infs.nbrCheck = 0

                listPlayers = Player.getListOfExistPlayers(Player,players)
                infNextStep = getInfNextStep(listPlayers,infs)
                if len(infNextStep) != 0:
                    ########################----BUG FIXED----########################
                    #####NOT DISPLAYING THE PLAYERS ACTION WHEN ALL THE PLAYERS HAVE THE SAME BETTING AMOUNT
                    #####speak_output= infNextStep[0]
                    #####SOULAIMANE----THE FOLLOWING OUTPUT FIXES THE PROBLEM
                    listPlayers  = Player.getListOfExistPlayers(Player,players)
                    playersActions = toString(lastsActions, infs,listPlayers)
                    speak_output = f"{playersActions} {infNextStep[0]}"
                    #################################################################
                    sessionAttributes["state"] = infNextStep[1]
                else:
                    myState = sessionAttributes["state"]
                    availableActions = Player.available_actions(Player,sessionAttributes["lastaction"],infs.nbrCheck)
                    if myindex == 0:
                        for player in players[1:]:
                            if player.isFold == False:
                                sessionAttributes["lastaction"] = Player.play(Player,availableActions,players,player,infs,deck,small_blind,lastsActions,holeCardsName,flopCards)
                                sessionAttributes["p_actions"] = update_actions(player.name, sessionAttributes["lastaction"], sessionAttributes["p_actions"])####
                                availableActions = Player.available_actions(Player,sessionAttributes["lastaction"],infs.nbrCheck)
                            listPlayers  = Player.getListOfExistPlayers(Player,players)
                            infNextStep = getInfNextStep(listPlayers,infs)
                            if len(infNextStep) != 0:
                                ########################----BUG FIXED----########################
                                #####NOT DISPLAYING THE PLAYERS ACTION WHEN ALL THE PLAYERS HAVE THE SAME BETTING AMOUNT
                                #####speak_output= infNextStep[0]
                                #####SOULAIMANE----THE FOLLOWING OUTPUT FIXES THE PROBLEM
                                listPlayers  = Player.getListOfExistPlayers(Player,players)
                                playersActions = toString(lastsActions, infs,listPlayers)
                                speak_output = f"{playersActions} {infNextStep[0]}"
                                #################################################################
                                sessionAttributes["state"] = infNextStep[1]
                                break
                    elif myindex == 1:
                        var = True
                        for player in players[2:]:
                            if player.isFold == False:
                                sessionAttributes["lastaction"] = Player.play(Player,availableActions,players,player,infs,deck,small_blind,lastsActions,holeCardsName,flopCards)
                                sessionAttributes["p_actions"] = update_actions(player.name, sessionAttributes["lastaction"], sessionAttributes["p_actions"])####
                                availableActions = Player.available_actions(Player,sessionAttributes["lastaction"],infs.nbrCheck)
                            listPlayers  = Player.getListOfExistPlayers(Player,players)
                            infNextStep = getInfNextStep(listPlayers,infs)
                            if len(infNextStep) != 0:
                                ########################----BUG FIXED----########################
                                #####NOT DISPLAYING THE PLAYERS ACTION WHEN ALL THE PLAYERS HAVE THE SAME BETTING AMOUNT
                                #####speak_output= infNextStep[0]
                                #####SOULAIMANE----THE FOLLOWING OUTPUT FIXES THE PROBLEM
                                listPlayers  = Player.getListOfExistPlayers(Player,players)
                                playersActions = toString(lastsActions, infs,listPlayers)
                                speak_output = f"{playersActions} {infNextStep[0]}"
                                #################################################################
                                sessionAttributes["state"] = infNextStep[1]
                                var = False
                                break
                        if (var):
                            if players[0].isFold == False:
                                sessionAttributes["lastaction"] = Player.play(Player,availableActions,players,players[0],infs,deck,small_blind,lastsActions,holeCardsName,flopCards)
                                sessionAttributes["p_actions"] = update_actions(players[0], sessionAttributes["lastaction"], sessionAttributes["p_actions"])####
                            listPlayers  = Player.getListOfExistPlayers(Player,players)
                            infNextStep = getInfNextStep(listPlayers,infs)
                            if len(infNextStep) != 0:
                                ########################----BUG FIXED----########################
                                #####NOT DISPLAYING THE PLAYERS ACTION WHEN ALL THE PLAYERS HAVE THE SAME BETTING AMOUNT
                                #####speak_output= infNextStep[0]
                                #####SOULAIMANE----THE FOLLOWING OUTPUT FIXES THE PROBLEM
                                listPlayers  = Player.getListOfExistPlayers(Player,players)
                                playersActions = toString(lastsActions, infs,listPlayers)
                                speak_output = f"{playersActions} {infNextStep[0]}"
                                #################################################################
                                sessionAttributes["state"] = infNextStep[1]
                    elif myindex == 2 :
                        var = True
                        for player in players[3:]:
                            if player.isFold == False:
                                sessionAttributes["lastaction"] = Player.play(Player,availableActions,players,player,infs,deck,small_blind,lastsActions,holeCardsName,flopCards)
                                sessionAttributes["p_actions"] = update_actions(player.name, sessionAttributes["lastaction"], sessionAttributes["p_actions"])####
                                availableActions = Player.available_actions(Player,sessionAttributes["lastaction"],infs.nbrCheck)
                            listPlayers  = Player.getListOfExistPlayers(Player,players)
                            infNextStep = getInfNextStep(listPlayers,infs)
                            if len(infNextStep) != 0:
                                ########################----BUG FIXED----########################
                                #####NOT DISPLAYING THE PLAYERS ACTION WHEN ALL THE PLAYERS HAVE THE SAME BETTING AMOUNT
                                #####speak_output= infNextStep[0]
                                #####SOULAIMANE----THE FOLLOWING OUTPUT FIXES THE PROBLEM
                                listPlayers  = Player.getListOfExistPlayers(Player,players)
                                playersActions = toString(lastsActions, infs,listPlayers)
                                speak_output = f"{playersActions} {infNextStep[0]}"
                                #################################################################
                                sessionAttributes["state"] = infNextStep[1]
                                var = False
                                break
                        if (var):
                            for player in players[:2]:
                                if player.isFold == False:
                                    sessionAttributes["lastaction"] = Player.play(Player,availableActions,players,player,infs,deck,small_blind,lastsActions,holeCardsName,flopCards)
                                    sessionAttributes["p_actions"] = update_actions(player.name, sessionAttributes["lastaction"], sessionAttributes["p_actions"])####
                                    availableActions = Player.available_actions(Player,sessionAttributes["lastaction"],infs.nbrCheck)
                                listPlayers  = Player.getListOfExistPlayers(Player,players)
                                infNextStep = getInfNextStep(listPlayers,infs)
                                if len(infNextStep) != 0:
                                    ########################----BUG FIXED----########################
                                    #####NOT DISPLAYING THE PLAYERS ACTION WHEN ALL THE PLAYERS HAVE THE SAME BETTING AMOUNT
                                    #####speak_output= infNextStep[0]
                                    #####SOULAIMANE----THE FOLLOWING OUTPUT FIXES THE PROBLEM
                                    listPlayers  = Player.getListOfExistPlayers(Player,players)
                                    playersActions = toString(lastsActions, infs,listPlayers)
                                    speak_output = f"{playersActions} {infNextStep[0]}"
                                    #################################################################
                                    sessionAttributes["state"] = infNextStep[1]
                                    break
                    elif myindex == 3 :
                        var = True
                        if players[4].isFold == False:
                            sessionAttributes["lastaction"] = Player.play(Player,availableActions,players,players[4],infs,deck,small_blind,lastsActions,holeCardsName,flopCards)
                            sessionAttributes["p_actions"] = update_actions(players[4], sessionAttributes["lastaction"], sessionAttributes["p_actions"])####
                            availableActions = Player.available_actions(Player,sessionAttributes["lastaction"],infs.nbrCheck)
                        listPlayers  = Player.getListOfExistPlayers(Player,players)
                        infNextStep = getInfNextStep(listPlayers,infs)
                        if len(infNextStep) != 0:
                            ########################----BUG FIXED----########################
                            #####NOT DISPLAYING THE PLAYERS ACTION WHEN ALL THE PLAYERS HAVE THE SAME BETTING AMOUNT
                            #####speak_output= infNextStep[0]
                            #####SOULAIMANE----THE FOLLOWING OUTPUT FIXES THE PROBLEM
                            listPlayers  = Player.getListOfExistPlayers(Player,players)
                            playersActions = toString(lastsActions, infs,listPlayers)
                            speak_output = f"{playersActions} {infNextStep[0]}"
                            #################################################################
                            sessionAttributes["state"] = infNextStep[1]
                            var = False
                        if(var):
                            for player in players[:3]:
                                if player.isFold == False:
                                    sessionAttributes["lastaction"] = Player.play(Player,availableActions,players,player,infs,deck,small_blind,lastsActions,holeCardsName,flopCards)
                                    sessionAttributes["p_actions"] = update_actions(player.name, sessionAttributes["lastaction"], sessionAttributes["p_actions"])####
                                    availableActions = Player.available_actions(Player,sessionAttributes["lastaction"],infs.nbrCheck)
                                listPlayers  = Player.getListOfExistPlayers(Player,players)
                                infNextStep = getInfNextStep(listPlayers,infs)
                                if len(infNextStep) != 0:
                                    ########################----BUG FIXED----########################
                                    #####NOT DISPLAYING THE PLAYERS ACTION WHEN ALL THE PLAYERS HAVE THE SAME BETTING AMOUNT
                                    #####speak_output= infNextStep[0]
                                    #####SOULAIMANE----THE FOLLOWING OUTPUT FIXES THE PROBLEM
                                    listPlayers  = Player.getListOfExistPlayers(Player,players)
                                    playersActions = toString(lastsActions, infs,listPlayers)
                                    speak_output = f"{playersActions} {infNextStep[0]}"
                                    #################################################################
                                    sessionAttributes["state"] = infNextStep[1]
                                    break
                    elif myindex == 4 :
                        for player in players[:4]:
                            if player.isFold == False:
                                sessionAttributes["lastaction"] = Player.play(Player,availableActions,players,player,infs,deck,small_blind,lastsActions,holeCardsName,flopCards)
                                sessionAttributes["p_actions"] = update_actions(player.name, sessionAttributes["lastaction"], sessionAttributes["p_actions"])####
                                availableActions = Player.available_actions(Player,sessionAttributes["lastaction"],infs.nbrCheck)
                            listPlayers  = Player.getListOfExistPlayers(Player,players)
                            infNextStep = getInfNextStep(listPlayers,infs)
                            if len(infNextStep) != 0:
                                ########################----BUG FIXED----########################
                                #####NOT DISPLAYING THE PLAYERS ACTION WHEN ALL THE PLAYERS HAVE THE SAME BETTING AMOUNT
                                #####speak_output= infNextStep[0]
                                #####SOULAIMANE----THE FOLLOWING OUTPUT FIXES THE PROBLEM
                                listPlayers  = Player.getListOfExistPlayers(Player,players)
                                playersActions = toString(lastsActions, infs,listPlayers)
                                speak_output = f"{playersActions} {infNextStep[0]}"
                                #################################################################
                                sessionAttributes["state"] = infNextStep[1]
                                break
                    if sessionAttributes["state"] == myState:
                        availableActions = Player.available_actions(Player,sessionAttributes["lastaction"],infs.nbrCheck)
                        listPlayers  = Player.getListOfExistPlayers(Player,players)
                        lastPlayersActions = toString(lastsActions, infs,listPlayers)
                        speak_output=f"{lastPlayersActions}  Your available actions are {availableActions[0]}, {availableActions[1]}, and {availableActions[2]}. "
            sessionAttributes["last_output"] = speak_output
        else:
            speak_output = "Sorry, but you can't raise. Please try again ! "
            sessionAttributes["last_output"] = speak_output ################## REVISE THIS TEXT
        handler_input.response_builder.speak(speak_output).set_should_end_session(False)
        potValue =  Player.getPrice(Player,players)
        myHoleIndex = 2*myindex + 1 
        if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:
            handler_input.response_builder.add_directive(
                RenderDocumentDirective(
                    token="indexToken",
                    document=_load_apl_document("./templates/index.json"),
                    datasources = apl_current(potValue, players, holeCardsName, myindex, myHoleIndex, flopCardsName)
                )
            )
        return handler_input.response_builder.response


class YesIntentHandler(AbstractRequestHandler):
    """Yes intent handler"""
    def can_handle(self,handler_input):
        return ask_utils.is_intent_name("YesIntent")(handler_input)
    
    def handle(self,handler_input):
        logger.info("In YesIntentHandler")
        sessionAttributes = handler_input.attributes_manager.session_attributes
        myState = sessionAttributes["state"]
        global flopCards, infs, deck, lastsActions, flopCardsName, holeCardsName, players
        sessionAttributes["p_actions"] = update_actions_multi(lastsActions, sessionAttributes["p_actions"])#############*
        if myState == "ready to shutdown":
            winText = ""
            price = Player.getPrice(Player,players)
            playersExist = Player.getListOfExistPlayers(Player,players)
            sessionAttributes["state"] = "default"
            sessionAttributes["lastsActions"] = None
            if(len(playersExist) == 1):
                winOne = playersExist[0]
                Player.addPricetoPlayer(Player,players,winOne.name,price)
                speak_output = f"Cnogratulations. You won. "
                winText = "You Won"
            else:
                for player in playersExist:
                    cards = player.holeCards + flopCards
                    player.hand = Cards.get_best_hand(Cards,cards)
                winOne = Cards.getWinOne(Cards,playersExist)
                typeHand = Cards.score_hand(Cards,winOne.hand)[1]
                Player.addPricetoPlayer(Player,players,winOne.name,price)
                if winOne.name == "me" :
                    speak_output = f"Congratulations. You won. The best hand is {typeHand}. The pot contains ${price}. "
                    winText = "You won. "
                else:
                    speak_output = f"The winner is {winOne.name}. The best hand is {typeHand}. "
                    winText = f"{winOne.name} Won"
            potValue =  Player.getPrice(Player,players)
            myHoleIndex = 2*myindex + 1 
            listHoleCards = []
            for player in players:
                if(len(player.holeCards) ==0):
                    listHoleCards.append("empty")
                    listHoleCards.append("empty")
                else:
                    listHoleCards.append(str(player.holeCards[0]))
                    listHoleCards.append(str(player.holeCards[1]))
            
            speak_output += "Say 'replay' to start a new game, or 'stop' to quit. " 
            if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:
                handler_input.response_builder.add_directive(
                    RenderDocumentDirective(
                        token="indexToken",
                        document=_load_apl_document("./templates/index.json"),
                        datasources = apl_current_win(winText, potValue, players, listHoleCards, flopCardsName)
                    )
                )
        elif myState in ["ready to flop","ready to turn","ready to river"] :
            if myState == "ready to flop" :
                flopCards  = Cards.flopCards(Cards,deck)
                for i in range(3):
                    flopCardsName[i] = str(flopCards[i])
                sessionAttributes["lastaction"] = "flop"
                lastsActions.clear()
                infs.cmp_round = 1
            elif myState == "ready to turn":
                card = Cards.getRandomCards(Cards,deck)
                flopCards.append(card)
                flopCardsName[3] = str(card)
                infs.cmp_round = 2
                sessionAttributes["lastaction"] = "turn"
                lastsActions.clear()
            elif myState == "ready to river":
                card = Cards.getRandomCards(Cards,deck)
                flopCards.append(card)
                flopCardsName[4] = str(card)
                infs.cmp_round = 3
                sessionAttributes["lastaction"] = "river"
                lastsActions.clear()
            
            availableActions = Player.available_actions(Player,sessionAttributes["lastaction"],infs.nbrCheck)
            if myindex == 0 :
                for player in players[1:]:
                    if player.isFold == False:
                        sessionAttributes["lastaction"] = Player.play(Player,availableActions,players,player,infs,deck,small_blind,lastsActions,holeCardsName,flopCards)
                        sessionAttributes["p_actions"] = update_actions(player.name, sessionAttributes["lastaction"], sessionAttributes["p_actions"])####
                        availableActions = Player.available_actions(Player,sessionAttributes["lastaction"],infs.nbrCheck)
                listPlayers  = Player.getListOfExistPlayers(Player,players)
                if len(listPlayers)== 1:
                    speak_output= "Are you ready to shutdown? "
                    sessionAttributes["state"] = "ready to shutdown"
            elif myindex == 2:
                if players[1].isFold == False:
                    sessionAttributes["lastaction"] = Player.play(Player,availableActions,players,players[1],infs,deck,small_blind,lastsActions,holeCardsName,flopCards)
                    sessionAttributes["p_actions"] = update_actions(players[1], sessionAttributes["lastaction"], sessionAttributes["p_actions"])####
                listPlayers  = Player.getListOfExistPlayers(Player,players)
                if len(listPlayers)== 1:
                    speak_output= "Are you ready to shutdown? "
                    sessionAttributes["state"] = "ready to shutdown"
            elif myindex == 3 :
                for player in players[1:3]:
                    if player.isFold == False:
                        sessionAttributes["lastaction"] = Player.play(Player,availableActions,players,player,infs,deck,small_blind,lastsActions,holeCardsName,flopCards)
                        sessionAttributes["p_actions"] = update_actions(player.name, sessionAttributes["lastaction"], sessionAttributes["p_actions"])####
                        availableActions = Player.available_actions(Player,sessionAttributes["lastaction"],infs.nbrCheck)
                listPlayers  = Player.getListOfExistPlayers(Player,players)
                if len(listPlayers)== 1:
                    speak_output= "Are you ready to shutdown? "
                    sessionAttributes["state"] = "ready to shutdown"
            elif myindex == 4 :
                for player in players[1:4]:
                    if player.isFold == False:
                        sessionAttributes["lastaction"] = Player.play(Player,availableActions,players,player,infs,deck,small_blind,lastsActions,holeCardsName,flopCards)
                        sessionAttributes["p_actions"] = update_actions(player.name, sessionAttributes["lastaction"], sessionAttributes["p_actions"])####
                        availableActions = Player.available_actions(Player,sessionAttributes["lastaction"],infs.nbrCheck)
                listPlayers  = Player.getListOfExistPlayers(Player,players)
                if len(listPlayers)== 1:
                    speak_output= "Are you ready to shutdown? "
                    sessionAttributes["state"] = "ready to shutdown"
            if sessionAttributes["state"] == myState:
                availableActions = Player.available_actions(Player,sessionAttributes["lastaction"],infs.nbrCheck)
                listPlayers  = Player.getListOfExistPlayers(Player,players)
                lastPlayersActions = toString(lastsActions, infs,listPlayers)
                speak_output=f"{lastPlayersActions} Your available actions are {availableActions[0]}, {availableActions[1]}, and {availableActions[2]}. "
            
            potValue =  Player.getPrice(Player,players)
            myHoleIndex = 2*myindex + 1 
            if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:
                handler_input.response_builder.add_directive(
                    RenderDocumentDirective(
                        token="indexToken",
                        document=_load_apl_document("./templates/index.json"),
                        datasources = apl_current(potValue, players, holeCardsName, myindex, myHoleIndex, flopCardsName)
                    )
                )
            sessionAttributes["last_output"] = speak_output
        else:
            speak_output = "This is an invalid action. "
            sessionAttributes["last_output"] = ""
        handler_input.response_builder.speak(speak_output).set_should_end_session(False)
        return handler_input.response_builder.response


class FoldIntentHandler(AbstractRequestHandler):
    """Fold intent handler"""
    def can_handle(self,handler_input):
        return ask_utils.is_intent_name("FoldIntent")(handler_input)
    
    def handle(self,handler_input):
        logger.info("In FoldIntentHandler")
        global deck, lastsActions, players, flopCards, flopCardsName
        sessionAttributes = handler_input.attributes_manager.session_attributes
        sessionAttributes["lastaction"] = "fold"
        players[myindex].isFold = True
        deck.append(players[myindex].holeCards[0])
        deck.append(players[myindex].holeCards[1])
        players[myindex].holeCards.clear()
        lastsActions.clear()
        sessionAttributes["state"] = "default"
        sessionAttributes["lastaction"] = None
        theWinPlayer,score_hand = Player.winPlayerIfIfold(Player,players,flopCards,deck)
        speak_output = f"The winner is {theWinPlayer.name}. The best hand is {score_hand[1]}. "
        speak_output += "Say 'replay' to start a new game, or 'stop' to quit. "
        winText = theWinPlayer.name+" Won"
        potValue =  Player.getPrice(Player,players)
        myHoleIndex = 2*myindex + 1 
        listHoleCards = []
        for player in players:
            if(len(player.holeCards) ==0):
                listHoleCards.append("empty")
                listHoleCards.append("empty")
            else:
                listHoleCards.append(str(player.holeCards[0]))
                listHoleCards.append(str(player.holeCards[1]))
        for i in range(5):
            flopCardsName[i] = str(flopCards[i])
        if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:
            handler_input.response_builder.add_directive(
                RenderDocumentDirective(
                    token="indexToken",
                    document=_load_apl_document("./templates/index.json"),
                    datasources = apl_current_win(winText, potValue, players, listHoleCards, flopCardsName)
                )
            )
        handler_input.response_builder.speak(speak_output).set_should_end_session(False) 
        return handler_input.response_builder.response


class ReplayIntentHandler(AbstractRequestHandler):
    """Replay intent handler"""
    def can_handle(self,handler_input):
        return ask_utils.is_intent_name("ReplayIntent")(handler_input)
    
    def handle(self,handler_input):
        logger.info("In ReplayIntentHandler")
        sessionAttributes = handler_input.attributes_manager.session_attributes
        myState = sessionAttributes["state"]
        if myState == "default":
            sessionAttributes["state"] = "preflop"
            sessionAttributes["lastaction"] = None
            global players, deck, myindex, infs, lastsActions, holeCardsName, flopCardsName, flopCards
            Player.Replay(Player,players)
            deck = StandarDeck()
            Cards.HoleCards(Cards,deck,players)
            flopCards.clear()
            flopCardsName = ["empty"]*5
            holeCardsName = ["default"]*10
            infs = Informations(4,0,0,0)
            myInf = Player.getMyPosition(Player,players)
            myindex = myInf[1]
            players[1].chips = players[1].chips-small_blind
            players[1].myprice = small_blind
            players[2].myprice = big_blind
            players[2].chips = players[2].chips-big_blind
            infs.last_raise = big_blind
            sessionAttributes["lastaction"] = "bet"
            availableActions = Player.available_actions(Player,sessionAttributes["lastaction"],infs.nbrCheck)
            lastsActions.clear()
            lastsActions.append([players[2].name,"bet"])
            if myindex == 0:
                for player in players[3:]:
                    sessionAttributes["lastaction"] = Player.play(Player,availableActions,players,player,infs,deck,small_blind,lastsActions,holeCardsName,flopCards)
                    availableActions = Player.available_actions(Player,sessionAttributes["lastaction"],infs.nbrCheck)
            elif myindex == 1:
                for player in players[3:]:
                    sessionAttributes["lastaction"] = Player.play(Player,availableActions,players,player,infs,deck,small_blind,lastsActions,holeCardsName,flopCards)
                    availableActions = Player.available_actions(Player,sessionAttributes["lastaction"],infs.nbrCheck)
                if players[0].isFold == False:
                    sessionAttributes["lastaction"] = Player.play(Player,availableActions,players,players[0],infs,deck,small_blind,lastsActions,holeCardsName,flopCards)
            elif myindex == 2 :
                if lastsActions[0][0] == "me":
                    lastsActions.clear()
                for player in players[3:]:
                    sessionAttributes["lastaction"] = Player.play(Player,availableActions,players,player,infs,deck,small_blind,lastsActions,holeCardsName,flopCards)
                    availableActions = Player.available_actions(Player,sessionAttributes["lastaction"],infs.nbrCheck)
                for player in players[:2]:
                    sessionAttributes["lastaction"] = Player.play(Player,availableActions,players,player,infs,deck,small_blind,lastsActions,holeCardsName,flopCards)
                    availableActions = Player.available_actions(Player,sessionAttributes["lastaction"],infs.nbrCheck)
                listPlayers  = Player.getListOfExistPlayers(Player,players)
                infNextStep = getInfNextStep(listPlayers,infs)
                if len(infNextStep) != 0:
                    speak_output= infNextStep[0]
                    sessionAttributes["state"] = infNextStep[1]
            elif myindex == 4 :
                sessionAttributes["lastaction"] = Player.play(Player,availableActions,players,players[3],infs,deck,small_blind,lastsActions,holeCardsName,flopCards)
            if sessionAttributes["state"] == "preflop":
                availableActions = Player.available_actions(Player,sessionAttributes["lastaction"],infs.nbrCheck)
                listPlayers  = Player.getListOfExistPlayers(Player,players)
                playersActions = toString(lastsActions, infs,listPlayers)
                speak_output=f"{playersActions}  Your available actions are {availableActions[0]}, {availableActions[1]}, and {availableActions[2]}. "
            potValue =  Player.getPrice(Player,players)
            myHoleIndex = 2*myindex + 1 
            if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:
                handler_input.response_builder.add_directive(
                    RenderDocumentDirective(
                        token="indexToken",
                        document=_load_apl_document("./templates/index.json"),
                        datasources = apl_current(potValue, players, holeCardsName, myindex, myHoleIndex, flopCardsName)
                    )
                )
            sessionAttributes["last_output"] = speak_output
            speak_output = "Ok. Starting a new game ... " + speak_output
        else:   
            speak_output="This is an invalid action. You can fold first, then restart a new game. "
            sessionAttributes["last_output"] = ""
        handler_input.response_builder.speak(speak_output).set_should_end_session(False)
        return handler_input.response_builder.response


class MyInfoIntentHandler(AbstractRequestHandler):
    """Help intent handler"""
    def can_handle(self,handler_input):
        return ask_utils.is_intent_name("MyInfoIntent")(handler_input)
    
    def handle(self,handler_input):
        logger.info("In MyInfoIntentHandler")
        sessionAttributes = handler_input.attributes_manager.session_attributes
        myState = sessionAttributes["state"]
        speak_output = ""
        if myState != "default":
            playersExist = Player.getListOfExistPlayers(Player,players)
            if len(flopCards) == 0:
                speak_output = f"Your sold is {players[myindex].chips}$. You're in {players[myindex].position}. Your cards are {players[myindex].holeCards[0]} and {players[myindex].holeCards[1]}, and the number of the remaining players is {len(playersExist)}. "
            elif len(flopCards) == 3 :
                speak_output = f"Your sold is {players[myindex].chips}$. You're in {players[myindex].position}. Your cards are {players[myindex].holeCards[0]} and {players[myindex].holeCards[1]}, while the flop cards are {flopCards[0]} , {flopCards[1]} and {flopCards[2]}. The number of the remaining players is {len(playersExist)}. "
            elif len(flopCards) == 4 :
                speak_output = f"Your sold is {players[myindex].chips}$. You're in {players[myindex].position}. Your cards are {players[myindex].holeCards[0]} and {players[myindex].holeCards[1]}. The flop cards are {flopCards[0]} , {flopCards[1]} , {flopCards[2]} and {flopCards[3]}. The number of the remaining players is {len(playersExist)}. "
            elif len(flopCards) == 5:
                speak_output = f"Your sold is {players[myindex].chips}$. You're in {players[myindex].position}. Your cards are {players[myindex].holeCards[0]} and {players[myindex].holeCards[1]}. The flop cards are {flopCards[0]} , {flopCards[1]} , {flopCards[2]} and {flopCards[3]}. The number of the remaining players is {len(playersExist)}. "
        else : 
            speak_output = "We can't help you with that because you haven't started yet. "
        if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:
            handler_input.response_builder.add_directive(
                RenderDocumentDirective(
                    token="winToken",
                    document=_load_apl_document("./templates/help.json"),
                    datasources = apl_info(speak_output)
                )
            )
        speak_output += sessionAttributes["last_output"]
        handler_input.response_builder.speak(speak_output).set_should_end_session(False)
        return handler_input.response_builder.response


class CheckIntentHandler(AbstractRequestHandler):
    """Check intent handler"""
    def can_handle(self,handler_input):
        return ask_utils.is_intent_name("CheckIntent")(handler_input)
    
    def handle(self,handler_input):
        logger.info("In CheckIntentHandler")
        global infs,lastsActions,holeCardsName,players,deck
        sessionAttributes = handler_input.attributes_manager.session_attributes
        sessionAttributes["p_actions"] = update_actions_multi(lastsActions, sessionAttributes["p_actions"])#############*
        availableActions = Player.available_actions(Player,sessionAttributes["lastaction"],infs.nbrCheck)
        if "check" in availableActions:
            sessionAttributes["lastaction"] = "check"
            infs.nbrCheck = infs.nbrCheck+1
            lastsActions.clear()
            
            listPlayers  = Player.getListOfExistPlayers(Player,players)
            infNextStep = getInfNextStep(listPlayers,infs)
            if len(infNextStep) != 0:
                ########################----BUG FIXED----########################
                #####NOT DISPLAYING THE PLAYERS ACTION WHEN ALL THE PLAYERS HAVE THE SAME BETTING AMOUNT
                #####speak_output= infNextStep[0]
                #####SOULAIMANE----THE FOLLOWING OUTPUT FIXES THE PROBLEM
                listPlayers  = Player.getListOfExistPlayers(Player,players)
                playersActions = toString(lastsActions, infs,listPlayers)
                speak_output = f"{playersActions} {infNextStep[0]}"
                #################################################################
                sessionAttributes["state"] = infNextStep[1]
            else:
                myState = sessionAttributes["state"]
                availableActions = Player.available_actions(Player,sessionAttributes["lastaction"],infs.nbrCheck)
                if myindex == 0:
                    for player in players[1:]:
                        if player.isFold == False:
                            sessionAttributes["lastaction"] = Player.play(Player,availableActions,players,player,infs,deck,small_blind,lastsActions,holeCardsName,flopCards)
                            sessionAttributes["p_actions"] = update_actions(player.name, sessionAttributes["lastaction"], sessionAttributes["p_actions"])####
                            availableActions = Player.available_actions(Player,sessionAttributes["lastaction"],infs.nbrCheck)
                        listPlayers  = Player.getListOfExistPlayers(Player,players)
                        infNextStep = getInfNextStep(listPlayers,infs)
                        if len(infNextStep) != 0:
                            ########################----BUG FIXED----########################
                            #####NOT DISPLAYING THE PLAYERS ACTION WHEN ALL THE PLAYERS HAVE THE SAME BETTING AMOUNT
                            #####speak_output= infNextStep[0]
                            #####SOULAIMANE----THE FOLLOWING OUTPUT FIXES THE PROBLEM
                            listPlayers  = Player.getListOfExistPlayers(Player,players)
                            playersActions = toString(lastsActions, infs,listPlayers)
                            speak_output = f"{playersActions} {infNextStep[0]}"
                            #################################################################
                            sessionAttributes["state"] = infNextStep[1]
                            break
                elif myindex == 1:
                    var = True
                    for player in players[2:]:
                        if player.isFold == False:
                            sessionAttributes["lastaction"] = Player.play(Player,availableActions,players,player,infs,deck,small_blind,lastsActions,holeCardsName,flopCards)
                            sessionAttributes["p_actions"] = update_actions(player.name, sessionAttributes["lastaction"], sessionAttributes["p_actions"])####
                            availableActions = Player.available_actions(Player,sessionAttributes["lastaction"],infs.nbrCheck)
                        listPlayers  = Player.getListOfExistPlayers(Player,players)
                        infNextStep = getInfNextStep(listPlayers,infs)
                        if len(infNextStep) != 0:
                            ########################----BUG FIXED----########################
                            #####NOT DISPLAYING THE PLAYERS ACTION WHEN ALL THE PLAYERS HAVE THE SAME BETTING AMOUNT
                            #####speak_output= infNextStep[0]
                            #####SOULAIMANE----THE FOLLOWING OUTPUT FIXES THE PROBLEM
                            listPlayers  = Player.getListOfExistPlayers(Player,players)
                            playersActions = toString(lastsActions, infs,listPlayers)
                            speak_output = f"{playersActions} {infNextStep[0]}"
                            #################################################################
                            sessionAttributes["state"] = infNextStep[1]
                            var = False
                            break
                    if (var):
                        if players[0].isFold == False:
                            sessionAttributes["lastaction"] = Player.play(Player,availableActions,players,players[0],infs,deck,small_blind,lastsActions,holeCardsName,flopCards)
                            sessionAttributes["p_actions"] = update_actions(players[0], sessionAttributes["lastaction"], sessionAttributes["p_actions"])####
                        listPlayers  = Player.getListOfExistPlayers(Player,players)
                        infNextStep = getInfNextStep(listPlayers,infs)
                        if len(infNextStep) != 0:
                            ########################----BUG FIXED----########################
                            #####NOT DISPLAYING THE PLAYERS ACTION WHEN ALL THE PLAYERS HAVE THE SAME BETTING AMOUNT
                            #####speak_output= infNextStep[0]
                            #####SOULAIMANE----THE FOLLOWING OUTPUT FIXES THE PROBLEM
                            listPlayers  = Player.getListOfExistPlayers(Player,players)
                            playersActions = toString(lastsActions, infs,listPlayers)
                            speak_output = f"{playersActions} {infNextStep[0]}"
                            #################################################################
                            sessionAttributes["state"] = infNextStep[1]
                elif myindex == 2 :
                    var = True
                    for player in players[3:]:
                        if player.isFold == False:
                            sessionAttributes["lastaction"] = Player.play(Player,availableActions,players,player,infs,deck,small_blind,lastsActions,holeCardsName,flopCards)
                            sessionAttributes["p_actions"] = update_actions(player.name, sessionAttributes["lastaction"], sessionAttributes["p_actions"])####
                            availableActions = Player.available_actions(Player,sessionAttributes["lastaction"],infs.nbrCheck)
                        listPlayers  = Player.getListOfExistPlayers(Player,players)
                        infNextStep = getInfNextStep(listPlayers,infs)
                        if len(infNextStep) != 0:
                            ########################----BUG FIXED----########################
                            #####NOT DISPLAYING THE PLAYERS ACTION WHEN ALL THE PLAYERS HAVE THE SAME BETTING AMOUNT
                            #####speak_output= infNextStep[0]
                            #####SOULAIMANE----THE FOLLOWING OUTPUT FIXES THE PROBLEM
                            listPlayers  = Player.getListOfExistPlayers(Player,players)
                            playersActions = toString(lastsActions, infs,listPlayers)
                            speak_output = f"{playersActions} {infNextStep[0]}"
                            #################################################################
                            sessionAttributes["state"] = infNextStep[1]
                            var = False
                            break
                    if (var):
                        for player in players[:2]:
                            if player.isFold == False:
                                sessionAttributes["lastaction"] = Player.play(Player,availableActions,players,player,infs,deck,small_blind,lastsActions,holeCardsName,flopCards)
                                sessionAttributes["p_actions"] = update_actions(player.name, sessionAttributes["lastaction"], sessionAttributes["p_actions"])####
                                availableActions = Player.available_actions(Player,sessionAttributes["lastaction"],infs.nbrCheck)
                            listPlayers  = Player.getListOfExistPlayers(Player,players)
                            infNextStep = getInfNextStep(listPlayers,infs)
                            if len(infNextStep) != 0:
                                ########################----BUG FIXED----########################
                                #####NOT DISPLAYING THE PLAYERS ACTION WHEN ALL THE PLAYERS HAVE THE SAME BETTING AMOUNT
                                #####speak_output= infNextStep[0]
                                #####SOULAIMANE----THE FOLLOWING OUTPUT FIXES THE PROBLEM
                                listPlayers  = Player.getListOfExistPlayers(Player,players)
                                playersActions = toString(lastsActions, infs,listPlayers)
                                speak_output = f"{playersActions} {infNextStep[0]}"
                                #################################################################
                                sessionAttributes["state"] = infNextStep[1]
                                break
                elif myindex == 3 :
                    var = True
                    if players[4].isFold == False:
                        sessionAttributes["lastaction"] = Player.play(Player,availableActions,players,players[4],infs,deck,small_blind,lastsActions,holeCardsName,flopCards)
                        sessionAttributes["p_actions"] = update_actions(players[4], sessionAttributes["lastaction"], sessionAttributes["p_actions"])####
                        availableActions = Player.available_actions(Player,sessionAttributes["lastaction"],infs.nbrCheck)
                    listPlayers  = Player.getListOfExistPlayers(Player,players)
                    infNextStep = getInfNextStep(listPlayers,infs)
                    if len(infNextStep) != 0:
                        ########################----BUG FIXED----########################
                        #####NOT DISPLAYING THE PLAYERS ACTION WHEN ALL THE PLAYERS HAVE THE SAME BETTING AMOUNT
                        #####speak_output= infNextStep[0]
                        #####SOULAIMANE----THE FOLLOWING OUTPUT FIXES THE PROBLEM
                        listPlayers  = Player.getListOfExistPlayers(Player,players)
                        playersActions = toString(lastsActions, infs,listPlayers)
                        speak_output = f"{playersActions} {infNextStep[0]}"
                        #################################################################
                        sessionAttributes["state"] = infNextStep[1]
                        var = False
                    if(var):
                        for player in players[:3]:
                            if player.isFold == False:
                                sessionAttributes["lastaction"] = Player.play(Player,availableActions,players,player,infs,deck,small_blind,lastsActions,holeCardsName,flopCards)
                                sessionAttributes["p_actions"] = update_actions(player.name, sessionAttributes["lastaction"], sessionAttributes["p_actions"])####
                                availableActions = Player.available_actions(Player,sessionAttributes["lastaction"],infs.nbrCheck)
                            listPlayers  = Player.getListOfExistPlayers(Player,players)
                            infNextStep = getInfNextStep(listPlayers,infs)
                            if len(infNextStep) != 0:
                                ########################----BUG FIXED----########################
                                #####NOT DISPLAYING THE PLAYERS ACTION WHEN ALL THE PLAYERS HAVE THE SAME BETTING AMOUNT
                                #####speak_output= infNextStep[0]
                                #####SOULAIMANE----THE FOLLOWING OUTPUT FIXES THE PROBLEM
                                listPlayers  = Player.getListOfExistPlayers(Player,players)
                                playersActions = toString(lastsActions, infs,listPlayers)
                                speak_output = f"{playersActions} {infNextStep[0]}"
                                #################################################################
                                sessionAttributes["state"] = infNextStep[1]
                                break
                elif myindex == 4 :
                    for player in players[:4]:
                        if player.isFold == False:
                            sessionAttributes["lastaction"] = Player.play(Player,availableActions,players,player,infs,deck,small_blind,lastsActions,holeCardsName,flopCards)
                            sessionAttributes["p_actions"] = update_actions(player.name, sessionAttributes["lastaction"], sessionAttributes["p_actions"])####
                            availableActions = Player.available_actions(Player,sessionAttributes["lastaction"],infs.nbrCheck)
                        listPlayers  = Player.getListOfExistPlayers(Player,players)
                        infNextStep = getInfNextStep(listPlayers,infs)
                        if len(infNextStep) != 0:
                            ########################----BUG FIXED----########################
                            #####NOT DISPLAYING THE PLAYERS ACTION WHEN ALL THE PLAYERS HAVE THE SAME BETTING AMOUNT
                            #####speak_output= infNextStep[0]
                            #####SOULAIMANE----THE FOLLOWING OUTPUT FIXES THE PROBLEM
                            listPlayers  = Player.getListOfExistPlayers(Player,players)
                            playersActions = toString(lastsActions, infs,listPlayers)
                            speak_output = f"{playersActions} {infNextStep[0]}"
                            #################################################################
                            sessionAttributes["state"] = infNextStep[1]
                            break
                if sessionAttributes["state"] == myState:
                    availableActions = Player.available_actions(Player,sessionAttributes["lastaction"],infs.nbrCheck)
                    lastPlayersActions = toString(lastsActions, infs,listPlayers)
                    speak_output=f"{lastPlayersActions}  Your available actions are {availableActions[0]}, {availableActions[1]}, and {availableActions[2]}. "
            
            potValue =  Player.getPrice(Player,players)
            myHoleIndex = 2*myindex + 1 
            if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:
                handler_input.response_builder.add_directive(
                    RenderDocumentDirective(
                        token="indexToken",
                        document=_load_apl_document("./templates/index.json"),
                        datasources = apl_current(potValue, players, holeCardsName, myindex, myHoleIndex, flopCardsName)
                    )
                )
            sessionAttributes["last_output"] = speak_output
        else:
            speak_output = "invalid action"
            sessionAttributes["last_output"] = ""
        handler_input.response_builder.speak(speak_output).set_should_end_session(False)
        return handler_input.response_builder.response


## info Intents
class CurrentSituationIntentHandler(AbstractRequestHandler):
    """Tell the current situation about the table"""
    def can_handle(self,handler_input):
        return ask_utils.is_intent_name("CurrentSituationIntent")(handler_input)
    
    def handle(self,handler_input):
        logger.info("In CurrentSituationIntent")
        sessionAttributes = handler_input.attributes_manager.session_attributes
        
        my_index = myindex
        current_static_list = sessionAttributes["p_actions"]
        
        speak_output = current_situation(my_index, current_static_list, infs)
        handler_input.response_builder.speak(speak_output).set_should_end_session(False)
        return handler_input.response_builder.response

class GetPositionIntentHandler(AbstractRequestHandler):
    """ Get my position (delear , small blind, big blind ...)"""
    def can_handle(self,handler_input):
        return ask_utils.is_intent_name("GetPositionIntent")(handler_input)
    
    def handle(self,handler_input):
        logger.info("In GetPositionIntentHandler")
        sessionAttributes = handler_input.attributes_manager.session_attributes
        myState = sessionAttributes["state"]
        if myState != "default":
            speak_output = f"Your position is {players[myindex].position}. "
        else:
            speak_output = "You don't have any position yet. "
        
        speak_output += sessionAttributes["last_output"]
        handler_input.response_builder.speak(speak_output).set_should_end_session(False)
        return handler_input.response_builder.response


class GetHoleCardsIntentHandler(AbstractRequestHandler):
    """ Get hole cards """
    def can_handle(self,handler_input):
        return ask_utils.is_intent_name("GetHoleCardsIntent")(handler_input)
    
    def handle(self,handler_input):
        logger.info("In GetHoleCardsIntentHandler")
        sessionAttributes = handler_input.attributes_manager.session_attributes
        myState = sessionAttributes["state"]
        if myState != "default":
            speak_output = f"Your hole cards are {players[myindex].holeCards[0]} and {players[myindex].holeCards[1]}. "
        else:
            speak_output = "You haven't started yet! "
        
        speak_output += sessionAttributes["last_output"]
        handler_input.response_builder.speak(speak_output).set_should_end_session(False)
        return handler_input.response_builder.response


class GetCommunityCardsIntentHandler(AbstractRequestHandler):
    """ Get community cards """
    def can_handle(self,handler_input):
        return ask_utils.is_intent_name("GetCommunityCardsIntent")(handler_input)
    
    def handle(self,handler_input):
        logger.info("In GetCommunityCardsIntentHandler")
        sessionAttributes = handler_input.attributes_manager.session_attributes
        myState = sessionAttributes["state"]
        if myState != "default":
            if len(flopCards) == 0:
                speak_output = f"No card on the table for now! "
            elif len(flopCards) == 3 :
                speak_output=f"Community cards are {flopCards[0]}, {flopCards[1]}, and {flopCards[2]}. "
            elif len(flopCards) == 4 :
                speak_output = f"Community cards are {flopCards[0]}, {flopCards[1]}, {flopCards[2]}, and {flopCards[3]}. "
            elif len(flopCards) == 5:
                speak_output=f"Community cards are {flopCards[0]}, {flopCards[1]}, {flopCards[2]}, {flopCards[3]}, and {flopCards[4]}. "
        else:
            speak_output = "The game hasn't started yet. "
        
        speak_output += sessionAttributes["last_output"]
        handler_input.response_builder.speak(speak_output).set_should_end_session(False)
        return handler_input.response_builder.response


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input) or
                ask_utils.is_intent_name("CloseIntent")(handler_input))

    def handle(self, handler_input):
        logger.info("In CancelOrStopIntentHandler")
        speak_output = "Ok. See you next time. "
        
        if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:
            handler_input.response_builder.add_directive(
                RenderDocumentDirective(
                    token="homeToken",
                    document=_load_apl_document("./templates/home.json"),
                    datasources = apl_home("stop")
                )
            )
        handler_input.response_builder.set_should_end_session(True)
        return handler_input.response_builder.speak(speak_output).response


class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        logger.info("In FallbackIntentHandler")
        speech = "Hmmm, I can't really understand what you're saying. You can say 'Help' if you want to ask for help. "
        reprompt = "I didn't catch that. You can say 'Help' if you want to ask for help. "
        return handler_input.response_builder.speak(speech).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        logger.info("In SessionEndedRequestHandler")

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.info("In CatchAllExceptionHandler")
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return handler_input.response_builder.speak(speak_output).response


# The SkillBuilder object acts as the entry point for your skill, routing all request and response payloads to the handlers above.
# Make sure any new handlers or interceptors you've defined are included below. The order matters - they're processed top to bottom.
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(PerflopIntentHandler())
sb.add_request_handler(AboutUsIntentHandler())
sb.add_request_handler(CallIntentHandler())
sb.add_request_handler(RaiseIntentHandler())
sb.add_request_handler(YesIntentHandler())
sb.add_request_handler(FoldIntentHandler())
sb.add_request_handler(CheckIntentHandler())
sb.add_request_handler(ReplayIntentHandler())
sb.add_request_handler(MyInfoIntentHandler())
sb.add_request_handler(CurrentSituationIntentHandler())
sb.add_request_handler(GetPositionIntentHandler())
sb.add_request_handler(GetHoleCardsIntentHandler())
sb.add_request_handler(GetCommunityCardsIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()