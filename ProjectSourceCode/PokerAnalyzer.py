import random
from itertools import combinations

# For this code, we need it to be fast.
# I've written this previously using loops, but because python is so ungodly slow, let's try and use bitwise.

# c1-13 (Clubs), d1-d13 (Diamonds), h1-h13 (Hearts), s1-s13 (Spades)
# Bit ordering:
# Clubs: Bits 0-12
# Diamonds: Bits 13-25
# Hearts: 26-38
# Spades: 39-51

# ---- CARD CONVERSIONS

# This  method will convert card notation ('c13', 'd7', 'h10') into bit position.
def card_to_bit(card_str):
    suit = card_str[0].lower() # Sets the suit to lower
    rank = int(card_str[1:]) # 1-13

    suit_bases = {
        'c': 0, # Clubs: 0-12
        'd': 13, # Diamonds: bits 13-25
        'h': 26, # Hearts: bits 26-38
        's': 39 # Spades: bits 39-51
    }

    return suit_bases[suit] + (rank - 1)

# This will take the value and set it correctly as a nested function
def card_bit_setting(card_str):
    return 1 << card_to_bit(card_str)

# This method will work as a way to make sure I'm not messing up bitwise math, and can convert back to cards.
def position_to_card(bitwise):
    suits = ['c', 'd', 'h', 's']
    index = bitwise // 13
    rank = (bitwise % 13) + 1
    return f"{suits[index]}{rank}"

# This will take in the bithands that we created earlier.
def bit_to_cards(hand_bits):
    cards = []
    for position in range(52):
        if hand_bits & (1 << position):
            cards.append(position_to_card(position))
    return cards

# ---- PARSING FUNCTIONS

# This breaks up the line of cards into hole, board, and full hand bits.
def card_parse(line):
    cards = line.strip().split()

    hole_card1 = card_bit_setting(cards[0])
    hole_card2 = card_bit_setting(cards[1])
    hole_cards = hole_card1 | hole_card2

    # These are board cards (flop, turn, and river)
    board = 0
    for card in cards[2:]:
        board |= card_bit_setting(card)

    # This will be good to know what cards we have
    all_cards = hole_cards | board

    # This will return three different values that we can use later
    return hole_cards, board, all_cards

# This method will be used for when we have a more structured format with pandas or something similar for data visualization.
# It will parse a list of cards into structured data.
def parse_card_list(cards_list):
    if len(cards_list) < 0:
        raise ValueError("Must provide at least 2 hole cards")

    hole_card1 = card_bit_setting(cards_list[0])
    hole_card2 = card_bit_setting(cards_list[1])
    hole_cards = hole_card1 | hole_card2

    board = 0
    for card in cards_list[2:]:
        board |= card_bit_setting(card)

    return {
        'hole': hole_cards,
        'board': board,
        'full': hole_cards | board
    }

def game_state(line):
    cards = line.strip().split()

    hole_cards = card_to_bit(cards[0]) | card_to_bit(cards[1])

    # This fills out the rest of the cards as bitwise for the board
    board_cards = [card_to_bit(c) for c in cards[2:]]
    board = 0
    for card in board_cards:
        board |= card

    # This is how we'll keep track of the game state
    num_board_cards = len(cards) - 2
    if num_board_cards == 0:
        state = "pre-flop"
    elif num_board_cards == 3:
        state = "flop"
    elif num_board_cards == 4:
        state = "turn"
    elif num_board_cards == 5:
        state = "river"
    else:
        state = "This is an unknown state of poker."

    # This will return key-pair values that we can use later.
    return {
        'hole': hole_cards,
        'board': board,
        'full': hole_cards | board,
        'state': state,
        'num_cards': len(cards)
    }

# ---- VALIDATION

# This will check that whatever we got will be a valid number of cards.
def validation(hand_bits):
    num_cards = bin(hand_bits).count('1') # Puts it in binary equivalent and makes sure the number of occurences is at 1.
    return num_cards <= 7 # If there is less than seven then obviously it is a valid hand.

# ---- HAND EVALUATION

# This will find straights, return high card, or none if it can't detect.
def find_straight(rank_bits):
    # This is checking if we got broadway straight (the best straight)
    if (rank_bits & 0b1111100000000) == 0b1111100000000:
        return 12  # Ace high straight

    # This checks the other straights and ranks them
    for high_rank in range(12, 3, -1): # Starting from K down to 5
        straight = 0b11111 << (high_rank - 4) # Going over the bits again
        if (rank_bits & straight) == straight:
            return high_rank # This will return the highest value from the straight.


    if (rank_bits & 0b1000000001111) == 0b1000000001111:
        return 3 # 5 high (special case due to the wheel straight).

    return None

# When evaluating a hand, there's no real clean way of doing this I believe from just coding a detection, which is why we're using bitwise to make this fast.
def hand_strength(hand_bits):
    # Rank Creation
    ranks = [0] * 13
    for offset in [0, 13, 26, 39]: # We need to offset against the suit because they're in the bits. When in a loop like this, it starts at their starting position.
        for rank in range (13): # This is the rank
            if hand_bits & (1 << (offset + rank)):
                ranks[rank] += 1 # All of this is to tell us how many times a rank is detected.
                # ranks[0] = 4, this means that we would have four 2s.

    # Multiple card Checks

    # Defining if we have pairs, trips, or quads using the ranks we defined before.
    pairs = [r for r in range(13) if ranks[r] == 2]
    trips = [r for r in range(13) if ranks[r] == 3]
    quads = [r for r in range(13) if ranks[r] == 4]

    # Straight Checking
    # This is where we're getting our rank bits to have them all in order for checking.
    rank_bits = 0
    for rank in range(13):
        if ranks[rank] > 0: # If there is a number at a rank
            rank_bits |= (1 << rank)  # This sets our bits ready to be checked at that rank.

    # Low Straight Set (If ace present)
    if rank_bits & (1 << 12):
        rank_bits |= 1

    # This method we defined above.
    straight_rank = find_straight(rank_bits)
    has_straight = straight_rank is not None

    # Flush Checking
    has_flush = False
    suit_bits = 0 # This is for checking for straight flushes later.
    for offset in [0, 13, 26, 39]:
        mask = 0x1FFF << offset # Each suit needs 13 bits. We're going to position those 13 bits over the suit.
        # 0x1FFF = 13 ones in binary
        suit_cards = (hand_bits & mask) >> offset # With the mask set + bits, we can overlay the bits to see which ones will result a 1. If it's a 1, that means the suit is there.
        if bin(suit_cards).count('1') >= 5: # If there are 5+ suited cards, that means there is a flush.
            has_flush = True
            suit_bits = suit_cards
            break

    # Finally evaluating hands to return values. We need to go top to down, otherwise the code will return the lowest value:

    # Straight Flush (8)
    if has_flush and has_straight:
        sf_rank = find_straight(suit_bits)
        if sf_rank is not None:
            return (8, sf_rank)

    # Four of a Kind (7)
    if quads:
        kicker = max([r for r in range(13) if ranks[r] > 0 and r not in quads])
        return (7, (quads[0], kicker))

    # Full House (6)
    if trips and pairs:
        return (6, (trips[0], pairs[0]))

    # Flush (5)
    if has_flush:
        flush_ranks = [r for r in range(12, -1, -1) if suit_bits & (1 << r)][:5]
        return (5, tuple(flush_ranks))

    # Straight (4)
    if has_straight:
        return (4, straight_rank)

    # Three of a Kind (3)
    if trips:
        kickers = sorted([r for r in range(13) if ranks[r] > 0 and r not in trips], reverse=True)[:2]
        return (3, (trips[0], *kickers))

    # Two Pair (2)
    if len(pairs) >= 2:
        top_pairs = sorted(pairs, reverse=True)[:2]
        kickers = [r for r in range(12, -1, -1) if ranks[r] > 0 and r not in top_pairs]
        kicker = kickers[0] if kickers else 0
        return (2, (*top_pairs, kicker))

    # One Pair (1)
    if pairs:
        kickers = sorted([r for r in range(13) if ranks[r] > 0 and r not in pairs], reverse=True)[:3]
        return (1, (pairs[0], *kickers))

    # High Card (0)
    high_cards = sorted([r for r in range(13) if ranks[r] > 0], reverse=True)[:5]
    return (0, tuple(high_cards))

# ---- SIMULATION FUNCTIONS

# This is how we're going to deal random cards. Knowing is fine because we're going to use it for simulations.
def deal_random(used_cards):
    while True:
        card_bit = random.randint(0, 51)
        card = 1 << card_bit
        if not (used_cards & card):
            return card

# This right here is why we tried to make our program as fast as possible. If we can do simulations fast, we can get good estimates.
def calculation_monte(hole_cards, board, num_simulations=10000):
    wins = 0
    ties = 0
    losses = 0

    # Cards already in play (can't be drawn again)
    used_cards = hole_cards | board

    board_cards = bin(board).count('1')
    cards_to_deal = 5 - board_cards # This is how we'll complete the board with cards.

    # HERE WE GO FOR SIMULATION TIMEEE
    for _ in range(num_simulations):
        sim_board = board
        sim_used = used_cards

        # This is how the board is dealt
        for _ in range(cards_to_deal):
            card = deal_random(sim_used)
            sim_board |= card
            sim_used |= card

        # Deals random cards from opponents.
        opponent_card1 = deal_random(sim_used)
        sim_used |= opponent_card1
        opponent_card2 = deal_random(sim_used)

        opponent_hole = opponent_card1 | opponent_card2

        # Evaluate both hands for which is better
        player_hand = hand_strength(hole_cards | sim_board)
        opponent_hand = hand_strength(opponent_hole | sim_board)

        # Do comparison to see who wins
        if player_hand > opponent_hand:
            wins += 1
        elif player_hand == opponent_hand:
            ties += 1
        else:
            losses += 1

    return {
        'wins': wins / num_simulations,
        'ties': ties / num_simulations,
        'losses': losses / num_simulations,
        'equity': (wins + ties * 0.5) / num_simulations
    }

def calculate_percentile(hole_cards, board):
    # I'm not going to enumerate over everything, because that's insane.
    # This is a form from sampling

    player_rank = hand_strength(hole_cards | board)

    used_cards = hole_cards | board
    better_hands = 0
    equal_hands = 0
    worse_hands = 0

    # Sampling from random opponent holdings
    samples =  1000
    for _ in range(samples):
        opponent_card1 = deal_random(used_cards)
        temp_used = used_cards | opponent_card1
        opponent_card2 = deal_random(temp_used)
        opponent_hand_rank = hand_strength(opponent_card1 | opponent_card2 | board)

        if opponent_hand_rank > player_rank:
            better_hands += 1
        elif opponent_hand_rank == player_rank:
            equal_hands += 1
        else:
            worse_hands += 1

    percentile = (worse_hands + equal_hands * 0.5) / samples
    return percentile

# ---- THREAT ANALYSIS

def threats_analysis(hole_cards, board):
    player_hand = hand_strength(hole_cards | board)
    player_type = player_hand[0]

    threats = []

    board_ranks = []
    board_suits = [0, 0, 0, 0]

    for offset, suit_index in [(0, 0), (13, 1), (26, 2), (39, 3)]:
        for rank in range(13):
            if board & (1 << (offset + rank)):
                board_ranks.append(rank)
                board_suits[suit_index] += 1

    # Flush Draws
    if max(board_suits) >= 3:
        threats.append(f"Possible Flush (board has {max(board_suits)} of same suit")

    # Straight Draws
    if max(board_ranks) >= 3:
        sorted_ranks = sorted(set(board_ranks))
        max_gap = max([sorted_ranks[i+1] - sorted_ranks[i] for i in range(len(sorted_ranks)-1)])
        if max_gap <= 2:
            threats.append("Possible Straight (connected board)")

    # Check for pairs/trips on board
    rank_counts = {}
    for rank in board_ranks:
        rank_counts[rank] = rank_counts.get(rank, 0) + 1

    if 2 in rank_counts.values():
        threats.append("Board paired, possible full house or better")
    if 3 in rank_counts.values():
        threats.append("Board has trips, possible full house or quads.")

    # Hand Names
    hand_names = ["high card", "pair", "two pair", "three of a kind",
                  "straight", "flush", "full house", "four of a kind", "straight flush"]

    if player_type < 8:
        for better_type in range(player_type + 1, 9):
            threats.append(f"Any {hand_names[better_type]} will beat you")

    return threats

# ---- RECOMMENDATION LOGIC

def recommendation(equity, percentile):
    if equity > 0.65 and percentile > 0.75:
        return "You have a very strong hand in this position. Consider raising/betting aggressively"
    elif equity > 0.50 and percentile > 0.60:
        return "You have a okay strong hand in this position. Call or moderate bet"
    elif equity > 0.35:
        return "You have a weak hand in this position. Consider checking or folding to aggression."
    else:
        return "You have a very weak hand in this position. Folding is highly advised."

# ---- MAIN ANALYSIS FUNCTION

def analyze_hand(hole_cards, board):

    player_hand = hand_strength(hole_cards | board)
    hand_names = ["high card", "pair", "two pair", "three of a kind",
                  "straight", "flush", "full house", "four of a kind", "straight flush"]

    equity = calculation_monte(hole_cards, board, num_simulations=5000)
    percentile = calculate_percentile(hole_cards, board)
    threats = threats_analysis(hole_cards, board)

    return {
        'current_hand' : {
            'type': hand_names[player_hand[0]],
            'type_rank': player_hand[0],
            'value': player_hand[1],
        },
        'equity': equity['equity'],
        'win_probability': equity['wins'],
        'percentile': percentile,
        'threats': threats,
        'recommendations': recommendation(equity['equity'], percentile)
    }

# ---- FILE I/O

# This opens/reads the cards file that Dante created
def read_poker_hands(file):
    hands = [] # Important for saving data later

    with open(file, 'r') as f: # Reading the file just so we're not modifying data.
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            try:
                hole, board, full = card_parse(line)
                hands.append({
                    'hole': hole,
                    'board': board,
                    'full': full,
                    'raw_line': line
                })
            except (IndexError, ValueError, KeyError) as e:
                print(f"Error parsing line: {line} - {e}")
                continue

    return hands

# ---- UTILITY

# This will get the name of the hand type from its positional rank (0-8):
def get_hand_names(hand_rank):
    names = ["High Card", "Pair", "Two Pair", "Three of a Kind", "Straight", "Flush", "Full House", "Four of a Kind", "Straight Flush"]
    return names[hand_rank] if 0 <= hand_rank <= 8 else "Unknown"

# This converts the suit + rank notation we've been using into a more readable format.
def format_cards(card_string):
    suit = card_string[0].lower()
    rank = int(card_string[1])

    suit_symbols = {
        'c': '♣',
        'd': '♦',
        'h': '♥',
        's': '♥'
    }

    rank_names = {
        '1': '2',
        '2': '3',
        '3': '4',
        '4': '5',
        '5': '6',
        '6': '7',
        '7': '8',
        '8': '9',
        '9': '10',
        '10': 'J',
        '11': 'Q',
        '12': 'K',
        '13': 'A'
    }

    return f"{rank_names[rank]}{suit_symbols[suit]}"


# read_poker_hands activates which is reading the txt file of the cards.
# Once the file is open, we parse the data into card_parse from the file's line of cards.
# In card_parse we clarify the information for what is the hold cards and what is the board, but we also set the bits for each position using card_bit_setting()
# Once in card_bit_setting, we return the value of the bitwise math of whatever the card was using card_to_bit which gives us an integer value of what the card is.

# Basically, method order is going: read_poker_hands() --> card_parse() --> card_bit_setting() --> card_to_bit

# Once card_to_bit is activated, we do the simulations of the boards throughout.

# In conclusion, this is getting out all of that data for us to use effectively in bitwise.
def run():
    print("------POKER HAND ANALYZER------\n")

    filename = "cards.txt"

    # Load hands
    try:
        hands = read_poker_hands(filename)
        print(f"Loaded {len(hands)} hand(s) from {filename}\n")
    except FileNotFoundError:
        print(f"Missing file: {filename}")
        print("Create a file with lines like:")
        print("  s13 s12 h10 h11 h12 d5 c3")
        return
    except Exception as e:
        print("Error reading file:", e)
        return

    # Analyze each hand
    for i, hand in enumerate(hands, 1):
        print(f"--- HAND #{i} ---")
        print(hand["raw_line"])

        hole = bit_to_cards(hand["hole"])
        board = bit_to_cards(hand["board"])

        print(f"Hole:  {', '.join(hole)}")
        print(f"Board: {', '.join(board) if board else '(none)'}")


        if not validation(hand["full"]):
            print("Invalid hand, duplicates or too many cards.\n")
            continue

        # Analyze
        try:
            analysis = analyze_hand(hand["hole"], hand["board"])
        except Exception as e:
            print("Error analyzing:", e)
            continue

        cur = analysis["current_hand"]

        print("\nCurrent Hand:")
        print(f"  Type: {cur['type']}")
        print(f"  Rank: {cur['type_rank']}/8")

        print("\nStats:")
        print(f"  Win %:      {analysis['win_probability']:.1%}")
        print(f"  Equity:     {analysis['equity']:.1%}")
        print(f"  Percentile: {analysis['percentile']:.1%}")

        print("\nThreats:")
        if analysis["threats"]:
            for t in analysis["threats"]:
                print("  -", t)
        else:
            print("  None")

        print("\nRecommendation:")
        print(" ", analysis["recommendations"])

        print("\nInterpretation:")
        eq = analysis["equity"]
        if eq > 0.65:
            print(" Strong hand. Bet/raise.")
        elif eq > 0.50:
            print(" Decent hand. Play cautiously.")
        elif eq > 0.35:
            print(" Weak hand. Consider pot odds.")
        else:
            print(" Very weak. Usually fold.")

        print()

    print("ANALYSIS COMPLETE")


# Automatically run when file is executed
run()