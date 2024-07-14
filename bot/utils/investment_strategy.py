from decimal import Decimal, DecimalException

from loguru import logger


def simulate_investment_strategy(
        initial_accounts: int,
        account_cost: float,
        weekly_profit_per_account: float,
        total_weeks: int,
        reinvest_ratio: float
) -> tuple[int, float, int] | tuple[int, str, str]:
    """
    Симулирует стратегию инвестирования на основе заданных параметров.

    Args:
        initial_accounts (int): Начальное количество аккаунтов.
        account_cost (float): Стоимость одного аккаунта.
        weekly_profit_per_account (float): Недельная прибыль с одного аккаунта.
        total_weeks (int): Общее количество недель для симуляции.
        reinvest_ratio (float): Доля прибыли, которая реинвестируется.

    Returns:
        tuple: Кортеж из двух элементов:
            - int: Итоговое количество аккаунтов после симуляции.
            - float: Накопленные сбережения после симуляции.
            - int: Количество добавленных аккаунтов после симуляции.
            Если ошибка , возвращает start_accounts, 'очень много', 'Слишком большие значения'.
    """
    start_accounts = initial_accounts
    try:
        accumulated_profit = Decimal('0.0')
        accumulated_savings = Decimal('0.0')

        # Convert float inputs to Decimal
        account_cost = Decimal(str(account_cost))
        weekly_profit_per_account = Decimal(str(weekly_profit_per_account))
        reinvest_ratio = Decimal(str(reinvest_ratio))

        # Precompute values to minimize operations in the loop
        weekly_profit_reinvest_ratio = weekly_profit_per_account * reinvest_ratio
        weekly_profit_saving_ratio = weekly_profit_per_account * (Decimal('1') - reinvest_ratio)

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

        # Prepare the results
        final_accounts = initial_accounts
        total_savings = float(accumulated_savings)  # Convert to float if needed
        accounts_added = final_accounts - start_accounts

    except (Exception, DecimalException):
        logger.info('Какой то приколист вписал большие числа в стратегию')
        return start_accounts, 'очень много', 'Слишком большие значения'

    return final_accounts, total_savings, accounts_added
