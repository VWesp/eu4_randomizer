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

class Application(tk.Frame):

    def __init__(self, master=None):
        self.adm_ideas = []
        self.dip_ideas = []
        self.mil_ideas = []
        self.idea_costs = {}
        self.translations = {}
        self.loadIdeas("ideas.yaml")
        self.loadTranslations("german")
        tk.Frame.__init__(self, master)
        self.master = master
        self.initWindow()

    def initWindow(self):
        self.master.title("EU4 - Custom Nation - Idea Randomizer")
        ###############################
        self.language_frame = tk.LabelFrame(self.master, text=self.translations["gui_language"])
        languages = {"Sprache: Deutsch": "german", "Language: English": "english", "Idioma: Espanol": "spanish", "Idoma: Francais": "french"}
        self.language_var = tk.StringVar()
        self.language_var.set("german")
        column = 0
        for (key, value) in languages.items():
            tk.Radiobutton(self.language_frame, text=key, variable=self.language_var, value=value, command=lambda:
                           self.changeLanguage(self.language_var.get())).grid(row=0, column=column, pady=5)
            column += 1

        self.language_frame.grid(row=0, column=0, pady=5)
        ###############################
        self.cost_frame = tk.LabelFrame(self.master, text=self.translations["gui_costs"], borderwidth=2, relief="groove")
        vcmd = (self.cost_frame.register(self.validateCostInput), "%P")
        self.min_cost_label = tk.Label(self.cost_frame, text=self.translations["gui_minimum"] + ":")
        self.min_cost = tk.DoubleVar()
        self.min_cost.set(50)
        self.min_cost_entry = tk.Entry(self.cost_frame, textvariable=self.min_cost, validate="key", validatecommand=vcmd)
        self.max_cost_label = tk.Label(self.cost_frame, text=self.translations["gui_maximum"] + ":")
        self.max_cost = tk.DoubleVar()
        self.max_cost.set(800)
        self.max_cost_entry = tk.Entry(self.cost_frame, textvariable=self.max_cost, validate="key", validatecommand=vcmd)
        self.min_cost_label.grid(row=0, column=0, pady=5, padx=1)
        self.max_cost_label.grid(row=0, column=2, pady=5)
        self.min_cost_entry.grid(row=0, column=1, pady=5, padx=(5, 40))
        self.max_cost_entry.grid(row=0, column=3, pady=5)
        self.cost_frame.grid(row=1, column=0, pady=5)
        ###############################
        self.iter_frame = tk.LabelFrame(self.master, text=self.translations["gui_iterations"], borderwidth=2, relief="groove")
        vcmd = (self.cost_frame.register(self.validateIterationInput), "%P")
        self.min_iter_label = tk.Label(self.iter_frame, text=self.translations["gui_minimum"] + ":")
        self.min_iter = tk.DoubleVar()
        self.min_iter.set(1000)
        self.min_iter_entry = tk.Entry(self.iter_frame, textvariable=self.min_iter, validate="key", validatecommand=vcmd)
        self.max_iter = tk.DoubleVar()
        self.max_iter.set(100000)
        self.max_iter_label = tk.Label(self.iter_frame, text=self.translations["gui_maximum"] + ":")
        self.max_iter_entry = tk.Entry(self.iter_frame, textvariable=self.max_iter, validate="key", validatecommand=vcmd)
        self.min_iter_label.grid(row=0, column=0, pady=5)
        self.max_iter_label.grid(row=0, column=2, pady=5)
        self.min_iter_entry.grid(row=0, column=1, pady=5, padx=(5, 40))
        self.max_iter_entry.grid(row=0, column=3, pady=5)
        self.iter_frame.grid(row=2, column=0, pady=5)
        ###############################
        self.start_frame = tk.Frame(self.master,  borderwidth=2, relief="groove")
        self.start_button = tk.Button(self.start_frame, text=self.translations["gui_start"], command=lambda:
                                      self.getRandomIdeas(self.min_cost, self.max_cost, self.min_iter, self.max_iter))
        self.start_button.grid(row=0, column=0, padx=(5, 25))
        #############
        self.cost_label = tk.Label(self.start_frame, text=self.translations["gui_costs"] + ":")
        self.cost_label.grid(row=0, column=1, pady=5, padx=1)
        self.cost = tk.DoubleVar()
        self.cost.set(0)
        self.cost_entry = tk.Entry(self.start_frame, textvariable=self.cost)
        self.cost_entry.config(state="readonly")
        self.cost_entry.grid(row=0, column=2, pady=5, padx=(5, 25))
        #############
        self.iter_label = tk.Label(self.start_frame, text=self.translations["gui_iterations"] + ":")
        self.iter_label.grid(row=0, column=3, pady=5, padx=1)
        self.iter = tk.DoubleVar()
        self.iter.set(0)
        self.iter_entry = tk.Entry(self.start_frame, textvariable=self.iter)
        self.iter_entry.config(state="readonly")
        self.iter_entry.grid(row=0, column=4, pady=5, padx=5)
        self.start_frame.grid(row=3, column=0, pady=5)
        ###############################
        self.grid_frame = tk.Frame(self.master)
        self.headers = (self.translations["gui_ideas"], self.translations["gui_level"], self.translations["gui_category"])
        self.tree = ttk.Treeview(columns=self.headers, show="headings")
        ysb = ttk.Scrollbar(orient="vertical", command=self.tree.yview)
        xsb = ttk.Scrollbar(orient="horizontal", command=self.tree.xview)
        self.tree["yscroll"] = ysb.set
        self.tree["xscroll"] = xsb.set
        self.tree.grid(in_=self.grid_frame, row=0, column=0, sticky=tk.NSEW)
        ysb.grid(in_=self.grid_frame, row=0, column=1, sticky=tk.NS)
        xsb.grid(in_=self.grid_frame, row=1, column=0, sticky=tk.EW)
        self.tree.rowconfigure(0, weight=1)
        self.tree.columnconfigure(0, weight=1)
        self.grid_frame.grid(row=4, column=0, pady=5)

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
        for i in self.tree.get_children():
            self.tree.delete(i)

        self.loadTranslations(language)
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

    def loadIdeas(self, config_yaml):
        with open(config_yaml, "r", encoding="utf-8") as ideas_file:
            ideas_data = yaml.safe_load(ideas_file)
            for idea_type in ideas_data:
                with open(ideas_data[idea_type], "r") as idea_file:
                    idea_json = json.load(idea_file)
                    for type in idea_json:
                        for idea in idea_json[type]:
                            if(not idea == "category"):
                                self.idea_costs[idea] = {}
                                self.idea_costs[idea][1] = 0
                                for level in idea_json[type][idea]:
                                    if("level_cost_" in level):
                                        current_level = int(level.split("level_cost_")[1])
                                        self.idea_costs[idea][current_level] = idea_json[type][idea][level]
                                        if("_adm_" in type):
                                            self.adm_ideas.append(idea + "-" + str(current_level))
                                        elif("_dip_" in type):
                                            self.dip_ideas.append(idea + "-" + str(current_level))
                                        elif("_mil_" in type):
                                            self.mil_ideas.append(idea + "-" + str(current_level))

    def loadTranslations(self, language):
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
            self.translations["gui_language"] = "Idioma"
        elif(language == "german"):
            self.translations["gui_traditions"] = "Traditionen"
            self.translations["gui_ideas"] = "Ideen"
            self.translations["gui_ambitions"] = "Ambitionen"
            self.translations["gui_iterations"] = "Iterationen"
            self.translations["gui_costs"] = "Kosten"
            self.translations["gui_minimum"] = "Minimal"
            self.translations["gui_maximum"] = "Maximal"
            self.translations["gui_start"] = "Zufallsgenerator Starten"
            self.translations["gui_level"] = "Stufe"
            self.translations["gui_category"] = "Kategorie"
            self.translations["gui_language"] = "Sprache"
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

        for file in os.listdir("localisations/" + language):
            if(file.endswith(".yml")):
                with open("localisations/" + language + "/" + file, "r", encoding="utf-8") as language_file:
                    for line in language_file.readlines():
                        stripped_line = line.strip()
                        if(stripped_line and not (stripped_line.startswith("\ufeffl_") or stripped_line.startswith("#"))):
                            regex_line = re.split(":[0-9]* \"", stripped_line[:-1])
                            self.translations[regex_line[0].lower()] = regex_line[1]

    def getRandomIdeas(self, min_cost, max_cost, min_iter, max_iter):
        self.cost.set(0.0)
        self.iter.set(0)
        for i in self.tree.get_children():
            self.tree.delete(i)

        try:
            min_cost = float(min_cost.get())
        except:
            min_cost = 50
            self.min_cost.set(50)

        try:
            max_cost = float(max_cost.get())
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
        except:
            min_iter = 1000
            self.min_iter.set(1000)

        try:
            max_iter = int(max_iter.get())
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
        while(True):
            idea_names = []
            for position in range(len(chosen_ideas)):
                while(True):
                    taken_idea = random.choice(self.adm_ideas + self.dip_ideas + self.mil_ideas)
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
                if(counter > max_iter):
                    self.iter.set(counter)
                    return

                idea_name = chosen_ideas[position][0]
                try:
                    chosen_ideas[position][0] = "\t" + self.translations[idea_name]
                except:
                    chosen_ideas[position][0] = "\t" + idea_name

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
            if(overloaded or over_under_cost or counter < min_iter):
                chosen_ideas = [None] * 10
            else:
                self.cost.set("{:.1f}".format(current_cost))
                self.iter.set(counter)
                for position in range(len(chosen_ideas)):
                    if(position == 0):
                        self.tree.insert("", "end", values=(self.translations["gui_traditions"]+":", "", ""))
                        for idx, val in enumerate((self.translations["gui_traditions"]+":", "", "")):
                            iwidth = Font().measure(val)
                            if self.tree.column(self.headers[idx], 'width') < iwidth:
                                self.tree.column(self.headers[idx], width = iwidth)
                    elif(position == 2):
                        self.tree.insert("", "end", values=(self.translations["gui_ideas"]+":", "", ""))
                        for idx, val in enumerate((self.translations["gui_ideas"]+":", "", "")):
                            iwidth = Font().measure(val)
                            if self.tree.column(self.headers[idx], 'width') < iwidth:
                                self.tree.column(self.headers[idx], width = iwidth)
                    elif(position == 9):
                        self.tree.insert("", "end", values=(self.translations["gui_ambitions"]+":", "", ""))
                        for idx, val in enumerate((self.translations["gui_ambitions"]+":", "", "")):
                            iwidth = Font().measure(val)
                            if self.tree.column(self.headers[idx], 'width') < iwidth:
                                self.tree.column(self.headers[idx], width = iwidth)

                    self.tree.insert("", "end", values=chosen_ideas[position])
                    for idx, val in enumerate(chosen_ideas[position]):
                        iwidth = Font().measure(val)
                        if self.tree.column(self.headers[idx], 'width') < iwidth:
                            self.tree.column(self.headers[idx], width = iwidth)

                return

if __name__ == "__main__":
    root = tk.Tk()
    root.style = ttk.Style()
    root.style.theme_use("clam")
    Application(root)
    root.mainloop()
