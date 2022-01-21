import logging
import os
import boto3
from botocore.exceptions import ClientError

from Poker import Cards,Player
from ask_sdk_model import ui
import json

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def create_presigned_url(object_name):
    """Generate a presigned URL to share an S3 object with a capped expiration of 60 seconds
    :param object_name: string
    :return: Presigned URL as string. If error, returns None.
    """
    s3_client = boto3.client('s3',
                             region_name=os.environ.get('S3_PERSISTENCE_REGION'),
                             config=boto3.session.Config(signature_version='s3v4',s3={'addressing_style': 'path'}))
    try:
        bucket_name = os.environ.get('S3_PERSISTENCE_BUCKET')
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=60*1)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response

## start code ##
def StandarDeck():
    allCards = []
    suits = list(range(4))
    values = list(range(13))
    for j in suits:
        for i in values:
            allCards.append(Cards(i,j))
    return allCards

#cette fonction retourne l'etape suivant
def getInfNextStep(listPlayers,infs):
    if (Player.testAllPrice(Player,listPlayers) and infs.cmp_round == 3 and (infs.nbrCheck == 0 or infs.nbrCheck == len(listPlayers))) or len(listPlayers) == 1:
        return ["are you ready to the Shutdown round?","ready to shutdown"]
    elif(Player.testAllPrice(Player,listPlayers) and infs.cmp_round == 0 and (infs.nbrCheck == 0 or infs.nbrCheck == len(listPlayers))):
        infs.nbrCheck = 0
        return ["are you ready to the Flop round?","ready to flop"]
    elif (Player.testAllPrice(Player,listPlayers) and infs.cmp_round == 1 and (infs.nbrCheck == 0 or infs.nbrCheck == len(listPlayers))):
        infs.nbrCheck = 0
        return ["are you ready to the Turn round?","ready to turn"]
    elif (Player.testAllPrice(Player,listPlayers) and infs.cmp_round == 2 and (infs.nbrCheck == 0 or infs.nbrCheck == len(listPlayers))):
        infs.nbrCheck = 0
        return ["are you ready to the River round?","ready to river"]
    else:
        return []

#return l'indice d'un player dans la liste
def getIndexPlayerInPlayers(players,player):
    for p in players:
        if player.name == p.name :
            return players.index(p)

def info_player(playerAction, infs,listPlayers):
    """This function takes and action and outputs the message
    said by alexa"""
    if playerAction[1] in ['fold','check', 'call']:
        result = playerAction[1]+'ed'
    elif playerAction[1] == 'raise':
        for player in listPlayers:
            if player.name == playerAction[0]:
                result = playerAction[1]+'d to $'+str(player.myprice)
        #result = playerAction[1]+'d to $'+str(infs.last_raise)
    else:
        result = playerAction[1]
    return result+'. '

def toString(lastactions, infs,listPlayers):
    result = "Here is the current situation: "
    action = ""
    if len(lastactions) != 0:
        for playerAction in lastactions:
            action = info_player(playerAction, infs,listPlayers)
            result = f"{result}{playerAction[0]} {action}"
    return result

def update_actions(name, action, p_actions):
    """makes sure the list of players actions (p_actions) remains up to date
    by executing this function whenever a (name) makes an (action)"""
    for p in p_actions:
        if p[0] == name:
            p[1] = action
    return p_actions

def update_actions_multi(my_list, p_actions):
    """the same as the function above but this one is executed in the beginning
    in order to initiate the list (p_actions) with the first actions (my_list)"""
    for p in p_actions:
        for player in my_list:
            if p[0] == player[0]:
                p[1] = player[1]
    return p_actions

def current_situation(my_index, current_static_list, infs):
    """gives an output text about the current situation, starting from the player 
    sitting next to the main player"""
    
    output = "Here is the current situation: "
    
    if current_static_list[my_index][1] != "":
        logger.info(f"CHECKPOINT: index: {current_static_list[my_index]}")
        action = info_player(current_static_list[my_index][1], infs)
        output += f"You {action}"
    
    for i in range(my_index+1,5):
        c = current_static_list[i]
        if c[1] != "":
            action = info_player(c[1], infs)
            output += f"{c[0]} {action}"
    
    for i in range(0,my_index):
        c = current_static_list[i]
        if c[1] != "":
            action = info_player(c[1], infs)
            output += f"{c[0]} {action}"
    
    return output

def _load_apl_document(file_path):
    # type: (str) -> Dict[str, Any]
    """Load the apl json document at the path into a dict object."""
    with open(file_path) as f:
        return json.load(f)

def create_url(key):
    img_url_raw = str(ui.Image(large_image_url=create_presigned_url(key)))
    length = len(img_url_raw)
    return img_url_raw[21:length-28]


