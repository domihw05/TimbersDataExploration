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

def get_data(season_name='2025', use_cache=True):
    cache_path = f"Cache Data/mls_gplus_{season_name}.parquet"
    if use_cache and os.path.exists(cache_path):
        grouped_data = pd.read_parquet(cache_path)
        return grouped_data

    asa = AmericanSoccerAnalysis()

    # Import 2025 G+ Data
    gplus_data = asa.get_player_goals_added(
        leagues=["mls"],
        season_name = season_name,
        split_by_games = True
    )

    # Import Player Names
    player_data = asa.get_players(leagues=["mls"])

    # Merge them together
    main_df = pd.merge(gplus_data, player_data, on='player_id', how='left')

    def wrangle_data(main_df):
        # Step 1: Expand the 'data' column into rows
        expanded_data = main_df.explode('data')

        # Step 2: Normalize the 'data' column (convert list of dictionaries into columns)
        expanded_data = pd.concat(
            [expanded_data.drop(columns=['data']), expanded_data['data'].apply(pd.Series)],
            axis=1
        )

        return expanded_data

    expanded_data = wrangle_data(main_df)

    # Step 3: Group by player_id and calculate averages for relevant statistics
    grouped_data = expanded_data.groupby(['player_id','action_type']).agg({
        'goals_added_raw': 'sum',
        'goals_added_above_avg': 'sum',
        'count_actions': 'sum',
        'minutes_played':'sum'
    }).reset_index()

    grouped_data['goals_added_raw_per90'] = grouped_data['goals_added_raw'] / (grouped_data['minutes_played'] / 90)
    grouped_data['goals_added_above_avg_per90'] = grouped_data['goals_added_above_avg'] / (grouped_data['minutes_played'] / 90)

    # Step 4: (Optional) Add player names for better readability
    grouped_data = pd.merge(grouped_data, main_df[['player_id', 'player_name','general_position','team_id']].drop_duplicates(), on='player_id', how='left')

    grouped_data.to_parquet(cache_path)
    return grouped_data

def calculate_percentiles(grouped_data, player_name='Felipe Carballo', position='CM'):
    import scipy.stats as stats

    player_df = grouped_data[(grouped_data['player_name'] == player_name) & (grouped_data['general_position'] == position)]

    value = player_df[['action_type','goals_added_raw_per90']]

    position_data = grouped_data[(grouped_data['general_position'] == position) & (grouped_data['minutes_played'] > 800)]
    all_values = position_data[['action_type','goals_added_raw_per90']]
    params = ['Dribbling','Fouling','Interrupting','Passing','Receiving','Shooting']

    percentile = []

    for param in params:
        param_all = all_values[all_values['action_type'] == param]['goals_added_raw_per90']
        param_player = value[value['action_type'] == param]['goals_added_raw_per90']

        percentile.append(stats.percentileofscore(param_all,param_player)[0])

    return percentile

def draw_radar_chart(percentile,player_name,position_name,team_name,season,compare = False,second_percentile = None, second_season = None):
    from mplsoccer import Radar, FontManager, grid
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    URL1 = ('https://raw.githubusercontent.com/googlefonts/SourceSerifProGFVersion/main/fonts/'
            'SourceSerifPro-Regular.ttf')
    serif_regular = FontManager(URL1)
    URL2 = ('https://raw.githubusercontent.com/googlefonts/SourceSerifProGFVersion/main/fonts/'
            'SourceSerifPro-ExtraLight.ttf')
    serif_extra_light = FontManager(URL2)
    URL3 = ('https://raw.githubusercontent.com/google/fonts/main/ofl/rubikmonoone/'
            'RubikMonoOne-Regular.ttf')
    rubik_regular = FontManager(URL3)
    URL4 = 'https://raw.githubusercontent.com/googlefonts/roboto/main/src/hinted/Roboto-Thin.ttf'
    robotto_thin = FontManager(URL4)
    URL5 = ('https://raw.githubusercontent.com/google/fonts/main/apache/robotoslab/'
            'RobotoSlab%5Bwght%5D.ttf')
    robotto_bold = FontManager(URL5)

    # Example stat names
    params = ['Dribbling','Fouling','Interrupting','Passing','Receiving','Shooting']


    # Define min-max ranges (all percentiles here)
    low = [0] * len(params)
    high = [100] * len(params)

    round_int = [True] * len(params)
    lower_is_better = None

    # Radar setup exactly like docs
    radar = Radar(params, low, high,
                lower_is_better=lower_is_better,
                # whether to round any of the labels to integers instead of decimal places
                round_int=round_int,
                num_rings=4,  # the number of concentric circles (excluding center circle)
                # if the ring_width is more than the center_circle_radius then
                # the center circle radius will be wider than the width of the concentric circles
                ring_width=1, center_circle_radius=1)

    # creating the figure using the grid function from mplsoccer:
    fig, ax = grid(figheight=14, grid_height=0.915, title_height=0.06, endnote_height=0.025,
                    title_space=0, endnote_space=0, grid_key='radar', axis=False)

    # plot the radar
    radar.setup_axis(ax=ax['radar'])

    rings_inner = radar.draw_circles(ax=ax['radar'], facecolor="#FFBE27", edgecolor='#FFBE27')
    legend_handles = [Patch(color="#175922", label=season)]

    if compare and second_percentile is not None:
        second_radar_output = radar.draw_radar(second_percentile, ax=ax['radar'],
                                               kwargs_radar={'facecolor': "#8A0F17", 'alpha': 0.8},
                                               kwargs_rings={'facecolor': "#65100B", 'alpha': 0.8})
        legend_handles.append(Patch(color="#8A0F17", label=second_season))

    radar_output = radar.draw_radar(percentile, ax=ax['radar'],
                                    kwargs_radar={'facecolor': "#175922",'alpha': 0.7 if compare else 1},
                                    kwargs_rings={'facecolor': "#143A18",'alpha': 0.7 if compare else 1})
    

    

    radar_poly, rings_outer, vertices = radar_output
    range_labels = radar.draw_range_labels(ax=ax['radar'], fontsize=25,
                                        fontproperties=serif_regular.prop)
    param_labels = radar.draw_param_labels(ax=ax['radar'], fontsize=25,
                                        fontproperties=serif_regular.prop)
    
    # Add legend
    ax['radar'].legend(handles=legend_handles, loc='upper right', fontsize=18, 
                       frameon=True,bbox_to_anchor=(1, 0.99))  # (x, y) where y < 1 moves it down


    # adding the endnote and title text (these axes range from 0-1, i.e. 0, 0 is the bottom left)
    # Note we are slightly offsetting the text from the edges by 0.01 (1%, e.g. 0.99)
    endnote_text = ax['endnote'].text(0.99, 0.5, 'Made by TotalTimbers - Statistics via American Soccer Analysis - Percentiles Based on G+ of Positional Peers with >800 Minutes this Season', fontsize=15,
                                    fontproperties=robotto_thin.prop, ha='right', va='center')
    title1_text = ax['title'].text(0.01, 0.6, player_name, fontsize=40,
                                    fontproperties=robotto_bold.prop, ha='left', va='center')
    title2_text = ax['title'].text(0.01, 0.05, team_name, fontsize=25,
                                    fontproperties=robotto_thin.prop,
                                    ha='left', va='center', color="#104618")
    title3_text = ax['title'].text(0.99, 0.6, 'Radar Chart', fontsize=40,
                                    fontproperties=robotto_bold.prop, ha='right', va='center')
    title4_text = ax['title'].text(0.99, 0.05, position_name, fontsize=25,
                                    fontproperties=robotto_thin.prop,
                                    ha='right', va='center', color='#104618')
    
    new_name_arr = player_name.split(' ')
    if len(new_name_arr) > 1:
        new_name = new_name_arr[0] + new_name_arr[1]
    else:
        new_name = new_name_arr[0]
    if compare:
        outpath = f"Output/{new_name}_{season}_vs_{second_season}_spiderchart.png"
    else:
        outpath = f"Output/{new_name}_{season}_spiderchart.png"

    plt.savefig(outpath, dpi=300, bbox_inches='tight')



if __name__ == "__main__":
    # Get the data
    (season, player_name, position, 
     position_name, team_name) = ('2024',
                                  'Santiago Moreno',
                                  'W', 
                                  'Winger', 
                                  'Portland Timbers')
    (season2, player_name2, position2, 
     position_name2, team_name2) = ('2023',
                                  'Santiago Moreno',
                                  'W', 
                                  'Winger', 
                                  'Portland Timbers')

    grouped_data = get_data(season)
    grouped_data2 = get_data(season2)

    # Calculate percentiles for a specific player
    percentile = calculate_percentiles(grouped_data, player_name=player_name, position=position)
    second_percentile = calculate_percentiles(grouped_data2, player_name=player_name2, position=position2)

    # Draw the radar chart
    draw_radar_chart(percentile, player_name=player_name, 
                     position_name=position_name, team_name=team_name, 
                     season = season, compare=True,
                     second_percentile=second_percentile,
                     second_season=season2)