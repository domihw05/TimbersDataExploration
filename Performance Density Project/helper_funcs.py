import random
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.cm import ScalarMappable, get_cmap
from itscalledsoccer.client import AmericanSoccerAnalysis
import pandas as pd
import os
import numpy as np
import matplotlib.font_manager as font_manager
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker


def import_asa_timbers_data():
    asa = AmericanSoccerAnalysis()

    # Step 1: Get Teams and Games
    teams = asa.get_teams()
    games = asa.get_games(seasons=['2025'])
    games['date_only'] = pd.to_datetime(games['date_time_utc']).dt.date
    games['game_id'] = games['game_id'].astype(str)
    games = games[['game_id', 'date_only']]
    
    # Step 2: Find Portland Timbers FC
    timbers_rows = teams[teams["team_name"] == "Portland Timbers FC"]
    timbers_id = timbers_rows["team_id"].values[0]  # <<< just grab the string

    # Step 3: Get player g+ just for Timbers
    gplus_data = asa.get_player_goals_added(
        leagues=["mls"],
        team_ids=[timbers_id],  # Now passing a real string inside a list
        split_by_games=True
    )

    player_data = asa.get_players(leagues=["mls"])


    gplus_data['game_id'] = gplus_data['game_id'].astype(str)

    # Step 4: Merge player names and info with gplus_data
    main_df_sub = pd.merge(gplus_data, games, on='game_id', how='left')
    main_df = pd.merge(main_df_sub, player_data, on='player_id', how='left')


    return main_df

def wrangle_data_by_player(main_df):
    # Step 1: Expand the 'data' column into rows
    expanded_data = main_df.explode('data')

    # Step 2: Normalize the 'data' column (convert list of dictionaries into columns)
    expanded_data = pd.concat(
        [expanded_data.drop(columns=['data']), expanded_data['data'].apply(pd.Series)],
        axis=1
    )

    # Step 3: Group by player_id and calculate averages for relevant statistics
    grouped_data = expanded_data.groupby('player_id').agg({
        'goals_added_raw': 'mean',
        'goals_added_above_avg': 'mean',
        'count_actions': 'mean'
    }).reset_index()

    # Step 4: (Optional) Add player names for better readability
    grouped_data = pd.merge(grouped_data, main_df[['player_id', 'player_name']].drop_duplicates(), on='player_id', how='left')

    # Step 5: Return the result
    return grouped_data


def wrangle_data(main_df):
    # Step 1: Expand the 'data' column into rows
    expanded_data = main_df.explode('data')

    # Step 2: Normalize the 'data' column (convert list of dictionaries into columns)
    expanded_data = pd.concat(
        [expanded_data.drop(columns=['data']), expanded_data['data'].apply(pd.Series)],
        axis=1
    )

    return expanded_data

def normalize_data(main_df):
    min_ = main_df['goals_added_raw'].min()
    max_ = main_df['goals_added_raw'].max()
    # Standardize
    z = (main_df['goals_added_raw'] - np.mean(main_df['goals_added_raw'])) / np.std(main_df['goals_added_raw'])

    # Squash with sigmoid and stretch to 4–10
    main_df['rating'] = 4 + 6 * (1 / (1 + np.exp(-z)))  # Sigmoid scaled to [4,10]
    main_df['gplus'] = ((main_df['goals_added_raw'] - min_) / (max_ - min_))

    return main_df



def plot_each_player(data, output_dir = "Player Distributions"):
    '''
    Take player data and create a graph distribution of past performances based
    on that, outputting every player's graph to a specified folder.
    
    Args:
        data: dataframe with each row being a player in a specific game
        output_dir: String, specified output directory for graphs
    
    Returns:
        Nothing
    '''
    players = data['player_id'].unique()  

    # Step 1: Normalize the 'goals_added_raw' values for consistent coloring
    all_values = data['goals_added_raw']
    norm = Normalize(vmin=all_values.min(),vmax = all_values.max()) # Normalize across all players

    # Create a custom colormap (red -> yellow -> green)
    colors = [(1, 0, 0), (1, 1, 0), (0, 1, 0)]  # Red -> Yellow -> Green
    custom_cmap = LinearSegmentedColormap.from_list("custom_cmap", colors)

    for player_id in players:
        # Filter data for the current player
        player_data = data[data['player_id'] == player_id]
        
        # Skip if there are not enough data points
        if player_data['goals_added_raw'].dropna().shape[0] < 2:
            print(f"Skipping player {player_id} due to insufficient data.")
            continue

        # Create a histogram or KDE plot for 'goals_added_raw'
        plt.figure(figsize=(8, 6))
        kde = sns.kdeplot(player_data['goals_added_raw'], fill=False, color='black', linewidth=1.5)
        
        # Get the KDE values
        line = kde.get_lines()
        if not line:  # Check if KDE plot was generated
            print(f"No KDE plot generated for player {player_id}. Skipping.")
            continue
        x, y = line[0].get_data()

        # Fill the area under the curve with colors
        for i in range(len(x) - 1):
            plt.fill_between(
                x[i:i+2], 0, y[i:i+2],
                color=custom_cmap(norm(x[i])),  # Map the x-value to a color
                alpha=0.8
            )
        
        # Add labels and title
        player_name = player_data['player_name'].iloc[0]  # Get the player's name
        plt.title(f"Career Goals Added Distribution for {player_name}", fontsize=14)
        plt.xlabel("Goals Added (Raw)", fontsize=12)
        plt.ylabel("Density", fontsize=12)
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Show the plot
        plt.savefig(f"{output_dir}/{player_name}_distr")
        plt.close()


def plot_a_game(data, game_date, vs_team, data_bool, output_file = "out", save_fig = False):
    '''
    Take player data and create a plot all player distributions in data (max 11)
    on one chart
    
    Args:
        data: dataframe with each row being a player in a specific game
        game_date: string, the date of the game in question
        vs_team: string, the team played against
        data_bool: bool, if false then g_added_raw, else g_added_above_avg
        output_file: String, specified output file name for graph
        save_fig: Boolean, whether or not to save the graph to file
    
    Returns:
        Nothing
    '''
    data_setting = 'goals_added_raw'
    if data_bool:
        data_setting = 'goals_added_above_avg'
    # Filters for Timbers
    game_date = pd.to_datetime(game_date).date()
    # Step 1: Create a custom colormap (red -> yellow -> green)
    colors = [(1, 0, 0), (1, 1, 0), (0, 1, 0)]  # Red -> Yellow -> Green
    custom_cmap = LinearSegmentedColormap.from_list("custom_cmap", colors)

    # Step 2: Normalize the 'goals_added_raw' values with 0.0 as the midpoint
    all_values = data[data_setting]
    norm = Normalize(vmin=all_values.min() + 0.2, vmax=all_values.max() - 0.2)  # Normalize across all players

    # Step 3: Get a list of unique player IDs and randomly sample 11 players
    chosen_game = data[data['date_only'] == game_date]
    players = chosen_game['player_id'].unique()

    # Step 4: Create a 4x4 grid for subplots
    fig, axes = plt.subplots(4, 4, figsize=(24, 18))  # 6 rows, 2 columns
    axes = axes.flatten()  # Flatten the 2D array of axes for easier indexing

    


    # Load font
    font_path = '../Fonts/Arvo-Bold.ttf'
    font_props = font_manager.FontProperties(fname=font_path)

    # Set background
    fig.patch.set_facecolor('#1a1a1a')  

    # Add overarching title
    fig.suptitle(f"Player Performance Distributions vs {vs_team}",
                 fontproperties = font_props, 
                 fontsize=40, color='white', weight='bold', y=0.96)

    # Step 5: Plot each player's distribution in a subplot
    for i, player_id in enumerate(players):
        axes[i].set_facecolor('#1a1a1a')
        # Filter data for the current player
        player_data = data[data['player_id'] == player_id]
        chosen_game_player = chosen_game[chosen_game['player_id'] == player_id]
        if chosen_game_player.empty:
            print(f"PLAYER DATA MISSING FOR {player_id} on {game_date}. Skipping.")
            continue
        todays_perf = chosen_game_player[data_setting].iloc[0]
        todays_rat = chosen_game_player['rating'].iloc[0]
        
        # Skip if there are not enough data points
        if player_data[data_setting].dropna().shape[0] < 2:
            print(f"Skipping player {player_id} due to insufficient data.")
            continue
        
        # Create a KDE plot for 'goals_added_raw'
        kde = sns.kdeplot(player_data[data_setting], ax=axes[i], fill=False, color='white', linewidth=1.5, bw_adjust = 0.42)
        
        # Get the KDE values
        line = kde.get_lines()
        if not line:  # Check if KDE plot was generated
            print(f"No KDE plot generated for player {player_id}. Skipping.")
            continue
        x, y = line[0].get_data()  # Extract x and y data from the first Line2D object
        
        # Fill the area under the curve with colors
        for j in range(len(x) - 1):
            axes[i].fill_between(
                x[j:j+2], 0, y[j:j+2],
                color=custom_cmap(norm(x[j])),  # Map the x-value to the custom colormap
                alpha=0.8
            )
        
        # Add title to each subplot
        player_name = player_data['player_name'].iloc[0]  # Get the player's name
        axes[i].set_title(player_name + f" (Rating: {round(todays_rat,1)})",
                          color = 'white',fontproperties = font_props, fontsize=20)
        axes[i].set_xlim(-0.3,0.3)
        axes[i].axvline(x=todays_perf,color='red', linestyle='solid', linewidth = 2, label = 'Performance')
        axes[i].axis('off')

    # Step 6: Hide any unused subplots
    for j in range(len(players), len(axes)):
        fig.delaxes(axes[j])

    # Step 7: Adjust layout and show the plot
    plt.tight_layout(rect=[0.025, 0.025, 0.975, 0.95])  # Reserve space for the title

    if save_fig:
        plt.savefig("output_file")
    else:
        plt.show()

    plt.close()
