import numpy as np
import pandas as pd
from tinytroupe.agent import TinyPerson
from tinytroupe.environment import TinyWorld
from datetime import timedelta

def calculate_coefficient_of_convergence(prices, equilibrium_price):
    if not prices:
        return np.nan
    squared_diffs = [(p - equilibrium_price)**2 for p in prices]
    mean_squared_diff = np.mean(squared_diffs)
    coefficient = np.sqrt(mean_squared_diff) / equilibrium_price
    return coefficient

def run_llm_market_experiment():
    world = TinyWorld("Double Auction Market")
    buyers = []
    sellers = []
    buyer_values = [3.25, 3.00, 2.75, 2.50, 2.25, 2.00, 1.75, 1.50, 1.25, 1.00, 0.75]
    seller_costs = [0.75, 1.00, 1.25, 1.50, 1.75, 2.00, 2.25, 2.50, 2.75, 3.00, 3.25]

    for i in range(11):
        buyer = TinyPerson(name=f"Buyer_{i+1}", role="buyer", value=buyer_values[i])
        seller = TinyPerson(name=f"Seller_{i+1}", role="seller", cost=seller_costs[i])
        buyers.append(buyer)
        sellers.append(seller)
        world.add_agent(buyer)
        world.add_agent(seller)

    world.make_everyone_accessible()

    num_rounds = 5
    equilibrium_price = 2.00
    transaction_history = []
    convergence_coefficients = []
    exchange_quantities_history = []

    for round_num in range(num_rounds):
        print(f"\n--- Round {round_num + 1} ---")
        round_transactions = []
        potential_transactions = []

        buyer_offers = {}
        seller_asks = {}

        world.broadcast(f"It is the beginning of trading day {round_num + 1}. Previous day's average transaction price was ${np.mean([trans['price'] for trans in round_transactions] if round_transactions else [equilibrium_price]):.2f}. Buyers, please post your bids. Sellers, please post your asks.")

        for buyer in buyers:
            bid_prompt = "Post your bid for today. As a buyer, you want to buy at the lowest possible price, but not so low that sellers reject your bid considering your value card is $" + str(buyer.get('value')) + ". Consider also the previous day's price."
            bid_action = buyer.listen_and_act(bid_prompt)
            bid_price_str = bid_action[0]['value'] if bid_action and bid_action[0]['value'] else "None"
            try:
                bid_price = float(bid_price_str.strip('$')) if bid_price_str and bid_price_str != "None" else None
                if bid_price is not None and bid_price >= 0:
                    buyer_offers[buyer.name] = bid_price
                    print(f"{buyer.name} bids ${bid_price:.2f}")
                else:
                    print(f"{buyer.name} made an invalid bid.")
                    buyer_offers[buyer.name] = None
            except ValueError:
                print(f"{buyer.name} made an invalid bid.")
                buyer_offers[buyer.name] = None


        for seller in sellers:
            ask_prompt = "Post your ask for today. As a seller, you want to sell at the highest possible price, but not so high that buyers reject your ask considering your cost card is $" + str(seller.get('cost')) + ". Consider also the previous day's price."
            ask_action = seller.listen_and_act(ask_prompt)
            ask_price_str = ask_action[0]['value'] if ask_action and ask_action[0]['value'] else "None"
            try:
                ask_price = float(ask_price_str.strip('$')) if ask_price_str and ask_price_str != "None" else None
                if ask_price is not None and ask_price >= 0:
                    seller_asks[seller.name] = ask_price
                    print(f"{seller.name} asks ${ask_price:.2f}")
                else:
                    print(f"{seller.name} made an invalid ask.")
                    seller_asks[seller.name] = None
            except ValueError:
                print(f"{seller.name} made an invalid ask.")
                seller_asks[seller.name] = None

        potential_transactions = []
        for buyer in buyers:
            for seller in sellers:
                bid = buyer_offers.get(buyer.name)
                ask = seller_asks.get(seller.name)
                if bid is not None and ask is not None and bid >= ask:
                    potential_transactions.append({'buyer': buyer, 'seller': seller, 'price': (bid + ask) / 2})

        potential_transactions.sort(key=lambda trans: trans['price'], reverse=True)

        matched_buyers = set()
        matched_sellers = set()
        current_round_transactions = []

        for transaction in potential_transactions:
            buyer = transaction['buyer']
            seller = transaction['seller']
            price = transaction['price']

            if buyer.name not in matched_buyers and seller.name not in matched_sellers:
                if buyer.get('value') >= price and seller.get('cost') <= price:
                    round_transactions.append({'buyer': buyer.name, 'seller': seller.name, 'price': price})
                    current_round_transactions.append(price)
                    matched_buyers.add(buyer.name)
                    matched_sellers.add(seller.name)
                    print(f"Transaction: {buyer.name} bought from {seller.name} at ${price:.2f}")

        transaction_history.append(round_transactions)
        exchange_quantity = len(round_transactions)
        exchange_quantities_history.append(exchange_quantity)
        convergence_coefficient = calculate_coefficient_of_convergence(current_round_transactions, equilibrium_price)
        convergence_coefficients.append(convergence_coefficient)

        print(f"Round {round_num + 1} Summary: Transactions: {exchange_quantity}, Avg. Price: ${np.mean(current_round_transactions) if current_round_transactions else 0:.2f}, Convergence Coeff: {convergence_coefficient:.2f}")

    print("\n--- Experiment Summary ---")
    avg_prices_per_round = [np.mean([trans['price'] for trans in round_txns]) if round_txns else 0 for round_txns in transaction_history]
    convergence_df = pd.DataFrame({
        'Round': range(1, num_rounds + 1),
        'Avg_Transaction_Price': avg_prices_per_round,
        'Exchange_Quantity': exchange_quantities_history,
        'Convergence_Coefficient': convergence_coefficients
    })
    print(convergence_df)

    return convergence_df

if __name__ == '__main__':
    results_df = run_llm_market_experiment()
    print("\nExperiment completed. Results DataFrame is returned.")
