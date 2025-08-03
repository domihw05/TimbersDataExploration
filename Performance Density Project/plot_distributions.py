from helper_funcs import import_asa_timbers_data, wrangle_data, plot_a_game, normalize_data


if __name__ == '__main__':
    raw_data_imported = import_asa_timbers_data()
    main_df = wrangle_data(raw_data_imported)
    #plot_on_one_graph(main_df,"output",True)
    plot_a_game(normalize_data(main_df),'2025-07-17','RSL',True,"output",True)

