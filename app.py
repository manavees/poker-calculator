
from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

# Deck of cards
suits = ['♠', '♥', '♦', '♣']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
deck = [rank + suit for suit in suits for rank in ranks]

def draw_random_cards(exclude, num):
    available_cards = [card for card in deck if card not in exclude]
    return random.sample(available_cards, num)

def simulate_win_probability(hole_cards, community_cards, num_opponents, num_simulations):
    wins, ties = 0, 0
    hole_cards_set = set(hole_cards)
    community_cards_set = set(community_cards)
    excluded_cards = hole_cards_set.union(community_cards_set)

    for _ in range(num_simulations):
        opponents_hands = [set(draw_random_cards(excluded_cards, 2)) for _ in range(num_opponents)]
        additional_community = draw_random_cards(excluded_cards.union(*opponents_hands), 5 - len(community_cards))
        player_hand_strength = random.randint(1, 7462)
        opponents_strengths = [random.randint(1, 7462) for _ in opponents_hands]

        if player_hand_strength > max(opponents_strengths):
            wins += 1
        elif player_hand_strength == max(opponents_strengths):
            ties += 1

    win_percentage = (wins / num_simulations) * 100
    tie_percentage = (ties / num_simulations) * 100
    loss_percentage = 100 - win_percentage - tie_percentage

    return {"win": win_percentage, "tie": tie_percentage, "lose": loss_percentage}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    hole_cards = data.get("hole_cards", [])
    community_cards = data.get("community_cards", [])
    num_opponents = int(data.get("num_opponents", 2))
    num_simulations = 10000

    result = simulate_win_probability(hole_cards, community_cards, num_opponents, num_simulations)
    return jsonify(result)

if __name__ == '__main__':
    app.run()
