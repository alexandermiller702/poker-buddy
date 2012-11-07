from __future__ import print_function
import sys
import re
from poker_data import sklansky_ratings, stats_rankings, card_suits, card_vals
from pokereval import PokerEval 
from collections import defaultdict

e = PokerEval()

def cardmapper(val):
    """
    >>> cardmapper(-1)
    '__'

    >>> cardmapper(0)
    '2c'

    >>> cardmapper(51)
    'As'
    """
    if val == -1:
        return '__'
    result = divmod(val, 13)
    return card_vals[result[1]] + card_suits[result[0]]

def card_comparator(x, y):
    """
    >>> card_comparator('2', '3')
    -1

    >>> card_comparator('A', '2')
    12

    """
    return card_vals.index(x) - card_vals.index(y)

def get_starting_hand(cards):
    """
    >>> get_starting_hand(('Ah', 'As'))
    'AA'

    >>> get_starting_hand(('Ah', 'Qs'))
    'AQ'

    >>> get_starting_hand(('Qh', 'As'))
    'AQ'

    >>> get_starting_hand(('2s', 'As'))
    'A2s'

    """
    starting_hand = ''.join(sorted(cards[0][0] + cards[1][0], card_comparator, reverse=True))
    if cards[0][1] == cards[1][1]:
        starting_hand += "s"
    return starting_hand

def rank_starting_hand(cards):
    """
    >>> rank_starting_hand(('Ah', 'As'))
    Group 1
    (1, 2.32)

    >>> rank_starting_hand(('3h', '2h'))
    Group 8
    (169, -0.16)
    """
    starting_hand = get_starting_hand(cards)
    print(([sklansky_ratings[group_key] for group_key in sklansky_ratings if starting_hand in group_key] + [None])[0])
    print(stats_rankings[starting_hand])

def rank_hand(pocket_cards, community_cards, iterations=100000):
    '''
    >>> rank_hand([['Ad', 'Kd'], ['__', '__'], ['__', '__'], ['__', '__'], ['__', '__']], ['Jd', 'Qd', 'Td'])
    ['Ad', 'Kd'] 100% 100000 0 0
    ['__', '__']  0% 0 100000 0
    ['__', '__']  0% 0 100000 0
    ['__', '__']  0% 0 100000 0
    ['__', '__']  0% 0 100000 0

    '''
    result = e.poker_eval(game = "holdem",
       pockets = pocket_cards, 
       iterations = iterations,
       board = community_cards + ['__'] * (5 - len(community_cards)))

    for i, data in enumerate(result['eval']):
        print(pocket_cards[i], "%2d%%" % (float(data['ev']) / 10), data['winhi'], data['losehi'], data['tiehi'])

def get_cards(update_str, player=True):
    """
    >>> get_cards('''Players0.Cards.~Count=2|Players0.Cards0=-1|Players0.Cards1=-1|Players1.PlayerAtSeat.PlayerId=b2c6bc38-2898-4f0d-816f-c04beb5fe2f1|Players1.PlayerAtSeat.SeatId=1|Players1.Name=Rog|Players1.Balance=990|Players1.InGame=True|Players1.ImageUrl=http://graph.facebook.com/659666531/picture?type%3Dnormal|Players1.Rank=28|Players1.RankValue=28|Players1.Cards.~Count=2|Players1.Cards0=21|Players1.Cards1=17|Players2.PlayerAtSeat.PlayerId=f9b99c7f-2531-464f-a2b1-83e7ef5ec267|Players2.PlayerAtSeat.SeatId=2|Players2.Name=marc|Players2.Balance=980|Players2.InGame=True|Players2.ImageUrl=avatars/default_small.png|Players2.Rank=40|Players2.RankValue=51|Players2.Cards.~Count=2|Players2.Cards0=-1|Players2.Cards1=-1|Players3.PlayerAtSeat.PlayerId=54a159ed-7a91-44a6-a9c8-4b926461231d|Players3.PlayerAtSeat.SeatId=3|Players3.Name=melaniafcb|Players3.Balance=1000|Players3.InGame=True|Players3.ImageUrl=avatars/avatar_female1_small.png|Players3.Rank=30|Players3.RankValue=30|Players3.Cards.~Count=2|Players3.Cards0=-1|Players3.Cards1=-1|Players4.PlayerAtSeat.PlayerId=a0760917-29fa-4ecd-b7e4-8a1cb30298ef|Players4.PlayerAtSeat.SeatId=4|Players4.Name=wawawiwa|Players4.Balance=1000|Players4.InGame=True|Players4.ImageUrl=http://graph.facebook.com/704950081/picture?type%3Dnormal|Players4.Rank=23|Players4.RankValue=23|Players4.Cards.~Count=2|Players4.Cards0=-1|Players4.Cards1=-1|Players.~Count=5''')
    [['Td', '6d'], ['__', '__'], ['__', '__'], ['__', '__'], ['__', '__']]

    >>> get_cards('''~ActionType=UpdateCommunityCards|Actions2.CommunityCards0=34|Actions2.CommunityCards1=27|Actions2.CommunityCards2=48|Actions2.CommunityCards.~Count=3''', player=False)
    ['Th', '3h', 'Js']
    """
    match = "Players(.)\.Cards([0-9])=(-?[0-9]*)" if player else "Actions.\.(C)ommunityCards([0-4])=(-?[0-9]*)"
    matches = re.findall(match, update_str)
    if not matches:
        return []
    result = defaultdict(list)
    for match in matches:
        result[match[0]] += [cardmapper(int(match[2]))]
    return result.values() if player else result.values()[0]

def check_for(pattern, update_str):
    """
    >>> check_for('''Actions0\.Action=1\|''', "Actions0.Action=1|")
    True

    >>> check_for('''Actions0\.Action=1\|''', "Actions0.Axtion=1|")

    """
    matches = re.findall(pattern, update_str)
    if matches:
        return True

old_player_cards = None
def parse_update(update_str):
    global old_player_cards
    try:
        player_cards = get_cards(update_str)
    except e:
        print(update_str)
        print(sys.exc_info())
        return
    if player_cards:
        old_player_cards = player_cards
        print("Player cards %s" % player_cards)
        my_cards = [v for v in player_cards if v[0] != '__']
        if my_cards:
            rank_starting_hand(my_cards[0])
    else:
        if check_for("Actions.\.Action=1\|", update_str) and not check_for("Actions(.)\.PlayerAtSeat\.PlayerId=b2c6bc38-2898-4f0d-816f-c04beb5fe2f1.*Actions\\1\.Action=1\|", update_str):
            for i in range(len(old_player_cards)):
                if old_player_cards[i][0] == '__':
                    del old_player_cards[i]
                    break
        player_cards = old_player_cards
        community_cards = get_cards(update_str, player=False)
        if community_cards:
            print("Community cards %s" % community_cards)
            rank_hand(player_cards, community_cards)

def read_raw_from_stdin():
    with open("/tmp/poker-buddy.log", 'w') as logfile:
        line = ''
        while 1:
            l = sys.stdin.readline()
            if not l:
                break
            if not l.strip() or not '|' in l:
                continue
            logfile.write(l + "\n")
            line += l.strip()
            if line[-1] == '.' and line.split('|')[-1].find('=') > 0:
                try:
                    print('.', end='')
                    parse_update(line)
                    line = ''
                except:
                    print(line)
                    raise

def read_from_pcapy():
    import pcapy
    dir(pcapy)

#    pcapy.findalldevs()
    pc = pcapy.open_live('eth1', 1024, False, 100)

    pc.setfilter('tcp and host 192.168.1.106 and ( port 5400 or port 5500 )')

    from impacket.ImpactDecoder import TCPDecoder
    # callback for received packets
    def recv_pkts(hdr, data):
        packet = TCPDecoder().decode(data)
        print(packet)

#    packet_limit = -1 # infinite
    packet_limit = 10
    pc.loop(packet_limit, recv_pkts) # capture packets

if __name__ == "__main__":
    read_raw_from_stdin()
#    read_from_pcapy()