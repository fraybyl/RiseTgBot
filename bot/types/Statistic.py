import orjson

from bot.types.AccountInfo import AccountInfo
from bot.types.Inventory import Inventory


class Statistic(dict):
    def __init__(
            self,
            total_accounts: int = 0,
            total_bans: int = 0,
            total_vac: int = 0,
            total_community: int = 0,
            total_game_ban: int = 0,
            bans_in_last_week: int = 0,
            items: int = 0,
            cases: int = 0,
            prices: float = 0.0
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
            prices=round(prices, 2)
        )

    @classmethod
    def from_dict(cls, bans_list: list[AccountInfo], inventory_list: list[Inventory]):
        instance = cls()
        for bans in bans_list:
            instance.add_account_info(bans)
        for inventory in inventory_list:
            instance.add_inventory_info(inventory)
        return instance

    def add_account_info(self, bans: AccountInfo):
        self['total_accounts'] += 1
        self['total_bans'] += bans.is_banned()
        self['total_vac'] += bans.vac_banned
        self['total_community'] += bans.community_banned
        self['total_game_ban'] += bans.number_of_game_bans
        self['bans_in_last_week'] += bans.ban_in_last_week()

    def add_inventory_info(self, inventory: Inventory):
        self['items'] += inventory.total_count()
        self['cases'] += inventory.total_case_items()
        self['prices'] = round(self['prices'] + inventory.total_price(), 2)

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
    def prices(self) -> float:
        return self['prices']
