if __name__ == "__main__":
    import yaml
    import json
    import random
    import itertools
    import sys
    import os
    import re
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    from tkinter.font import Font
    import traceback

    root = None

    class Application(tk.Frame):

        def __init__(self, master=None):
            self.adm_ideas = []
            self.dip_ideas = []
            self.mil_ideas = []
            self.idea_costs = {}
            self.cultures = {}
            self.all_cultures = []
            self.religions = ["christian-catholic", "christian-protestant", "christian-reformed", "christian-orthodox", "christian-coptic", "christian-anglican", "christian-hussite",
                              "muslim-sunni", "muslim-shiite", "muslim-ibadi",
                              "eastern-mahayana", "eastern-buddhism", "eastern-vajrayana", "eastern-confucianism", "eastern-shinto",
                              "dharmic-hinduism", "dharmic-sikhism",
                              "pagan-animism", "pagan-shamanism", "pagan-totemism", "pagan-inti", "pagan-nahuatl", "pagan-mesoamerican_religion", "pagan-norse_pagan_reformed", "pagan-tengri_pagan_reformed",
                              "other-jewish", "other-zoroastrian"]
            self.technologies = ["western", "high_american", "eastern", "anatolia_region_adj", "muslim", "indian", "east_african", "chinese", "west_african",
                                 "central_african", "nomad_group", "mesoamerican", "andean", "north_american", "south_american"]
            self.governments = {}
            self.translations = {}
            try:
                self.loadCultures("../../cultures/00_cultures.json")
            except FileNotFoundError as fnfe:
                self.loadCultures("cultures/00_cultures.json")

            try:
                self.loadGovernments("../../governments/")
            except FileNotFoundError as fnfe:
                self.loadGovernments("governments/")

            try:
                self.loadIdeas("../../ideas/ideas.yaml")
            except FileNotFoundError as fnfe:
                self.loadIdeas("ideas/local_ideas.yaml")

            try:
                self.loadTranslations("english", "../../localisations/")
            except FileNotFoundError as fnfe:
                self.loadTranslations("english", "localisations/")

            tk.Frame.__init__(self, master)
            self.master = master
            self.initWindow()


        def initWindow(self):
            self.master.title("EU4 - Custom Nation - Idea Randomizer")
            ###############################
            self.language_frame = tk.LabelFrame(self.master, text=self.translations["gui_language"])
            languages = {"Sprache: Deutsch": "german", "Language: English": "english", "Idioma: Espanol": "spanish", "Langue: Francais": "french"}
            self.language_var = tk.StringVar()
            self.language_var.set("english")
            column = 0
            for (key, value) in languages.items():
                tk.Radiobutton(self.language_frame, text=key, variable=self.language_var, value=value, command=lambda:
                               self.changeLanguage(self.language_var.get())).grid(row=0, column=column, pady=5)
                column += 1

            self.language_frame.grid(row=0, column=0, pady=5)
            ###############################
            self.cost_frame = tk.LabelFrame(self.master, text=self.translations["gui_costs"], borderwidth=2, relief="groove")
            vcmd = (self.cost_frame.register(self.validateCostInput), "%P")
            self.min_cost_label = tk.Label(self.cost_frame, text=self.translations["gui_minimum"]+":")
            self.min_cost = tk.DoubleVar()
            self.min_cost.set(50)
            self.min_cost_entry = tk.Entry(self.cost_frame, textvariable=self.min_cost, validate="key", validatecommand=vcmd)
            self.max_cost_label = tk.Label(self.cost_frame, text=self.translations["gui_maximum"]+":")
            self.max_cost = tk.DoubleVar()
            self.max_cost.set(800)
            self.max_cost_entry = tk.Entry(self.cost_frame, textvariable=self.max_cost, validate="key", validatecommand=vcmd)
            self.min_cost_label.grid(row=0, column=0, pady=5, padx=(5, 20))
            self.max_cost_label.grid(row=0, column=2, pady=5, padx=(5, 20))
            self.min_cost_entry.grid(row=0, column=1, pady=5, padx=(5, 30))
            self.max_cost_entry.grid(row=0, column=3, pady=5)
            self.cost_frame.grid(row=1, column=0, pady=5)
            ###############################
            self.iter_frame = tk.LabelFrame(self.master, text=self.translations["gui_iterations"], borderwidth=2, relief="groove")
            vcmd = (self.cost_frame.register(self.validateIterationInput), "%P")
            self.min_iter_label = tk.Label(self.iter_frame, text=self.translations["gui_minimum"]+":")
            self.min_iter = tk.DoubleVar()
            self.min_iter.set(1000)
            self.min_iter_entry = tk.Entry(self.iter_frame, textvariable=self.min_iter, validate="key", validatecommand=vcmd)
            self.max_iter = tk.DoubleVar()
            self.max_iter.set(100000)
            self.max_iter_label = tk.Label(self.iter_frame, text=self.translations["gui_maximum"]+":")
            self.max_iter_entry = tk.Entry(self.iter_frame, textvariable=self.max_iter, validate="key", validatecommand=vcmd)
            self.min_iter_label.grid(row=0, column=0, pady=5, padx=(5, 20))
            self.max_iter_label.grid(row=0, column=2, pady=5, padx=(5, 20))
            self.min_iter_entry.grid(row=0, column=1, pady=5, padx=(5, 30))
            self.max_iter_entry.grid(row=0, column=3, pady=5)
            self.iter_frame.grid(row=2, column=0, pady=5)
            ###############################
            self.start_frame = tk.Frame(self.master,  borderwidth=2, relief="groove")
            self.start_button = tk.Button(self.start_frame, text=self.translations["gui_start"], command=lambda:
                                          self.startRandomizer(self.min_cost, self.max_cost, self.min_iter, self.max_iter))
            self.start_button.grid(row=0, column=0, padx=5)
            #############
            self.cost_label = tk.Label(self.start_frame, text=self.translations["gui_costs"]+":")
            self.cost_label.grid(row=0, column=1, pady=5, padx=1)
            self.cost = tk.DoubleVar()
            self.cost.set(0)
            self.cost_entry = tk.Entry(self.start_frame, textvariable=self.cost)
            self.cost_entry.config(state="readonly")
            self.cost_entry.grid(row=0, column=2, pady=5, padx=5)
            #############
            self.iter_label = tk.Label(self.start_frame, text=self.translations["gui_iterations"]+":")
            self.iter_label.grid(row=0, column=3, pady=5, padx=1)
            self.iter = tk.DoubleVar()
            self.iter.set(0)
            self.iter_entry = tk.Entry(self.start_frame, textvariable=self.iter)
            self.iter_entry.config(state="readonly")
            self.iter_entry.grid(row=0, column=4, pady=5, padx=5)
            self.start_frame.grid(row=3, column=0, pady=5)
            ###############################
            self.culture_frame = tk.LabelFrame(self.master, text=self.translations["gui_culture"])
            #############
            self.culture_label = tk.Label(self.culture_frame, text=self.translations["gui_culture"]+":")
            self.culture_label.grid(row=0, column=0, padx=1)
            self.culture = tk.StringVar()
            self.culture.set("")
            self.culture_entry = tk.Entry(self.culture_frame, textvariable=self.culture)
            self.culture_entry.config(state="readonly")
            self.culture_entry.grid(row=0, column=1, pady=5, padx=(5, 43))
            #############
            self.culture_group_label = tk.Label(self.culture_frame, text=self.translations["gui_group"]+":")
            self.culture_group_label.grid(row=0, column=2, padx=1)
            self.culture_group = tk.StringVar()
            self.culture_group.set("")
            self.culture_group_entry = tk.Entry(self.culture_frame, textvariable=self.culture_group)
            self.culture_group_entry.config(state="readonly")
            self.culture_group_entry.grid(row=0, column=3, pady=5)
            self.culture_frame.grid(row=4, column=0, pady=5)
            ###############################
            self.religion_frame = tk.LabelFrame(self.master, text=self.translations["gui_religion"])
            #############
            self.religion_label = tk.Label(self.religion_frame, text=self.translations["gui_religion"]+":")
            self.religion_label.grid(row=0, column=0, padx=1)
            self.religion = tk.StringVar()
            self.religion.set("")
            self.religion_entry = tk.Entry(self.religion_frame, textvariable=self.religion)
            self.religion_entry.config(state="readonly")
            self.religion_entry.grid(row=0, column=1, pady=5, padx=(5, 40))
            #############
            self.religion_group_label = tk.Label(self.religion_frame, text=self.translations["gui_group"]+":")
            self.religion_group_label.grid(row=0, column=2, padx=1)
            self.religion_group = tk.StringVar()
            self.religion_group.set("")
            self.religion_group_entry = tk.Entry(self.religion_frame, textvariable=self.religion_group)
            self.religion_group_entry.config(state="readonly")
            self.religion_group_entry.grid(row=0, column=3, pady=5)
            #############
            self.religion_frame.grid(row=5, column=0, pady=5)
            ###############################
            self.government_frame = tk.LabelFrame(self.master, text=self.translations["gui_government"])
            #############
            self.government_label = tk.Label(self.government_frame, text=self.translations["gui_government"]+":")
            self.government_label.grid(row=0, column=0, padx=1)
            self.government = tk.StringVar()
            self.government.set("")
            self.government_entry = tk.Entry(self.government_frame, textvariable=self.government)
            self.government_entry.config(state="readonly")
            self.government_entry.grid(row=0, column=1, pady=5, padx=(5, 20))
            #############
            self.government_group_label = tk.Label(self.government_frame, text=self.translations["gui_group"]+":")
            self.government_group_label.grid(row=0, column=2, padx=1)
            self.government_group = tk.StringVar()
            self.government_group.set("")
            self.government_group_entry = tk.Entry(self.government_frame, textvariable=self.government_group)
            self.government_group_entry.config(state="readonly")
            self.government_group_entry.grid(row=0, column=3, pady=5)
            #############
            self.government_frame.grid(row=6, column=0, pady=5)
            ###############################
            self.technology_frame = tk.LabelFrame(self.master, text=self.translations["gui_technology"])
            self.technology_label = tk.Label(self.technology_frame, text=self.translations["gui_technology"]+":")
            self.technology_label.grid(row=0, column=0, padx=1)
            self.technology = tk.StringVar()
            self.technology.set("")
            self.technology_entry = tk.Entry(self.technology_frame, textvariable=self.technology)
            self.technology_entry.config(state="readonly")
            self.technology_entry.grid(row=0, column=1, pady=5)
            self.technology_frame.grid(row=7, column=0, pady=5)
            ###############################
            self.grid_frame = tk.Frame(self.master)
            self.tree = ttk.Treeview(self.grid_frame, column=("level", "category"))
            self.tree.heading("#0", text=self.translations["gui_ideas"], anchor="center")
            self.tree.heading("#1", text=self.translations["gui_level"], anchor="center")
            self.tree.heading("#2", text=self.translations["gui_category"], anchor="center")
            self.tree.column("level", anchor="center")
            self.tree.column("category", anchor="center")
            ysb = ttk.Scrollbar(orient="vertical", command=self.tree.yview)
            xsb = ttk.Scrollbar(orient="horizontal", command=self.tree.xview)
            self.tree["yscroll"] = ysb.set
            self.tree["xscroll"] = xsb.set
            self.tree.grid(in_=self.grid_frame, row=0, column=0, sticky=tk.NSEW)
            ysb.grid(in_=self.grid_frame, row=0, column=1, sticky=tk.NS)
            xsb.grid(in_=self.grid_frame, row=1, column=0, sticky=tk.EW)
            self.tree.rowconfigure(0, weight=1)
            self.tree.columnconfigure(0, weight=1)
            self.grid_frame.grid(row=8, column=0, pady=5, sticky=tk.NSEW)
            self.master.rowconfigure(5, weight=1)
            self.master.columnconfigure(0, weight=1)
            self.grid_frame.rowconfigure(0, weight=1)
            self.grid_frame.columnconfigure(0, weight=1)


        def validateCostInput(self, input):
            if(len(input) == 0 or input[-1].isdigit() or (input[-1] == "." and input.count(".") == 1)):
                return True

            self.cost_frame.bell()
            return False


        def validateIterationInput(self, input):
            if(len(input) == 0 or input[-1].isdigit()):
                return True

            self.cost_frame.bell()
            return False


        def changeLanguage(self, language):
            self.translations = {}
            self.cost.set(0.0)
            self.iter.set(0)
            self.culture.set("")
            self.culture_group.set("")
            self.religion.set("")
            self.religion_group.set("")
            self.government.set("")
            self.government_group.set("")
            self.technology.set("")
            for i in self.tree.get_children():
                self.tree.delete(i)

            try:
                self.loadTranslations(language, "../../localisations/")
            except FileNotFoundError as fnfe:
                self.loadTranslations(language, "localisations/")

            self.language_frame.configure(text=self.translations["gui_language"])
            self.cost_frame.configure(text=self.translations["gui_costs"])
            self.min_cost_label.configure(text=self.translations["gui_minimum"])
            self.max_cost_label.configure(text=self.translations["gui_maximum"])
            self.iter_frame.configure(text=self.translations["gui_iterations"])
            self.min_iter_label.configure(text=self.translations["gui_minimum"])
            self.max_iter_label.configure(text=self.translations["gui_maximum"])
            self.start_button.configure(text=self.translations["gui_start"])
            self.cost_label.configure(text=self.translations["gui_costs"] + ":")
            self.iter_label.configure(text=self.translations["gui_iterations"] + ":")
            self.culture_frame.config(text=self.translations["gui_culture"] + ":")
            self.culture_group_label.config(text=self.translations["gui_group"] + ":")
            self.religion_frame.config(text=self.translations["gui_religion"] + ":")
            self.religion_label.config(text=self.translations["gui_religion"] + ":")
            self.religion_group_label.config(text=self.translations["gui_group"] + ":")
            self.government_frame.config(text=self.translations["gui_government"] + ":")
            self.government_label.config(text=self.translations["gui_government"] + ":")
            self.government_group_label.config(text=self.translations["gui_group"] + ":")
            self.technology_frame.config(text=self.translations["gui_technology"] + ":")
            self.technology_label.config(text=self.translations["gui_technology"] + ":")
            self.tree.heading("#0", text=self.translations["gui_ideas"], anchor="center")
            self.tree.heading("#1", text=self.translations["gui_level"], anchor="center")
            self.tree.heading("#2", text=self.translations["gui_category"], anchor="center")


        def loadGovernments(self, path):
            self.monarchies = []
            with open(path + "01_government_reforms_monarchies.json", "r", encoding="utf-8") as monarchies_file:
                self.monarchies.append(json.load(monarchies_file))

            self.republics = []
            with open(path + "02_government_reforms_republics.json", "r", encoding="utf-8") as republics_file:
                self.republics.append(json.load(republics_file))

            self.theocracies = []
            with open(path + "03_government_reforms_theocracies.json", "r", encoding="utf-8") as theocracies_file:
                self.theocracies.append(json.load(theocracies_file))

            self.tribes = []
            with open(path + "04_government_reforms_tribes.json", "r", encoding="utf-8") as tribes_file:
                self.tribes.append(json.load(tribes_file))

            self.natives = []
            with open(path + "05_government_reforms_natives.json", "r", encoding="utf-8") as natives_file:
                self.natives.append(json.load(natives_file))

            self.others = []
            with open(path + "06_government_reforms_common.json", "r", encoding="utf-8") as common_file:
                self.others.append(json.load(common_file))

            with open(path + "00_governments.json", "r", encoding="utf-8") as governments_file:
                governments_data = json.load(governments_file)
                for gov in list(governments_data.keys())[:-1]:
                    if("reform_levels" in governments_data[gov].keys()):
                        reform = list(governments_data[gov]["reform_levels"].keys())[0]
                        for gov in governments_data[gov]["reform_levels"][reform]["reforms"]:
                            for gov_type in self.monarchies+self.republics+self.theocracies+self.tribes+self.natives+self.others:
                                if(gov in gov_type):
                                    try:
                                        if(gov_type[gov]["valid_for_nation_designer"]):
                                            self.governments[gov] = {}
                                            if("nation_designer_cost" in gov_type[gov]):
                                                self.governments[gov]["costs"] = gov_type[gov]["nation_designer_cost"]
                                            else:
                                                self.governments[gov]["costs"] = 0

                                            if("nation_designer_trigger" in gov_type[gov]):
                                                for restriction in gov_type[gov]["nation_designer_trigger"]:
                                                    if(restriction == "OR"):
                                                        for inner_restriction in gov_type[gov]["nation_designer_trigger"][restriction]:
                                                            if(isinstance(inner_restriction, dict)):
                                                                for restriction_type, restriction_value in inner_restriction.items():
                                                                    restriction_type = restriction_type.replace("_group", "").replace("primary_", "")
                                                                    if(not restriction_type in self.governments[gov]):
                                                                        self.governments[gov][restriction_type] = []

                                                                    if(isinstance(restriction_value, list)):
                                                                        self.governments[gov][restriction_type].extend(restriction_value)
                                                                    else:
                                                                        self.governments[gov][restriction_type].append(restriction_value)
                                                            else:
                                                                restriction_type = inner_restriction.replace("_group", "").replace("primary_", "")
                                                                restriction_value = gov_type[gov]["nation_designer_trigger"][restriction][inner_restriction]
                                                                if(not restriction_type in self.governments[gov]):
                                                                    self.governments[gov][restriction_type] = []

                                                                if(isinstance(restriction_value, list)):
                                                                    self.governments[gov][restriction_type].extend(restriction_value)
                                                                else:
                                                                    self.governments[gov][restriction_type].append(restriction_value)
                                                    elif(restriction == "NOT"):
                                                        for inner_restriction in gov_type[gov]["nation_designer_trigger"][restriction]:
                                                            if(isinstance(inner_restriction, dict)):
                                                                for restriction_type, restriction_value in inner_restriction.items():
                                                                    if(not "not" in self.governments[gov]):
                                                                        self.governments[gov]["not"] = {}

                                                                    restriction_type = restriction_type.replace("_group", "").replace("primary_", "")
                                                                    if(not restriction_type in self.governments[gov]["not"]):
                                                                        self.governments[gov]["not"][restriction_type] = []

                                                                    self.governments[gov]["not"][restriction_type].append(restriction_value)
                                                            else:
                                                                if(not "not" in self.governments[gov]):
                                                                    self.governments[gov]["not"] = {}

                                                                restriction_type = inner_restriction.replace("_group", "").replace("primary_", "")
                                                                restriction_value = gov_type[gov]["nation_designer_trigger"][restriction][inner_restriction]
                                                                if(not restriction_type in self.governments[gov]["not"]):
                                                                    self.governments[gov]["not"][restriction_type] = []

                                                                self.governments[gov]["not"][restriction_type].append(restriction_value)
                                                    else:
                                                        restriction_type = restriction.replace("_group", "").replace("primary_", "")
                                                        if(not restriction_type in self.governments[gov]):
                                                            self.governments[gov][restriction_type] = []

                                                        self.governments[gov][restriction_type].append(gov_type[gov]["nation_designer_trigger"][restriction])
                                    except:
                                        pass
                    elif("basic_reform" in governments_data[gov].keys()):
                        gov = governments_data[gov]["basic_reform"]


        def loadIdeas(self, config_yaml):
            with open(config_yaml, "r", encoding="utf-8") as ideas_file:
                ideas_data = yaml.safe_load(ideas_file)
                for idea_type in ideas_data:
                    with open(ideas_data[idea_type], "r") as idea_file:
                        idea_json = json.load(idea_file)
                        for idea_type in idea_json:
                            for idea in idea_json[idea_type]:
                                if(idea == "custom_idea_female_advisor_chance"):
                                    self.idea_costs["female_advisor_chance"] = {}
                                    self.idea_costs["female_advisor_chance"][10] = 0
                                    self.adm_ideas.append("female_advisor_chance-10")
                                elif(not (idea == "category" or idea == "custom_idea_ship_recruit_speed" or idea == "custom_idea_regiment_recruit_speed")):
                                    self.idea_costs[idea] = {}
                                    self.idea_costs[idea][1] = 0
                                    idea_name = None
                                    first_item = True
                                    for level in idea_json[idea_type][idea]:
                                        if(first_item):
                                            idea_name = level.replace("received", "recieved")
                                            self.idea_costs[idea_name] = {}
                                            self.idea_costs[idea_name][1] = 0
                                            first_item = False

                                        elif("level_cost_" in level):
                                            current_level = int(level.split("level_cost_")[1])
                                            self.idea_costs[idea_name][current_level] = idea_json[idea_type][idea][level]
                                            if("adm" in idea_type):
                                                if(not idea_name + "-" + str(current_level) in self.adm_ideas):
                                                    self.adm_ideas.append(idea_name + "-" + str(current_level))
                                            elif("dip" in idea_type):
                                                if(not idea_name + "-" + str(current_level) in self.dip_ideas):
                                                    self.dip_ideas.append(idea_name + "-" + str(current_level))
                                            elif("mil" in idea_type):
                                                if(not idea_name + "-" + str(current_level) in self.mil_ideas):
                                                    self.mil_ideas.append(idea_name + "-" + str(current_level))

                                    if("adm" in idea_type and not idea_name + "-1" in self.adm_ideas):
                                        self.adm_ideas.append(idea_name + "-1")
                                    elif("dip" in idea_type and not idea_name + "-1" in self.dip_ideas):
                                        self.dip_ideas.append(idea_name + "-1")
                                    elif("mil" in idea_type and not idea_name + "-1" in self.mil_ideas):
                                        self.mil_ideas.append(idea_name + "-1")


        def loadCultures(self, path):
            with open(path, "r", encoding="utf-8") as culture_file:
                culture_data = json.load(culture_file)
                for culture_group in culture_data:
                    self.cultures[culture_group] = []
                    for culture in culture_data[culture_group]:
                        if(not (culture == "graphical_culture" or culture == "dynasty_names" or culture == "male_names" or culture == "female_names")):
                            self.cultures[culture_group].append(culture)
                            self.all_cultures.append(culture + "-" + culture_group)


        def loadTranslations(self, language, path):
            self.translations = {}
            if(language == "english"):
                self.translations["gui_traditions"] = "Traditions"
                self.translations["gui_ideas"] = "Ideas"
                self.translations["gui_ambitions"] = "Ambitions"
                self.translations["gui_iterations"] = "Iterations"
                self.translations["gui_costs"] = "Costs"
                self.translations["gui_minimum"] = "Minimum"
                self.translations["gui_maximum"] = "Maximum"
                self.translations["gui_start"] = "Start Randomizer"
                self.translations["gui_level"] = "Level"
                self.translations["gui_category"] = "Category"
                self.translations["gui_language"] = "Language"
                self.translations["gui_cul_rel"] = "Culture and Religion"
                self.translations["gui_culture"] = "Culture"
                self.translations["gui_group"] = "Group"
                self.translations["gui_religion"] = "Religion"
                self.translations["gui_government"] = "Government"
                self.translations["gui_technology"] = "Technology"
            elif(language == "french"):
                self.translations["gui_traditions"] = "Traditions"
                self.translations["gui_ideas"] = "Doctrines"
                self.translations["gui_ambitions"] = "Ambitions"
                self.translations["gui_iterations"] = "Iterations"
                self.translations["gui_costs"] = "Couts"
                self.translations["gui_minimum"] = "Minimaux"
                self.translations["gui_maximum"] = "Maximums"
                self.translations["gui_start"] = "Demarrer Le Randomizer"
                self.translations["gui_level"] = "Niveau"
                self.translations["gui_category"] = "Categorie"
                self.translations["gui_language"] = "Langue"
                self.translations["gui_cul_rel"] = "Culture et Religion"
                self.translations["gui_culture"] = "Culture"
                self.translations["gui_group"] = "Groupe"
                self.translations["gui_religion"] = "Religion"
                self.translations["gui_government"] = "Gouvernement"
                self.translations["gui_technology"] = "Technologie"
            elif(language == "german"):
                self.translations["gui_traditions"] = "Traditionen"
                self.translations["gui_ideas"] = "Ideen"
                self.translations["gui_ambitions"] = "Ambitionen"
                self.translations["gui_iterations"] = "Iterationen"
                self.translations["gui_costs"] = "Kosten"
                self.translations["gui_minimum"] = "Minimal"
                self.translations["gui_maximum"] = "Maximal"
                self.translations["gui_start"] = "Starte Zufallsgenerator"
                self.translations["gui_level"] = "Stufe"
                self.translations["gui_category"] = "Kategorie"
                self.translations["gui_language"] = "Sprache"
                self.translations["gui_culture"] = "Kultur"
                self.translations["gui_group"] = "Gruppe"
                self.translations["gui_religion"] = "Religion"
                self.translations["gui_government"] = "Regierung"
                self.translations["gui_technology"] = "Technologie"
            elif(language == "spanish"):
                self.translations["gui_traditions"] = "Tradiciones"
                self.translations["gui_ideas"] = "Ideas"
                self.translations["gui_ambitions"] = "Ambiciones"
                self.translations["gui_iterations"] = "Iteratione"
                self.translations["gui_costs"] = "Costos"
                self.translations["gui_minimum"] = "Minimos"
                self.translations["gui_maximum"] = "Maximos"
                self.translations["gui_start"] = "Iniciar Randomizer"
                self.translations["gui_level"] = "Nivel"
                self.translations["gui_category"] = "Categoria"
                self.translations["gui_language"] = "Idioma"
                self.translations["gui_cul_rel"] = "Cultura y Religion"
                self.translations["gui_culture"] = "Cultura"
                self.translations["gui_group"] = "Grupo"
                self.translations["gui_religion"] = "Religion"
                self.translations["gui_government"] = "Gobierno"
                self.translations["gui_technology"] = "Tecnología"


            for file in os.listdir(path + language):
                if(file.endswith(".yml")):
                    with open(path + language + "/" + file, "r", encoding="utf-8") as language_file:
                        for line in language_file.readlines():
                            stripped_line = line.strip()
                            if(stripped_line and not (stripped_line.startswith("\ufeffl_") or stripped_line.startswith("#"))):
                                regex_line = re.split(":[0-9]* \"", stripped_line[:-1])
                                regex_line[0] = regex_line[0].lower().replace("received", "recieved")
                                # substitute wrong labels in the localisation files
                                if(regex_line[0] == "modifier_justify_trade_conflict_time"):
                                    regex_line[0] = "justify_trade_conflict_cost"
                                elif(regex_line[0] == "modifier_fabricate_claims_time"):
                                    regex_line[0] = "fabricate_claims_cost"
                                elif(regex_line[0] == "regiment_cost"):
                                    regex_line[0] = "global_regiment_cost"
                                elif(regex_line[0] == "modifier_reinforce_cost"):
                                    regex_line[0] = "reinforce_cost_modifier"
                                elif(regex_line[0] == "modifier_trade_range"):
                                    regex_line[0] = "trade_range_modifier"
                                elif(regex_line[0] == "modifier_global_naval_engagement"):
                                    regex_line[0] = "global_naval_engagement_modifier"
                                elif(regex_line[0] == "modifier_sailor_maintenance"):
                                    regex_line[0] = "sailor_maintenance_modifer"
                                elif(regex_line[0] == "may_attack_primitives"):
                                    regex_line[0] = "cb_on_primitives"
                                elif(regex_line[0] == "idea_may_siberian_frontier"):
                                    regex_line[0] = "may_establish_frontier"
                                elif(regex_line[0] == "local_autonomy_mod"):
                                    regex_line[0] = "local_autonomy"
                                elif(regex_line[0] == "global_autonomy_mod"):
                                    regex_line[0] = "global_autonomy"
                                elif(regex_line[0] == "lightship_power"):
                                    regex_line[0] = "light_ship_power"
                                elif(regex_line[0] == "lightship_cost"):
                                    regex_line[0] = "light_ship_cost"
                                elif(regex_line[0] == "galleyship_power"):
                                    regex_line[0] = "galley_ship_power"
                                elif(regex_line[0] == "galleyship_cost"):
                                    regex_line[0] = "galley_ship_cost"
                                elif(regex_line[0] == "heavyship_power"):
                                    regex_line[0] = "heavy_ship_power"
                                elif(regex_line[0] == "heavyship_cost"):
                                    regex_line[0] = "heavy_ship_cost"
                                elif(regex_line[0] == "naval_leader_maneuver"):
                                    regex_line[0] = "leader_naval_manuever"
                                elif(regex_line[0] == "land_leader_maneuver"):
                                    regex_line[0] = "leader_land_manuever"
                                elif(regex_line[0] == "global_tariff_modifier"):
                                    regex_line[0] = "global_tariffs"
                                elif(regex_line[0] == "spy_global_defence"):
                                    regex_line[0] = "global_spy_defence"
                                elif(regex_line[0] == "modifier_colonial_range"):
                                    regex_line[0] = "range"
                                elif(regex_line[0] == "sailors_recovery"):
                                    regex_line[0] = "sailors_recovery_speed"
                                elif(regex_line[0] == "modifier_diplo_skill"):
                                    regex_line[0] = "diplomatic_reputation"
                                elif(regex_line[0] == "global_manpower"):
                                    regex_line[0] = "global_manpower_modifier"
                                elif(regex_line[0] == "manpower_recovery"):
                                    regex_line[0] = "manpower_recovery_speed"
                                elif(regex_line[0] == "global_sailors"):
                                    regex_line[0] = "global_sailors_modifier"
                                elif(regex_line[0] == "modifier_colonial_growth"):
                                    regex_line[0] = "global_colonial_growth"
                                elif(regex_line[0] == "modifier_accepted_cultures"):
                                    regex_line[0] = "num_accepted_cultures"

                                try:
                                    self.translations[regex_line[0]] = regex_line[1][0].upper() + regex_line[1][1:]
                                except:
                                    self.translations[regex_line[0]] = regex_line[1]


        def startRandomizer(self, min_cost, max_cost, min_iter, max_iter):
            self.start_button.config(state=tk.DISABLED)
            for button in self.language_frame.winfo_children():
                button.configure(state=tk.DISABLED)

            self.cost.set(0.0)
            self.iter.set(0)
            self.culture.set("")
            self.culture_group.set("")
            self.religion.set("")
            self.religion_group.set("")
            self.government.set("")
            self.government_group.set("")
            self.technology.set("")
            root.update()
            for i in self.tree.get_children():
                self.tree.delete(i)

            try:
                min_cost = float(min_cost.get())
                if(min_cost < 0):
                    min_cost = 50
                    self.min_cost.set(50)
            except:
                min_cost = 50
                self.min_cost.set(50)

            try:
                max_cost = float(max_cost.get())
                if(max_cost < 0):
                    max_cost = 800
                    self.max_cost.set(800)
            except:
                max_cost = 800
                self.max_cost.set(800)

            if(min_cost > max_cost):
                temp = min_cost
                min_cost = max_cost
                max_cost = temp
                self.min_cost.set(min_cost)
                self.max_cost.set(max_cost)

            try:
                min_iter = int(min_iter.get())
                if(min_iter < 0):
                    min_iter = 1000
                    self.min_iter.set(1000)
            except:
                min_iter = 1000
                self.min_iter.set(1000)

            try:
                max_iter = int(max_iter.get())
                if(max_iter < 0):
                    max_iter = 100000
                    self.max_iter.set(100000)
            except:
                max_iter = 100000
                self.max_iter.set(100000)

            if(min_iter > max_iter):
                temp = min_iter
                min_iter = max_iter
                max_iter = temp
                self.min_iter.set(min_iter)
                self.max_iter.set(max_iter)

            chosen_ideas = [None] * 10
            position_modifier = [2.0, 2.0, 2.0, 1.8, 1.6, 1.4, 1.2, 1.0, 1.0, 1.0]
            counter = 0
            self.idea_icons = [None] * 10
            while(True):
                culture = random.choice(self.all_cultures)
                taken_culture = "-".join(culture.split("-")[:-1])
                taken_culture_group = culture.split("-")[-1]
                taken_religion = None
                taken_religion_group = None
                while(taken_religion == None):
                    religion = random.choice(self.religions)
                    taken_religion = religion.split("-")[1]
                    taken_religion_group = religion.split("-")[0]
                    if(taken_religion == "anglican" and taken_culture_group != "british"):
                        taken_religion = None
                        taken_religion_group = None

                taken_technology = random.choice(self.technologies)
                taken_government = None
                taken_government_group = None
                while(taken_government == None):
                    taken_government = random.choice(list(self.governments.keys()))
                    if("not" in self.governments[taken_government]):
                        if("culture" in self.governments[taken_government]["not"]):
                            if(taken_culture_group in self.governments[taken_government]["not"]["culture"] or
                               taken_culture in self.governments[taken_government]["not"]["culture"]):
                                taken_government = None
                                continue

                        if("religion" in self.governments[taken_government]["not"]):
                            if(taken_religion_group in self.governments[taken_government]["not"]["religion"] or
                               taken_religion in self.governments[taken_government]["not"]["religion"]):
                                taken_government = None
                                continue

                        if("technology" in self.governments[taken_government]["not"]):
                            if(taken_technology in self.governments[taken_government]["not"]["technology"]):
                                taken_government = None
                                continue

                    if("culture" in self.governments[taken_government]):
                        if(not (taken_culture_group in self.governments[taken_government]["culture"] and
                                taken_culture in self.governments[taken_government]["culture"])):
                            taken_government = None
                            continue

                    if("religion" in self.governments[taken_government]):
                        if(not(taken_religion_group in self.governments[taken_government]["religion"] and
                               taken_religion in self.governments[taken_government]["religion"])):
                            taken_government = None
                            continue

                    if("technology" in self.governments[taken_government]):
                        if(not taken_technology in self.governments[taken_government]["technology"]):
                            taken_government = None
                            continue

                # set government group
                # and remove incorrect ideas for given government
                ideas_pool_government = None
                all_ideas = self.adm_ideas+self.dip_ideas+self.mil_ideas
                if(taken_government in self.monarchies[0]):
                    taken_government_group = "monarchy"
                    not_allowed_ideas = ["horde_unity", "devotion", "republican_tradition", "meritocracy", "monthly_militarized_society", "amount_of_banners"]
                    if(taken_government == "prussian_monarchy"):
                        not_allowed_ideas = ["horde_unity", "devotion", "republican_tradition", "meritocracy", "amount_of_banners"]
                    elif(taken_government == "celestial_empire"):
                        not_allowed_ideas = ["legitimacy", "horde_unity", "devotion", "republican_tradition", "monthly_militarized_society", "loyalty", "amount_of_banners"]

                    ideas_pool_government = [idea for idea in all_ideas if not any(not_allowed in idea for not_allowed in not_allowed_ideas)]
                elif(taken_government in self.republics[0]):
                    taken_government_group = "republic"
                    not_allowed_ideas = ["legitimacy", "horde_unity", "devotion", "meritocracy", "heir_chance", "monthly_militarized_society", "monarch_admin_power", "monarch_diplomatic_power", "monarch_military_power", "amount_of_banners"]
                    if(taken_government == "prussian_republic_reform"):
                        not_allowed_ideas = ["legitimacy", "horde_unity", "devotion", "meritocracy", "heir_chance", "monarch_admin_power", "monarch_diplomatic_power", "monarch_military_power", "amount_of_banners"]
                    elif(taken_government == "pirate_republic_reform" or taken_government == "plutocratic_reform" or taken_government == "veche_republic" or taken_government == "venice_merchants_reform" or taken_government == "cossacks_reform"):
                        not_allowed_ideas = ["legitimacy", "horde_unity", "devotion", "meritocracy", "heir_chance", "monthly_militarized_society", "monarch_admin_power", "monarch_diplomatic_power", "monarch_military_power", "loyalty", "amount_of_banners"]

                    ideas_pool_government = [idea for idea in all_ideas if not any(not_allowed in idea for not_allowed in not_allowed_ideas)]
                elif(taken_government in self.theocracies[0]):
                    taken_government_group = "theocracy"
                    not_allowed_ideas = ["legitimacy", "horde_unity", "republican_tradition", "meritocracy", "heir_chance", "monthly_militarized_society", "monarch_admin_power", "monarch_diplomatic_power", "monarch_military_power", "amount_of_banners"]
                    ideas_pool_government = [idea for idea in all_ideas if not any(not_allowed in idea for not_allowed in not_allowed_ideas)]
                elif(taken_government in self.tribes[0]):
                    taken_government_group = "tribal"
                    not_allowed_ideas = ["horde_unity", "devotion", "republican_tradition", "meritocracy", "monthly_militarized_society", "amount_of_banners"]
                    if(taken_government == "steppe_horde"):
                        not_allowed_ideas = ["legitimacy", "devotion", "republican_tradition", "meritocracy", "monthly_militarized_society", "amount_of_banners"]
                    elif(taken_government == "siberian_tribe"):
                        not_allowed_ideas = ["horde_unity", "devotion", "republican_tradition", "meritocracy", "monthly_militarized_society", "loyalty", "amount_of_banners"]

                    ideas_pool_government = [idea for idea in all_ideas if not any(not_allowed in idea for not_allowed in not_allowed_ideas)]
                elif(taken_government in self.natives[0]):
                    taken_government_group = "native"
                    not_allowed_ideas = ["horde_unity", "devotion", "republican_tradition", "meritocracy", "monthly_militarized_society", "loyalty", "amount_of_banners"]
                    ideas_pool_government = [idea for idea in all_ideas if not any(not_allowed in idea for not_allowed in not_allowed_ideas)]
                else:
                    taken_government_group = "other"
                    if(taken_government == "united_cantons_reform"):
                        not_allowed_ideas = ["legitimacy", "horde_unity", "meritocracy", "heir_chance", "monthly_militarized_society", "monarch_admin_power", "monarch_diplomatic_power", "monarch_military_power", "amount_of_banners"]
                    elif(taken_government == "holy_state_reform"):
                        not_allowed_ideas = ["legitimacy", "horde_unity", "republican_tradition", "meritocracy", "heir_chance", "monthly_militarized_society", "monarch_admin_power", "monarch_diplomatic_power", "monarch_military_power", "amount_of_banners"]

                    ideas_pool_government = [idea for idea in all_ideas if not any(not_allowed in idea for not_allowed in not_allowed_ideas)]

                # remove incorrect ideas for given religion
                ideas_pool_religion = None
                if(taken_religion == "catholic"):
                    not_allowed_ideas = ["yearly_harmony", "harmonization_speed", "church_power_modifier", "monthly_fervor_increase", "monthly_piety", "yearly_patriarch_authority"]
                    ideas_pool_religion = [idea for idea in ideas_pool_government if not any(not_allowed in idea for not_allowed in not_allowed_ideas)]
                elif(taken_religion == "protestant" or taken_religion == "anglican" or taken_religion == "hussite"):
                    not_allowed_ideas = ["papal_influence", "yearly_harmony", "harmonization_speed", "monthly_fervor_increase", "monthly_piety", "yearly_patriarch_authority"]
                    ideas_pool_religion = [idea for idea in ideas_pool_government if not any(not_allowed in idea for not_allowed in not_allowed_ideas)]
                elif(taken_religion == "reformed"):
                    not_allowed_ideas = ["papal_influence", "yearly_harmony", "harmonization_speed", "church_power_modifier", "monthly_piety", "yearly_patriarch_authority"]
                    ideas_pool_religion = [idea for idea in ideas_pool_government if not any(not_allowed in idea for not_allowed in not_allowed_ideas)]
                elif(taken_religion == "orthodox"):
                    not_allowed_ideas = ["papal_influence", "yearly_harmony", "harmonization_speed", "church_power_modifier", "monthly_fervor_increase", "monthly_piety"]
                    ideas_pool_religion = [idea for idea in ideas_pool_government if not any(not_allowed in idea for not_allowed in not_allowed_ideas)]
                elif(taken_religion == "confucianism"):
                    not_allowed_ideas = ["papal_influence", "church_power_modifier", "monthly_fervor_increase", "monthly_piety", "yearly_patriarch_authority"]
                    ideas_pool_religion = [idea for idea in ideas_pool_government if not any(not_allowed in idea for not_allowed in not_allowed_ideas)]
                elif(taken_religion_group == "muslim"):
                    not_allowed_ideas = ["papal_influence", "yearly_harmony", "harmonization_speed", "church_power_modifier", "monthly_fervor_increase", "yearly_patriarch_authority"]
                    ideas_pool_religion = [idea for idea in ideas_pool_government if not any(not_allowed in idea for not_allowed in not_allowed_ideas)]
                else:
                    not_allowed_ideas = ["papal_influence", "yearly_harmony", "harmonization_speed", "church_power_modifier", "monthly_fervor_increase", "monthly_piety", "yearly_patriarch_authority"]
                    ideas_pool_religion = [idea for idea in ideas_pool_government if not any(not_allowed in idea for not_allowed in not_allowed_ideas)]

                # remove incorrect ideas for given culture
                ideas_pool = None
                if(taken_culture != "manchu" or taken_culture != "manchu_new"):
                    ideas_pool = [idea for idea in ideas_pool_religion if not "amount_of_banners" in idea]
                else:
                    ideas_pool = ideas_pool_religion

                for position in range(len(chosen_ideas)):
                    taken_idea = random.choice(ideas_pool)
                    idea_name = "-".join(taken_idea.split("-")[:-1])
                    level = int(taken_idea.split("-")[-1])
                    chosen_ideas[position] = [idea_name, level]
                    ideas_pool_temp = [idea for idea in ideas_pool if not idea_name in idea]
                    ideas_pool = ideas_pool_temp

                adm_max_level = 0
                dip_max_level = 0
                mil_max_level = 0
                current_cost = 0
                if(taken_technology == "high_american"):
                    current_cost += 75

                current_cost += self.governments[taken_government]["costs"]
                for position in range(len(chosen_ideas)):
                    idea_name = chosen_ideas[position][0]
                    level = chosen_ideas[position][1]
                    if(idea_name + "-" + str(level) in self.adm_ideas):
                        chosen_ideas[position].append("ADM")
                    elif(idea_name + "-" + str(level) in self.dip_ideas):
                        chosen_ideas[position].append("DIP")
                    elif(idea_name + "-" + str(level) in self.mil_ideas):
                        chosen_ideas[position].append("MIL")

                    current_cost += self.idea_costs[idea_name][level] * position_modifier[position]
                    if(idea_name + "-" + str(level) in self.adm_ideas):
                        adm_max_level += (10 * level) / max(self.idea_costs[idea_name].keys())
                    elif(idea_name + "-" + str(level) in self.dip_ideas):
                        dip_max_level += (10 * level) / max(self.idea_costs[idea_name].keys())
                    elif(idea_name + "-" + str(level) in self.mil_ideas):
                        mil_max_level += (10 * level) / max(self.idea_costs[idea_name].keys())

                overloaded = adm_max_level / (adm_max_level + dip_max_level + mil_max_level) > 0.5 or dip_max_level / (adm_max_level + dip_max_level + mil_max_level) > 0.5 or mil_max_level / (adm_max_level + dip_max_level + mil_max_level) > 0.5
                over_under_cost = current_cost < min_cost or current_cost > max_cost
                counter += 1
                self.cost.set("{:.1f}".format(current_cost))
                self.iter.set(counter)
                self.culture.set(self.translations[taken_culture])
                self.culture_group.set(self.translations[taken_culture_group])
                self.religion.set(self.translations[taken_religion])
                try:
                    self.religion_group.set(self.translations[taken_religion_group])
                except:
                    self.religion_group.set(taken_religion_group.capitalize())

                self.government.set(self.translations[taken_government])
                try:
                    self.government_group.set(self.translations[taken_government_group])
                except:
                    self.government_group.set(taken_government_group.capitalize())

                self.technology.set(self.translations[taken_technology])
                root.update()
                if(overloaded or over_under_cost or counter < min_iter):
                    chosen_ideas = [None] * 10
                else:
                    section = None
                    for position in range(len(chosen_ideas)):
                        if(position == 0):
                            section = "traditions"
                            self.tree.insert("", "end", section, text=self.translations["gui_traditions"]+":", values=("", ""))
                        elif(position == 2):
                            section = "ideas"
                            self.tree.insert("", "end", section, text=self.translations["gui_ideas"]+":", values=("", ""))
                        elif(position == 9):
                            section = "amibitions"
                            self.tree.insert("", "end", section, text=self.translations["gui_ambitions"]+":", values=("", ""))

                        icon = None
                        try:
                            icon = tk.PhotoImage(file="../../ideas/icons/"+chosen_ideas[position][0]+".gif")
                        except:
                            icon = tk.PhotoImage(file="ideas/icons/"+chosen_ideas[position][0]+".gif")

                        icon = icon.subsample(3, 3)
                        self.idea_icons[position] = icon
                        idea_name = chosen_ideas[position][0]
                        try:
                            self.tree.insert(section, "end", text=" "+self.translations["modifier_"+idea_name], image=self.idea_icons[position], values=chosen_ideas[position][1:])
                        except:
                            try:
                                self.tree.insert(section, "end", text=" "+self.translations["yearly_"+idea_name], image=self.idea_icons[position], values=chosen_ideas[position][1:])
                            except:
                                if("_loyalty_modifier" in idea_name):
                                    estate = self.translations[idea_name].split("[Country.Get")[1].split("Name]")[0]
                                    self.tree.insert(section, "end", text=" "+estate+self.translations[idea_name].split("]")[1], image=self.idea_icons[position], values=chosen_ideas[position][1:])
                                else:
                                    self.tree.insert(section, "end", text=" "+self.translations[idea_name], image=self.idea_icons[position], values=chosen_ideas[position][1:])

                    for i in self.tree.get_children():
                        self.tree.item(i, open=True)

                    break

                if(counter == max_iter):
                    self.cost.set(0.0)
                    break

            self.start_button.config(state=tk.NORMAL)
            for button in self.language_frame.winfo_children():
                button.configure(state=tk.NORMAL)


    try:
        root = tk.Tk()
        try:
            root.iconbitmap("../../icons/ideas.ico")
        except:
            root.iconbitmap("icons/ideas.ico")

        root.style = ttk.Style()
        root.style.theme_use("clam")
        Application(root)
        root.mainloop()
    except Exception as ex:
        messagebox.showerror("Critical error", "A critical error occurred while executing the program. See the message below for more details:\n\n"
                             + traceback.format_exc())
