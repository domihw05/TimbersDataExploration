from spiderchart import get_data, draw_radar_chart
import matplotlib.pyplot as plt
import pandas as pd
from itscalledsoccer.client import AmericanSoccerAnalysis
from scipy import stats

PARAMS = ['Dribbling', 'Fouling', 'Interrupting', 'Passing', 'Receiving', 'Shooting']
POSITION_WEIGHTS = {
    'ST': {
        'Dribbling': 1.0,
        'Fouling': 0.5,
        'Interrupting': 0.5,
        'Passing': 1.0,
        'Receiving': 1.5,
        'Shooting': 2.0,
    },
    'W': {
        'Dribbling': 1.5,
        'Fouling': 0.5,
        'Interrupting': 0.5,
        'Passing': 1.0,
        'Receiving': 1.5,
        'Shooting': 1.5,
    },
    'AM': {
        'Dribbling': 1.25,
        'Fouling': 0.5,
        'Interrupting': 0.5,
        'Passing': 1.5,
        'Receiving': 1.5,
        'Shooting': 1.0,
    },
    'CM': {
        'Dribbling': 0.75,
        'Fouling': 0.5,
        'Interrupting': 1.25,
        'Passing': 1.75,
        'Receiving': 1.0,
        'Shooting': 0.75,
    },
    'DM': {
        'Dribbling': 0.5,
        'Fouling': 0.5,
        'Interrupting': 2.0,
        'Passing': 1.5,
        'Receiving': 0.75,
        'Shooting': 0.25,
    },
    'FB': {
        'Dribbling': 1.0,
        'Fouling': 0.5,
        'Interrupting': 1.5,
        'Passing': 1.25,
        'Receiving': 1.0,
        'Shooting': 0.5,
    },
    'CB': {
        'Dribbling': 0.5,
        'Fouling': 0.5,
        'Interrupting': 2.0,
        'Passing': 1.5,
        'Receiving': 1.0,
        'Shooting': 0.25,
    },
}


def calculate_percentiles_with_fallback(grouped_data, player_name, position):
    player_df = grouped_data[
        (grouped_data['player_name'] == player_name)
        & (grouped_data['general_position'] == position)
    ]

    if player_df.empty:
        return []

    # Early-season data often has no positional peers above 800 minutes,
    # so relax the threshold until a usable comparison pool exists.
    position_data = pd.DataFrame()
    for min_minutes in (800, 400, 180, 90, 0):
        candidate = grouped_data[
            (grouped_data['general_position'] == position)
            & (grouped_data['minutes_played'] > min_minutes)
        ]
        if candidate['player_id'].nunique() >= 10 or min_minutes == 0:
            position_data = candidate
            break

    percentile = []
    for param in PARAMS:
        param_all = position_data[
            position_data['action_type'] == param
        ]['goals_added_raw_per90'].dropna()
        param_player = player_df[
            player_df['action_type'] == param
        ]['goals_added_raw_per90'].dropna()

        if param_all.empty or param_player.empty:
            return []

        percentile.append(float(stats.percentileofscore(param_all, param_player.iloc[0])))

    return percentile


def resolve_comparable_position(player, prev_rows, curr_rows):
    prev_positions = set(prev_rows['general_position'].dropna())
    curr_positions = set(curr_rows['general_position'].dropna())
    shared_positions = prev_positions & curr_positions

    preferred_positions = {
        "Antony": "W",
        "Jimer Fory": "FB",
    }

    preferred = preferred_positions.get(player)
    if preferred and preferred in shared_positions:
        return preferred, preferred

    if shared_positions:
        shared = sorted(shared_positions)[0]
        return shared, shared

    pos_prev = prev_rows['general_position'].iloc[0]
    pos_curr = curr_rows['general_position'].iloc[0]
    return pos_prev, pos_curr


def calculate_weighted_average_percentile_change(p_prev, p_curr, position):
    weights_by_param = POSITION_WEIGHTS.get(position, {param: 1.0 for param in PARAMS})
    deltas = [curr - prev for prev, curr in zip(p_prev, p_curr)]
    weighted_sum = sum(delta * weights_by_param[param] for param, delta in zip(PARAMS, deltas))
    total_weight = sum(weights_by_param[param] for param in PARAMS)
    return weighted_sum / total_weight

def find_most_improved_players(prevSeason,currSeason):
    asa = AmericanSoccerAnalysis()
    print("Fetching data for both seasons...")
    team_data = asa.get_teams(leagues=["mls"])

    data_prev = get_data(prevSeason)
    data_curr = get_data(currSeason)
    data_prev = pd.merge(data_prev, team_data, on='team_id', how='left')
    data_curr = pd.merge(data_curr, team_data, on='team_id', how='left')


    timbers_prev = data_prev[data_prev['team_abbreviation'] == ('POR')]
    timbers_curr = data_curr[data_curr['team_abbreviation'] == ('POR')]

    # Get all unique Timbers players who appear in both seasons
    players_prev = set(timbers_prev['player_name'].unique())
    players_curr = set(timbers_curr['player_name'].unique())
    common_players = list(players_prev & players_curr)

    print(f"Found {len(common_players)} players with data in both seasons...")

    improvement_scores = []

    for player in common_players:
        try:
            prev_rows = timbers_prev[timbers_prev['player_name'] == player]
            curr_rows = timbers_curr[timbers_curr['player_name'] == player]
            pos_prev, pos_curr = resolve_comparable_position(player, prev_rows, curr_rows)

            # Sanity check to ensure we're comparing same position
            if pos_prev != pos_curr:
                print(f"Skipping {player} due to position mismatch: {pos_prev} vs {pos_curr}")
                continue

            p_curr = calculate_percentiles_with_fallback(
                data_curr,
                player_name=player,
                position=pos_curr,
            )
            p_prev = calculate_percentiles_with_fallback(
                data_prev,
                player_name=player,
                position=pos_prev,
            )

            if len(p_curr) != 6 or len(p_prev) != 6:
                print(f"Skipping {player} due to missing data in percentiles: {p_curr} vs {p_prev}")
                continue  # skip if missing data

            improvement = calculate_weighted_average_percentile_change(
                p_prev,
                p_curr,
                pos_curr,
            )
            improvement_scores.append({
                "player_name": player,
                "position": pos_curr,
                f"{currSeason}_percentiles": p_curr,
                f"{prevSeason}_percentiles": p_prev,
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
    most_improved_df = find_most_improved_players("2025","2026")

    # Optional: Visualize the most improved player
    top_player = most_improved_df.iloc[0]
    print(most_improved_df)
