def simulate_investment_strategy(initial_accounts_str, account_cost_str, weekly_profit_per_account_str, total_weeks_str,
                                 reinvest_ratio_str):
    # Parse inputs once
    initial_accounts = int(initial_accounts_str)
    account_cost = float(account_cost_str)
    weekly_profit_per_account = float(weekly_profit_per_account_str)
    total_weeks = int(total_weeks_str)
    reinvest_ratio = float(reinvest_ratio_str)

    # Initialize variables
    accumulated_profit = 0.0
    accumulated_savings = 0.0

    # Precompute values to minimize operations in the loop
    weekly_profit_reinvest_ratio = weekly_profit_per_account * reinvest_ratio
    weekly_profit_saving_ratio = weekly_profit_per_account * (1 - reinvest_ratio)

    # Simulate the investment strategy
    for _ in range(total_weeks):
        accumulated_profit += initial_accounts * weekly_profit_reinvest_ratio
        accumulated_savings += initial_accounts * weekly_profit_saving_ratio

        if accumulated_profit >= account_cost:
            additional_accounts = int(accumulated_profit // account_cost)
            initial_accounts += additional_accounts
            accumulated_profit -= additional_accounts * account_cost

    # Add remaining accumulated profit to savings
    accumulated_savings += accumulated_profit

    return initial_accounts, accumulated_savings
