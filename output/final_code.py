import os
from dotenv import load_dotenv
import random

load_dotenv()

from tinytroupe.agent import TinyPerson
from tinytroupe.environment import TinyWorld
from tinytroupe.extraction import ArtifactExporter

exporter = ArtifactExporter(base_output_folder="./ultimatum_game_outputs/")
output_file = os.path.join(exporter.base_output_folder, "ultimatum_game_results.txt")

num_trials = 50
stake = 10.0
offers_made = []
rejection_counts = 0
positive_offer_rejection_counts = 0
positive_offers_made_count = 0

world = TinyWorld(name="UltimatumGameWorld")

for trial in range(num_trials):
    proposer = TinyPerson(name=f"Proposer_{trial}")
    responder = TinyPerson(name=f"Responder_{trial}")
    world.add_agent(proposer)
    world.add_agent(responder)
    world.make_everyone_accessible()

    proposer_instruction = f"You are Player 1 in the Ultimatum Game. You have ${stake:.2f} to split with Player 2. Decide how much to offer Player 2. Player 2 can either accept or reject your offer. If Player 2 accepts, you both get the agreed amount. If Player 2 rejects, both of you get $0. Make your offer in the format: 'I offer Player 2 ${stake:.2f}'."
    proposer.listen_and_act(proposer_instruction)
    proposer_action = proposer.act()

    offer_amount = 0.0
    try:
        offer_str = [action['content'] for action in proposer_action if action['tool_code'] == 'DEFAULT_UTTERANCE'][0]
        start_index = offer_str.find('$') + 1
        end_index = offer_str.find(' ', start_index)
        offer_amount = float(offer_str[start_index:end_index])
    except:
        offer_amount = -1.0

    if offer_amount >= 0:
        offers_made.append(offer_amount)
        responder_instruction = f"You are Player 2 in the Ultimatum Game. Player 1 has offered you ${offer_amount:.2f} out of ${stake:.2f}. Do you accept or reject this offer? If you accept, you get ${offer_amount:.2f} and Player 1 gets the rest. If you reject, both of you get $0. Respond with 'I accept' or 'I reject'."
        responder.listen_and_act(responder_instruction)
        responder_action = responder.act()
        accept_reject_str = [action['content'] for action in responder_action if action['tool_code'] == 'DEFAULT_UTTERANCE'][0].lower()

        if "reject" in accept_reject_str:
            rejection_counts += 1
            if offer_amount > 0:
                positive_offer_rejection_counts += 1
                positive_offers_made_count += 1
        elif offer_amount > 0:
            positive_offers_made_count += 1


    world.reset()

avg_offer_percentage = (sum(offers_made) / (stake * len(offers_made))) * 100 if offers_made else 0
modal_offer = max(set(offers_made), default=0, key=offers_made.count) if offers_made else 0
rejection_rate = (rejection_counts / num_trials) * 100 if num_trials > 0 else 0
positive_offer_rejection_rate = (positive_offer_rejection_counts / positive_offers_made_count) * 100 if positive_offers_made_count > 0 else 0

evaluation_metrics = {
    "average_offer_percentage": f"{avg_offer_percentage:.2f}%",
    "modal_offer": f"${modal_offer:.2f}",
    "rejection_rate": f"{rejection_rate:.2f}%",
    "positive_offer_rejection_rate": f"{positive_offer_rejection_rate:.2f}%",
    "number_of_trials": num_trials,
    "stake_amount": f"${stake:.2f}"
}

with open(output_file, 'w') as f:
    f.write("Ultimatum Game Simulation Results:\n")
    for key, value in evaluation_metrics.items():
        f.write(f"{key}: {value}\n")

print("Simulation completed. Evaluation metrics saved to 'ultimatum_game_results.txt' in 'ultimatum_game_outputs' directory.")
