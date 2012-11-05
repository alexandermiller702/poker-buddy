import sys
import re
from poker_data import sklansky_ratings, stats_rankings, card_suits, card_vals

def cardmapper(val):
    """
    >>> cardmapper(0)
    '2c'

    >>> cardmapper(0)
    '2c'

    >>> cardmapper(51)
    'As'
    """
    result = divmod(val, 13)
    return card_vals[result[1]] + card_suits[result[0]]

def card_comparator(x, y):
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
    print ([sklansky_ratings[group_key] for group_key in sklansky_ratings if starting_hand in group_key] + [None])[0]
    print stats_rankings[starting_hand]

def parse_update(update_str):
    data = re.split("[|]", update_str)
    cards = [s for s in data if re.findall("Cards[0-4]=[0-9]", s)]
    if cards:
        print [cardmapper(int(param.split('=')[1])) for param in cards]
    #sys.stdout.write(update_str)

def read_raw_from_stdin():
    while 1:
        line = sys.stdin.readline()
        if not line: break
        try:
            decoded_line = line.strip().decode("hex")
            parse_update(decoded_line)
        except:
            print line
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
        print packet

#    packet_limit = -1 # infinite
    packet_limit = 10
    pc.loop(packet_limit, recv_pkts) # capture packets

if __name__ == "__main__":
#    read_raw_from_stdin()
    read_from_pcapy()