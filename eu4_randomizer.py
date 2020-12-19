import yaml
import json
import random
import itertools

adm_ideas = []
adm_max_level = 0
dip_ideas = []
dip_max_level = 0
mil_ideas = []
mil_max_level = 0
idea_costs = {}
chosen_ideas = [None] * 10
position_modifier = [2.0, 2.0, 2.0, 1.8, 1.6, 1.4, 1.2, 1.0, 1.0, 1.0]

def loadIdeas(config_yaml):
    with open(config_yaml, "r") as ideas_file:
        ideas_data = yaml.safe_load(ideas_file)
        for idea_type in ideas_data:
            with open(ideas_data[idea_type], "r") as idea_file:
                idea_json = json.load(idea_file)
                for type in idea_json:
                    for idea in idea_json[type]:
                        idea_costs[idea] = {}
                        if(not "level_cost_1" in idea):
                            idea_costs[idea][1] = 0
                            if("_adm_" in type):
                                adm_ideas.append(idea + "-1")
                            elif("_dip_" in type):
                                dip_ideas.append(idea + "-1")
                            elif("_mil_" in type):
                                mil_ideas.append(idea + "-1")

                        for level in idea_json[type][idea]:
                            if("level_cost_" in level):
                                current_level = int(level.split("level_cost_")[1])
                                idea_costs[idea][current_level] = idea_json[type][idea][level]
                                if("_adm_" in type):
                                    adm_ideas.append(idea + "-" + str(current_level))
                                elif("_dip_" in type):
                                    dip_ideas.append(idea + "-" + str(current_level))
                                elif("_mil_" in type):
                                    mil_ideas.append(idea + "-" + str(current_level))

def getRandomIdeas(min_cost, max_cost):
    global chosen_ideas

    counter = 0
    while(True):
        idea_names = []
        for position in range(len(chosen_ideas)):
            while(True):
                taken_idea = random.choice(adm_ideas + dip_ideas + mil_ideas)
                idea_name = "-".join(taken_idea.split("-")[:-1])
                level = int(taken_idea.split("-")[-1])
                if(not idea_name in idea_names):
                    idea_names.append(idea_name)
                    chosen_ideas[position] = [idea_name, level]
                    break

        adm_max_level = -9223372036854775807 - 1
        dip_max_level = -9223372036854775807 - 1
        mil_max_level = -9223372036854775807 - 1
        current_cost = 0
        for position in range(len(chosen_ideas)):
            idea_name = chosen_ideas[position][0]
            level = chosen_ideas[position][1]
            current_cost += idea_costs[idea_name][level] * position_modifier[position]
            if(idea_name + "-" + str(level) in adm_ideas):
                adm_max_level += (10 * level) / max(idea_costs[idea_name].keys())
            elif(idea_name + "-" + str(level) in dip_ideas):
                dip_max_level += (10 * level) / max(idea_costs[idea_name].keys())
            elif(idea_name + "-" + str(level) in mil_ideas):
                mil_max_level += (10 * level) / max(idea_costs[idea_name].keys())

        overloaded = adm_max_level / (adm_max_level + dip_max_level + mil_max_level) > 0.5 or dip_max_level / (adm_max_level + dip_max_level + mil_max_level) > 0.5 or mil_max_level / (adm_max_level + dip_max_level + mil_max_level) > 0.5
        over_under_cost = current_cost < min_cost or current_cost > max_cost
        counter += 1
        if(overloaded or over_under_cost):
            chosen_ideas = [None] * 10
        else:
            print("Iterations: " + str(counter))
            print("Cost: " + str(current_cost))
            break

if __name__ == "__main__":
    loadIdeas("ideas.yaml")
    print("Admin ideas: " + str(len(adm_ideas)))
    print("Diplomacy ideas: " + str(len(dip_ideas)))
    print("Millitary ideas: " + str(len(mil_ideas)))
    getRandomIdeas(300, 400)
    print(chosen_ideas)
