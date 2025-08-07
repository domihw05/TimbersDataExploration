from spiderchart import get_data, calculate_percentiles, draw_radar_chart
import matplotlib.pyplot as plt
import pandas as pd
from itscalledsoccer.client import AmericanSoccerAnalysis

def find_most_improved_players():
    asa = AmericanSoccerAnalysis()
    print("Fetching data for both seasons...")
    team_data = asa.get_teams(leagues=["mls"])

    data_2024 = get_data("2024")
    data_2025 = get_data("2025")
    data_2024 = pd.merge(data_2024, team_data, on='team_id', how='left')
    data_2025 = pd.merge(data_2025, team_data, on='team_id', how='left')


    timbers_2024 = data_2024[data_2024['team_abbreviation'] == ('POR')]
    timbers_2025 = data_2025[data_2025['team_abbreviation'] == ('POR')]

    # Get all unique Timbers players who appear in both seasons
    players_2024 = set(timbers_2024['player_name'].unique())
    players_2025 = set(timbers_2025['player_name'].unique())
    common_players = list(players_2024 & players_2025)

    print(f"Found {len(common_players)} players with data in both seasons...")

    improvement_scores = []

    for player in common_players:
        try:
            # Position lookup
            pos_2025 = timbers_2025[timbers_2025['player_name'] == player]['general_position'].iloc[0]
            pos_2024 = timbers_2024[timbers_2024['player_name'] == player]['general_position'].iloc[0]

            # Sanity check to ensure we're comparing same position
            if pos_2024 != pos_2025:
                if player == 'David Ayala':
                    pos_2024 = pos_2025 = 'DM'
                elif player == 'Jonathan Rodríguez':
                    pos_2024 = pos_2025 = 'W'
                else:
                    print(f"Skipping {player} due to position mismatch: {pos_2024} vs {pos_2025}")
                    continue

            p25 = calculate_percentiles(data_2025, player_name=player, position=pos_2025)
            p24 = calculate_percentiles(data_2024, player_name=player, position=pos_2024)

            if len(p25) != 6 or len(p24) != 6:
                print(f"Skipping {player} due to missing data in percentiles: {p25} vs {p24}")
                continue  # skip if missing data

            improvement = sum([a - b for a, b in zip(p25, p24)])
            improvement_scores.append({
                "player_name": player,
                "position": pos_2025,
                "2025_percentiles": p25,
                "2024_percentiles": p24,
                "improvement_score": improvement
            })
        except Exception as e:
            print(f"Skipping {player} due to error: {e}")
            continue

    df = pd.DataFrame(improvement_scores)
    df = df.sort_values(by="improvement_score", ascending=False)

    print("\nTop 5 Most Improved Players:")
    print(df[['player_name', 'position', 'improvement_score']].head())

    # Return full df if further processing is needed
    return df

if __name__ == "__main__":
    # Run improvement analysis
    most_improved_df = find_most_improved_players()

    # Optional: Visualize the most improved player
    top_player = most_improved_df.iloc[0]
    print(most_improved_df)