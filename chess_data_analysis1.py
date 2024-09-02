import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns


dataframe_full = pd.read_csv("my_processed_data.csv",
                          delimiter=',')
all_headers = np.genfromtxt("my_processed_data.csv",
                          delimiter=','
                         , deletechars= ",':;-&*+=/\"",
                           autostrip=True,
                           invalid_raise=False,
                           dtype = str,
                           skip_footer=dataframe_full.shape[0])



dataframe_full= dataframe_full.set_axis(all_headers, axis=1)

#changing the wording of the ending conditions
new_victory_status_column = []
for i in dataframe_full["victory_status"]:
    if i == "mate":
        new_victory_status_column.append("Checkmate")
    elif i == "draw":
        new_victory_status_column.append("Draw")
    elif i == "resign":
        new_victory_status_column.append("Resignation")
    elif i == "outoftime":
        new_victory_status_column.append("Out of Time")

dataframe_full["victory_status"] = (new_victory_status_column)


#finding how many times each opening is used

unique_openings= (dataframe_full["opening_name"]).unique()



openings_count = dataframe_full["opening_name"].value_counts()[:20].tolist()
openings_in_order= dataframe_full["opening_name"].value_counts()[:20].index.tolist()

opening_colours = {"Sicilian Defense": "black", "French Defense": "black", "Queen's Pawn": "white", "Italian Game":"white", "King's Pawn":"white","Queen's Gambit": "white", "Ruy Lopez":"white", "English Opening":"white", "Scandinavian Defense":"black","Philidor Defense": "black","Caro-Kann Defense":"black", "Scotch Game":"white", "Four Knights Game":"white", "Van't Kruijs Opening":"white", "Slav Defense":"black","Zukertort Opening":"white","Indian Game":"black", "King's Indian":"black","Pirc Defense":"black","Russian Game":"black"}
bar_colours = []
for i in opening_colours:
    bar_colours.append(opening_colours[i])




# finding the win rates for each of these openings

draws=[]
wins=[]
losses=[]
percentages =[]
for i in range(len(openings_in_order)):
    wins_total = 0
    losses_total = 0
    draws_total = 0
    for j in range(len(dataframe_full["opening_name"])):
        if openings_in_order[i]== dataframe_full["opening_name"][j]:
            if dataframe_full["winner"][j] == opening_colours[openings_in_order[i]]:
                wins_total = wins_total+1
            elif dataframe_full["winner"][j] == "draw":
                draws_total=draws_total+1
            else:
                losses_total = losses_total+1
    win_percentages = (round((wins_total/(wins_total+losses_total)),2)*100)
    wins.append(wins_total)
    losses.append(losses_total)
    percentages.append(win_percentages)


wins_and_losses = pd.DataFrame({
    "Opening":openings_in_order,
    "Frequency":openings_count,
    "Wins":wins,
    "Losses":losses,
    "Win Percentage":percentages
    })

#plotting the data using a graph to combine the frequency of an opening and its win rate

fig, ax = plt.subplots(figsize = (10,7))
fig.subplots_adjust(bottom = 0.25, top = 0.9)
plt.xticks(rotation =90)
ax.bar(wins_and_losses["Opening"],
          wins_and_losses["Frequency"],
          color = bar_colours,
          edgecolor = "black")

ax.set_ylabel("Frequency of Opening",
              weight = "bold")
ax.yaxis.set_ticks(np.arange(0,np.max(openings_count),200))
ax1 = ax.twinx()
ax1.plot(wins_and_losses["Opening"],
         wins_and_losses["Win Percentage"],
         color = "red",
         marker = "D")
ax1.set_ylim(0,100)
ax1.set_ylabel("Win Percentage",
               weight = "bold")
ax.set_title("Popularity and Win Rates of top 20 Openings", fontsize = 14, weight = "bold")
plt.legend(handles = ((mpatches.Patch(color='black', label='Black Openings'),mpatches.Patch(color='White', label='White Openings',edgecolor="black", linewidth = 3))), facecolor = "gainsboro")
ax.yaxis.grid(visible = True, linestyle = '-', linewidth = 0.5, color = "teal")


print("The most popular opening is the",openings_in_order[0],". It has been played ",openings_count[0],"times.")
print("The opening with the highest success rate is the", openings_in_order[0], ".It has a success rate of ", round(np.max(wins_and_losses["Win Percentage"])),"%.")
print("The opening with the lowest success rate is the", openings_in_order[19], ".It has a success rate of ", round(np.min(wins_and_losses["Win Percentage"])),"%.")


#How do most games end for each time control?
#firstly, cutting down all increments to only include the number of minutes (e.g. 10+5 becomes just 10), and then categorising them as one of the 4 game types available - bullet, blitz, rapid and classical
all_time_controls = dataframe_full["increment_code"].tolist()
time_controls = list(set(all_time_controls))

for i in range((len(time_controls))):
    time_controls[i] = int((time_controls[i])[:time_controls[i].index("+")])
time_controls=  sorted((list(set(time_controls))))

Bullet = []
Blitz = []
Rapid = []
Classical = []
game_types_dict = {"Bullet":Bullet,"Blitz":Blitz,"Rapid":Rapid,"Classical":Classical}
victory_states = ["Draw","Resignation","Out of Time","Checkmate"]


for i in time_controls:
    if i <= 2 :
        Bullet.append(i)
    elif 3<= i and i <= 10 :
        Blitz.append(i)
    elif 11 <= i and i <= 30:
        Rapid.append(i)
    else:
        Classical.append(i)


#creatingf a dataframe to count how many times each game type ends in a certain way, e.g. how many times does a bullet game end in a draw?
# Then converting these figures to percentages, i.e. what percentage of bullet games end in draws?
game_endings_df = pd.DataFrame(0, index = victory_states,columns = ("Bullet","Blitz","Rapid","Classical"))

for i in range(len(all_time_controls)):
    for j in game_types_dict:
        if int((all_time_controls[i])[:all_time_controls[i].index("+")]) in game_types_dict[j]:
            for k in victory_states:
                if dataframe_full["victory_status"][i] == k:
                    game_endings_df[j][k] = game_endings_df[j][k] + 1

game_endings_percentages = game_endings_df.copy()

for j in victory_states:
        for i in game_types_dict:
            game_endings_percentages[i][j] = round((int(game_endings_df[i][j]))/sum(game_endings_df[i]) *100)


#plotting the graph 

game_endings_percentages = game_endings_percentages.T


bullet_data = game_endings_percentages["Draw"]
blitz_data = game_endings_percentages["Resignation"]
rapid_data = game_endings_percentages["Out of Time"]
classical_data = game_endings_percentages["Checkmate"]



barwidth = 0.25
r = np.arange(4)
r2 = r + 0.2
r3 = r2 + 0.2
r4 = r3 + 0.2

fig, ax = plt.subplots(figsize = (10,7))
fig.subplots_adjust(bottom = 0.25, top = 0.9)
ax.bar(r, bullet_data, color='darkorange', width=barwidth, edgecolor='white', label='Draw')
ax.bar(r2, blitz_data, color='orangered', width=barwidth, edgecolor='white', label='Resignation')
ax.bar(r3, rapid_data, color='limegreen', width=barwidth, edgecolor='white', label='Out of Time')
ax.bar(r4, classical_data, color='navy', width=barwidth, edgecolor='white', label='Checkmate')

ax.set_xlabel('Time Control', fontweight='bold')
ax.set_xticks(r + barwidth)
ax.set_xticklabels(['Bullet', 'Blitz', 'Rapid', 'Classical'])
ax.set_ylabel("Percentage of Games", fontweight = "bold")
ax.set_title("How do Games End for each Time Control", fontweight = "bold")


ax.legend()
plt.show()


#Providing some additional information about the openings

print("The most popular opening is the",openings_in_order[0],". It has been played ",openings_count[0],"times.")
print("The opening with the highest success rate is the", openings_in_order[0], ".It has a success rate of ", round(np.max(wins_and_losses["Win Percentage"])),"%.")
print("The opening with the lowest success rate is the", openings_in_order[19], ".It has a success rate of ", round(np.min(wins_and_losses["Win Percentage"])),"%.")