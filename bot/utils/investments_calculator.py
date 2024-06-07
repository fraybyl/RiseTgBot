def simulate_investment_strategy(initial_accounts_str, account_cost_str, weekly_profit_per_account_str, total_weeks_str, reinvest_ratio_str):
    initial_accounts = int(initial_accounts_str)
    account_cost = float(account_cost_str)
    weekly_profit_per_account = float(weekly_profit_per_account_str)
    total_weeks = int(total_weeks_str)
    reinvest_ratio = float(reinvest_ratio_str)
    
    accumulated_profit = 0
    accumulated_savings = 0
    accounts_over_time = []
    current_accounts = initial_accounts
        
    for week in range(total_weeks):
        # Вычисляем еженедельную прибыль
        weekly_profit = current_accounts * weekly_profit_per_account
        
        # Определяем суммы для реинвестирования и сохранения
        reinvestment_amount = weekly_profit * reinvest_ratio
        saving_amount = weekly_profit * (1 - reinvest_ratio)
        
        # Добавляем суммы к накопленным
        accumulated_profit += reinvestment_amount
        accumulated_savings += saving_amount
        
        # Проверяем, можем ли мы купить новые аккаунты
        while accumulated_profit >= account_cost:
            current_accounts += 1
            accumulated_profit -= account_cost
        
        # Записываем состояние на каждую неделю
        accounts_over_time.append((week + 1, current_accounts, accumulated_profit, accumulated_savings))
    
    return accounts_over_time[-1], accounts_over_time
