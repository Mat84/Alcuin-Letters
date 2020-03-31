###William James Mattingly | copyright April 2020###
####################################################
'''
I developed the following functions while researching and writing my dissertation at the University of Kentucky.
The dissertation was defended in April 2020.It is entitled: “DISTANCE LEARNING” IN THE NINTH CENTURY?: MICRO-CLUSTER
ANALYSIS OF THE EPISTOLARY NETWORK OF ALCUIN AFTER 796. These functions allow the researcher to analyze Alcuin's
letters quantitatively with two sets of metadata: manuscripts (located in the collections_data.json, hosted on UKnowledge)
and data extracted from the PASE dataset on Alcuin's letters (http://www.pase.ac.uk/). I do not have the rights to this data,
but I provide the functions for analyzing it bellow and the way in which one should structure the json file that holds that data.
Using PyVis, a powerful Python module to produce VisJS dynamic maps, these functions not only provide quantitative data,
but also render the data visually.
'''

#Dependecies
import json
from pyvis.network import Network
from functools import reduce
import collections


#MSS data storage
letters = []

mss = []

#Metadata storage
letters_2 =[]
names =[]
RecordedNames = []
letter_recipients = []


#MS Node Color and Shape -- for options, see PyVis Docs
ms_color="#da03b3"
ms_shape = "ellipse"

#Letter Node Color and Shape -- for options, see PyVis Docs
ep_color = "#03DAC6"
ep_shape = "box"

#Edge color -- for options, see PyVis Docs
edge_color = "#018786"

#Gets the data from the json file and loads it into memory
def get_mss_data():
    with open ("./json_files/collections_data.json", "r") as json_file:
        data = json.load(json_file)
        for i in data:
            letters.append((list(i.keys())))
            mss.append((list(i.values()))[0].split(", "))


#Gets the PASE Data which has the following structure:
'''
{
    "31": {
        "RecordedNames": [
            "Alchuinus (Alcuin 1)",
            "Aedilberctus (Aethelberht 10)"
        ],
        "Authorship": [
            "Aethelberht 10, anonymi 1876"
        ]
    }
},
'''
#Because I do not have the rights to the PASE data, I do not supply it.
def get_metadata():
    All_Recipients = []
    with open ("./PASE/Pase_Names.json", "r") as json_file:
        data = json.load(json_file)
        x=0
        for i in data:
            letters_2.append((list(i.keys())))
            # names = data[i]["RecordedNames"]
            names = (data[x][str(x+1)]["RecordedNames"])
            recipients = (data[x][str(x+1)]["Authorship"])
            list_names =[]
            list_recipients = []
            for t in names:
                new_name = t.split("(")[1].replace(")", "")
                list_names.append(new_name)
            RecordedNames.append(list_names)

            for t in recipients:
                new_recipients = t.split(", ")
                list_recipients.append(new_recipients)

            All_Recipients.append(list_recipients)
            x=x+1
    for i in range(len(letters_2)):
        for x in range(len(All_Recipients[i])):
            # print (All_Recipients[i])
            if All_Recipients[i][0] == None:
                letter_recipients.append(["none"])
            letter_recipients.append(All_Recipients[i][0])



#Maps the data using PyVis
#name will change the name of the map
#layout will change the layout of the map (I only used the barnes and force_atlas_2based algorithms)
def map_data(name="test", spring=20, layout="atlas"):
    neighbor_map = g.get_adj_list()
    for node in g.nodes:
        # print (node["value"])
        node["title"] += " Neighbors:<br>" + "<br>".join(neighbor_map[node["id"]])
        node["value"] = len(neighbor_map[node["id"]])*10
    if layout=="barnes":
        g.barnes_hut(spring_length=spring)
    if layout=="atlas":
        g.force_atlas_2based()
    g.show_buttons(filter_=["physics"])
    g.show(f"{name}.html")

#Maps all the data with no parameters
def all_data():
    get_mss_data()
    for i in range(len(letters)):
        print (letters[i])
        g.add_node(letters[i][0], title=letters[i][0])
        colors = []
        for x in range(len(mss[i])):
            colors.append("#e5d2d2")
        print (mss[i], colors)
        g.add_nodes(mss[i], title=mss[i], color=colors)
        for x in range(len(mss[i])):
            g.add_edge(letters[i][0], mss[i][x])

#Adds relevent data to the map
#ms is manuscript
#ep is letter
#This script is called by different functions in loops
def add_data(ms, ep):
    g.add_node(ms, title=ms, color=ms_color, shape=ms_shape)
    g.add_node(ep, title=ep, color=ep_color, shape=ep_shape)
    g.add_edge(ms, ep, color=edge_color)


#Finds collections of letters based on certain manuscripts
#get_data is a Boolean and allows you to prevent grabbing data multiple times
#map is a Boolean that either maps the data (True) or does not (False)
def find_collections(manuscripts=[], get_data=True, map=True):
    epp = []
    if get_data==True:
        get_mss_data()
    x = 0
    for ep_mss in mss:
        for ms in ep_mss:
            if ms in manuscripts:
                ep = letters[x][0]
                epp.append(ep)
                if map==True:
                    add_data(ms=ms, ep=ep)
        x=x+1
    mss_num = (len(manuscripts))
    overlap_letters = ([item for item, count in collections.Counter(epp).items() if count > (mss_num-1)])
    non_dupe_epp = list(dict.fromkeys(epp))
    return (len(non_dupe_epp), non_dupe_epp)

#Finds all common letters between manuscripts
#manuscripts is a list of the manuscripts that you want to compare
def get_common_letters(manuscripts=[]):
    get_mss_data()
    letters_found = []
    x=0
    for letter in letters:
        ep = letter[0]
        if set(manuscripts).issubset(mss[x]):
            letters_found.append(ep)
            for ms in manuscripts:
                add_data(ms=ms, ep=ep)
        x=x+1
    letters_found = list(dict.fromkeys(letters_found))
    return (len(letters_found), letters_found)

#Search by letter
#Map will map the data
#strict will only return mss that have overlapping letters and their overlaping and non-overlaping letters
def letter_mss_overlap(epp = [], map=False, strict=False):
    get_mss_data()
    manuscripts_found = []
    if strict==False:
        for ep_1 in epp:
            t=0
            for letter in letters:
                if letter[0] == ep_1:
                    manuscripts_found.append(mss[t])
                    if map == True:
                        find_collections(manuscripts=mss[t], get_data=False)
                t=t+1
    if strict==True:
        letters_found = []
        for ep in epp:
            t=0
            for letter in letters:
                if letter[0] == ep:
                    manuscripts_found.append(mss[t])
                t=t+1
        common_mss = list(reduce(lambda i, j: i & j, (set(x) for x in manuscripts_found)))
        manuscripts_found=[]
        [manuscripts_found.append(x) for x in common_mss]
        if map ==False:
            letters_found = find_collections(manuscripts=manuscripts_found, get_data=False, map=False)
        if map==True:
            letters_found = find_collections(manuscripts=manuscripts_found, get_data=False)
    return (manuscripts_found, letters_found)


#Returns the number of letters that overlap and the specific letters that overlap across singular or multiple manuscripts
def get_list_of_letters():
    found_letters = []
    for node in g.nodes:
        node = node["title"]
        if node.isdigit():
            found_letters.append(node)
    length = len(found_letters)
    return(length, found_letters)


'''
The following functions work with the PASE data. They have not been debugged.
I provide them for users who wish to expirement with them. Please check GitHub for updates on these functions
(https://github.com/wjbmattingly/Alcuin-Letters).
'''

#Returns a list of recipients
def find_recipients(epp=[]):
    get_metadata()
    ep_recipients = []
    for ep in epp:
        ep = int(ep)+1
        letter_and_recipient = {letters_2[ep][0]: letter_recipients[ep]}
        ep_recipients.append(letter_and_recipient.copy())
    return (ep_recipients)


#Eliminates duplicates in a list of names
def get_all_recipients(epp = [], dupe=False):
    epp_recipients = find_recipients(epp=epp)
    all_recipients = []
    if dupe==False:
        for ep in epp_recipients:
            print (ep)
            recipients = ep.values()
            for recipient in recipients:
                print (recipient)
                try:
                    all_recipients.append(recipient)
                except:
                    Exception
        all_recipients = list(dict.fromkeys(all_recipients))


    else:
        all_recipients = epp_recipients
    return (all_recipients)


'''
Below is some sample code for working with these functions.
'''
#This sets up the graph as an object
g = Network(height="1000px", width="75%", bgcolor="#222222", font_color="black")

#This will find collections and all letters connected to the manuscripts: "A1", "A1*", and "A2"
# print (find_collections(manuscripts=["A1", "A1*", "A2"]))

#This will print off the same manuscripts, but strictly the letters they share in common
print (get_common_letters(manuscripts=["A1", "A2", "A1*"]))

#This will map the data that has been gathered
map_data(name="Tour Collection", layout="atlas")
