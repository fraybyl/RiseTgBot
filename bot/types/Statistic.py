import orjson


class Statistic(dict):
    def __init__(
            self,
            total_accounts: int,
            total_bans: int,
            total_vac: int,
            total_community: int,
            total_game_ban: int,
            bans_in_last_week: int,
            items: int,
            cases: int,
            prices: int
    ) -> None:
        super().__init__(
            total_accounts=total_accounts,
            total_bans=total_bans,
            total_vac=total_vac,
            total_community=total_community,
            total_game_ban=total_game_ban,
            bans_in_last_week=bans_in_last_week,
            items=items,
            cases=cases,
            prices=prices
        )

    @classmethod
    def from_dict(cls, bans: dict, inventories: dict):
        return cls(
            total_accounts=bans['total_accounts'],
            total_bans=bans['total_bans'],
            total_vac=bans['total_vac'],
            total_community=bans['total_community'],
            total_game_ban=bans['total_game_ban'],
            bans_in_last_week=bans['bans_in_last_week'],
            items=len(inventories['items']),
            cases=len(inventories['cases']),
            prices=inventories['prices']  # исправить инвентари
        )

    def to_dict(self) -> str:
        return orjson.dumps(self).decode('utf-8')

    @property
    def total_accounts(self) -> int:
        return self['total_accounts']

    @property
    def total_bans(self) -> int:
        return self['total_bans']

    @property
    def total_vac(self) -> int:
        return self['total_vac']

    @property
    def total_community(self) -> int:
        return self['total_community']

    @property
    def total_game_ban(self) -> int:
        return self['total_game_ban']

    @property
    def bans_in_last_week(self) -> int:
        return self['bans_in_last_week']

    @property
    def items(self) -> int:
        return self['items']

    @property
    def cases(self) -> int:
        return self['cases']

    @property
    def prices(self) -> int:
        return self['prices']
