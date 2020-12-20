import yaml
import json
import random
import itertools
import sys
import os
import re

adm_ideas = []
adm_max_level = 0
dip_ideas = []
dip_max_level = 0
mil_ideas = []
mil_max_level = 0
idea_costs = {}
position_modifier = [2.0, 2.0, 2.0, 1.8, 1.6, 1.4, 1.2, 1.0, 1.0, 1.0]
translations = {}

def loadIdeas(config_yaml):
    with open(config_yaml, "r", encoding="utf-8") as ideas_file:
        ideas_data = yaml.safe_load(ideas_file)
        for idea_type in ideas_data:
            with open(ideas_data[idea_type], "r") as idea_file:
                idea_json = json.load(idea_file)
                for type in idea_json:
                    for idea in idea_json[type]:
                        if(not idea == "category"):
                            idea_costs[idea] = {}
                            idea_costs[idea][1] = 0
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

def getTranslations(language):
    if(language == "english"):
        translations["traditions"] = "Traditions"
        translations["ideas"] = "Ideas"
        translations["ambitions"] = "Ambitions"
        translations["iterations"] = "Iterations"
        translations["costs"] = "Costs"
    elif(language == "french"):
        translations["traditions"] = "Traditions"
        translations["ideas"] = "Doctrines"
        translations["ambitions"] = "Ambitions"
        translations["iterations"] = "Iterations"
        translations["costs"] = "Couts"
    elif(language == "german"):
        translations["traditions"] = "Traditionen"
        translations["ideas"] = "Ideen"
        translations["ambitions"] = "Ambitionen"
        translations["iterations"] = "Iterationen"
        translations["costs"] = "Kosten"
    elif(language == "spanish"):
        translations["traditions"] = "Tradiciones"
        translations["ideas"] = "Ideas"
        translations["ambitions"] = "Ambiciones"
        translations["iterations"] = "Iteratione"
        translations["costs"] = "Costos"

    for file in os.listdir("localisations/" + language):
        if(file.endswith(".yml")):
            with open("localisations/" + language + "/" + file, "r", encoding="utf-8") as language_file:
                for line in language_file.readlines():
                    stripped_line = line.strip()
                    if(stripped_line and not (stripped_line.startswith("\ufeffl_") or stripped_line.startswith("#"))):
                        regex_line = re.split(":[0-9]* \"", stripped_line[:-1])
                        translations[regex_line[0].lower()] = regex_line[1]

def getRandomIdeas(min_cost, max_cost, iterations):
    chosen_ideas = [None] * 10
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

        adm_max_level = -sys.maxsize - 1
        dip_max_level = -sys.maxsize - 1
        mil_max_level = -sys.maxsize - 1
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
        if(overloaded or over_under_cost or counter < iterations):
            chosen_ideas = [None] * 10
        else:
            print(translations["iterations"] + ": " + str(counter))
            print(translations["costs"] + ": " + str("{:.1f}".format(current_cost)))
            return chosen_ideas

if __name__ == "__main__":
    loadIdeas("ideas.yaml")
    getTranslations("german")
    translated_chosen_ideas = [None] * 10
    chosen_ideas = getRandomIdeas(175, 175, 100)
    for idea_pos in range(len(chosen_ideas)):
        type = None
        if(idea_pos == 0):
            type = translations["traditions"]
        elif(idea_pos == 2):
            type = translations["ideas"]
        elif(idea_pos == 9):
            type = translations["ambitions"]
        else:
            type = None

        if(type != None):
            print(" " + type + ":")

        category = None
        if(chosen_ideas[idea_pos][0] + "-" + str(chosen_ideas[idea_pos][1]) in adm_ideas):
            category = "ADM"
        elif(chosen_ideas[idea_pos][0] + "-" + str(chosen_ideas[idea_pos][1]) in dip_ideas):
            category = "DIP"
        elif(chosen_ideas[idea_pos][0] + "-" + str(chosen_ideas[idea_pos][1]) in mil_ideas):
            category = "MIL"

        try:
            print("\t" + translations[chosen_ideas[idea_pos][0]] + " --> Level: " + str(chosen_ideas[idea_pos][1]) + "  (" + category + ")")
        except:
            print("\t" + chosen_ideas[idea_pos][0] + " --> Level: " + str(chosen_ideas[idea_pos][1]) + "  (" + category + ")")
