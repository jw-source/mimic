from fast_graphrag import GraphRAG
from dotenv import load_dotenv

load_dotenv()

def search_knowledge(question):
    DOMAIN = "Analyze this Github repository to understand how an end-user would interact with this Python framework (e.g., how to use functions, classes, methods, examples, and documentation)."
    EXAMPLE_QUERIES = ['How can I define more detailed personas for the Allocator and Recipient, incorporating traits like risk aversion, fairness preferences, or cultural background, to better reflect human decision-making in bargaining games?', 'How can I implement variable stake sizes in the Ultimatum Game simulation to test the effect of stake size (c) on offers and acceptance rates, as explored in the human experiments?', 'How can I extend the simulation to model multi-stage Ultimatum Games, including two-stage and multi-round versions, to examine the impact of game structure and repetition, as seen in BSS, Güth and Tietz, and NSS experiments?', 'How can I incorporate a discount factor (δ) in multi-stage versions of the Ultimatum Game to simulate stake reduction in subsequent rounds and observe its influence on bargaining outcomes?', 'How can I model a more nuanced rejection mechanism in the Recipient agent that potentially includes emotional responses or justifications for rejecting offers, mirroring the human reactions to unfair proposals?', 'How can I implement a memory mechanism for the agents to track past game interactions and adjust their strategies over repeated plays to simulate learning or adaptation, as studied by GSS and Ochs and Roth?', 'How can I manipulate the perceived "earning" of the Allocator role, for example, by simulating a pre-game task or competition, to test the effect of role determination on offer generosity, as in Hoffman and Spitzer\'s work?', "How can I add mechanisms for agents to provide post-game justifications or reflections on their decisions, perhaps through a 'THINK' action or a dedicated utility, to capture qualitative data similar to post-experiment interviews?", "How can I use TinyTroupe's utilities to automatically extract and analyze key metrics from the simulation, such as mean offer amounts, rejection rates, and agent earnings, to quantitatively compare simulation results with human experiment data?", 'How can I introduce contextual variations into the simulation environment, such as manipulating the framing of the game or adding social cues, to examine their influence on fairness perceptions and bargaining behavior, similar to contextual effects observed in human studies?']
    ENTITY_TYPES = ["Parameters", "Functions", "Methods", "Classes", "Objects", "Examples", "Documentation"]
    grag = GraphRAG(
        working_dir="./knowledge",
        domain=DOMAIN,
        example_queries="\n".join(EXAMPLE_QUERIES),
        entity_types=ENTITY_TYPES
    )

    with open("./knowledge/code.txt") as f:
        grag.insert(f.read())
    
    return grag.query(question).response

if __name__ == "__main__":
    question = "How do I make a new persona with personality. Return me the code"
    response = search_knowledge(question)
    print(response)