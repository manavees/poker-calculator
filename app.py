from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

# Full deck of cards
suits = ['♠', '♥', '♦', '♣']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
deck = [rank + suit for rank in ranks for suit in suits]


def validate_card(card):
    """Validate a single card input to ensure it is in the format AH, KS, etc."""
    card = card.strip().upper()
    if len(card) == 2 and card[0] in ranks and card[1] in suits:
        return card
    raise ValueError(f"Invalid card input: {card}")


def draw_random_cards(exclude, num):
    """Draw random cards from the deck, excluding specific cards."""
    available_cards = [card for card in deck if card not in exclude]
    return random.sample(available_cards, num)


def simulate_win_probability(hole_cards, community_cards, num_opponents, num_simulations):
    """Simulate win probability using Monte Carlo simulation."""
    wins, ties = 0, 0
    excluded_cards = set(hole_cards + community_cards)

    for _ in range(num_simulations):
        # Generate random opponent hands
        opponents_hands = [draw_random_cards(excluded_cards, 2) for _ in range(num_opponents)]
        excluded_cards.update([card for hand in opponents_hands for card in hand])

        # Generate remaining community cards
        remaining_community = draw_random_cards(excluded_cards, 5 - len(community_cards))
        full_community = community_cards + remaining_community

        # Simulate hand strengths (simple random values for now)
        player_hand_strength = random.randint(1, 7462)
        opponent_strengths = [random.randint(1, 7462) for _ in opponents_hands]

        # Compare hand strengths
        if player_hand_strength > max(opponent_strengths):
            wins += 1
        elif player_hand_strength == max(opponent_strengths):
            ties += 1

    win_percentage = (wins / num_simulations) * 100
    tie_percentage = (ties / num_simulations) * 100
    loss_percentage = 100 - win_percentage - tie_percentage

    return {"win": win_percentage, "tie": tie_percentage, "lose": loss_percentage}


@app.route('/')
def index():
    """Render the main HTML page."""
    return render_template('index.html')


@app.route('/calculate', methods=['POST'])
def calculate():
    """Handle POST requests to calculate probabilities."""
    try:
        data = request.json
        # Get and validate hole cards
        hole_cards = [
            validate_card(data.get("hole_card_1", "")),
            validate_card(data.get("hole_card_2", ""))
        ]
        # Get and validate community cards
        community_cards = [
            validate_card(card) for card in [
                data.get("community_card_1", ""),
                data.get("community_card_2", ""),
                data.get("community_card_3", ""),
                data.get("community_card_4", ""),
                data.get("community_card_5", ""),
            ] if card.strip()  # Ignore empty fields
        ]
        num_opponents = int(data.get("num_opponents", 2))
        num_simulations = 10000

        # Simulate probabilities
        result = simulate_win_probability(hole_cards, community_cards, num_opponents, num_simulations)
        return jsonify(result)
    except Exception as e:
        print("Error:", str(e))  # Log the error for debugging
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True)
