import os
import pandas as pd
from tinytroupe.agent import TinyPerson
from tinytroupe.environment import TinyWorld
import numpy as np

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"

def run_ultimatum_game_simulation(stake, num_trials):
    offers_proportions = []
    rejection_rates = []
    offered_amounts_list = []
    accepted_offers_list = []
    recipient_payoffs = []
    allocator_payoffs = []

    for _ in range(num_trials):
        world = TinyWorld()
        allocator = TinyPerson(name="Allocator")
        recipient = TinyPerson(name="Recipient")
        world.add_agent(allocator)
        world.add_agent(recipient)
        world.make_everyone_accessible()

        offer_prompt = f"You are the Allocator in an Ultimatum Game with a total stake of ${stake}. How much (in dollars, integer amount) do you offer to the Recipient?"
        allocator_response = allocator.listen_and_act(offer_prompt)

        offered_amount = 0
        if allocator_response and isinstance(allocator_response, list) and allocator_response:
            response_item = allocator_response[0]
            if isinstance(response_item, dict) and 'action_result' in response_item:
                try:
                    action_result = response_item['action_result']
                    offered_amount = int("".join(filter(str.isdigit, action_result)))
                except ValueError:
                    offered_amount = 0

        offered_amounts_list.append(offered_amount)
        offer_proportion = offered_amount / stake if stake > 0 else 0
        offers_proportions.append(offer_proportion)

        acceptance_prompt = f"You are the Recipient in an Ultimatum Game. The Allocator offered you ${offered_amount} out of ${stake}. Do you accept or reject this offer? Answer 'accept' or 'reject'."
        recipient_response = recipient.listen_and_act(acceptance_prompt)

        accepted = False
        recipient_payoff_trial = 0
        allocator_payoff_trial = 0
        if recipient_response and isinstance(recipient_response, list) and recipient_response:
            response_item = recipient_response[0]
            if isinstance(response_item, dict) and 'action_result' in response_item:
                if "accept" in response_item['action_result'].lower():
                    accepted = True
                    recipient_payoff_trial = offered_amount
                    allocator_payoff_trial = stake - offered_amount
                else:
                    recipient_payoff_trial = 0
                    allocator_payoff_trial = 0

        rejection_rates.append(not accepted)
        accepted_offers_list.append(accepted)
        recipient_payoffs.append(recipient_payoff_trial)
        allocator_payoffs.append(allocator_payoff_trial)

    avg_offer_proportion = np.mean(offers_proportions) if num_trials > 0 else 0
    rejection_rate = np.mean(rejection_rates) if num_trials > 0 else 0
    std_offer_proportion = np.std(offers_proportions) if num_trials > 0 else 0
    median_offer_proportion = np.median(offers_proportions) if num_trials > 0 else 0
    avg_recipient_payoff = np.mean(recipient_payoffs) if num_trials > 0 else 0
    avg_allocator_payoff = np.mean(allocator_payoffs) if num_trials > 0 else 0

    return (avg_offer_proportion, rejection_rate, std_offer_proportion, median_offer_proportion,
            offers_proportions, rejection_rates, offered_amounts_list, accepted_offers_list,
            avg_recipient_payoff, avg_allocator_payoff, recipient_payoffs, allocator_payoffs)

stake_levels = [4, 10]
num_trials_per_stake = 50
simulation_results = {}

for stake in stake_levels:
    (avg_offer_proportion, rejection_rate, std_offer_proportion, median_offer_proportion,
     offers_proportions, rejection_rates, offered_amounts_list, accepted_offers_list,
     avg_recipient_payoff, avg_allocator_payoff, recipient_payoffs, allocator_payoffs) = run_ultimatum_game_simulation(stake, num_trials_per_stake)
    simulation_results[stake] = {
        "average_offer_proportion": avg_offer_proportion,
        "rejection_rate": rejection_rate,
        "std_offer_proportion": std_offer_proportion,
        "median_offer_proportion": median_offer_proportion,
        "offer_proportions": offers_proportions,
        "rejection_decisions": rejection_rates,
        "offered_amounts": offered_amounts_list,
        "accepted_offers": accepted_offers_list,
        "average_recipient_payoff": avg_recipient_payoff,
        "average_allocator_payoff": avg_allocator_payoff,
        "recipient_payoffs": recipient_payoffs,
        "allocator_payoffs": allocator_payoffs
    }

print("Simulation Results:")
for stake, results in simulation_results.items():
    print(f"\nStake: ${stake}")
    print(f"  Average Offer Proportion: {results['average_offer_proportion']:.2f}")
    print(f"  Median Offer Proportion: {results['median_offer_proportion']:.2f}")
    print(f"  Std Dev Offer Proportion: {results['std_offer_proportion']:.2f}")
    print(f"  Rejection Rate: {results['rejection_rate']:.2f}")
    print(f"  Average Recipient Payoff: ${results['average_recipient_payoff']:.2f}")
    print(f"  Average Allocator Payoff: ${results['average_allocator_payoff']:.2f}")

    offers_series = pd.Series(results['offer_proportions'])
    offer_distribution = offers_series.value_counts(bins=10, normalize=True).sort_index()
    print("\n  Offer Proportion Distribution:")
    print(offer_distribution)

    accepted_offers_series = pd.Series(results['accepted_offers'])
    acceptance_rate = accepted_offers_series.value_counts(normalize=True)
    print("\n  Acceptance Rate:")
    print(acceptance_rate)

    offer_amounts_series = pd.Series(results['offered_amounts'])
    descriptive_stats_offers = offer_amounts_series.describe()
    print("\n  Descriptive Statistics of Offered Amounts:")
    print(descriptive_stats_offers)
