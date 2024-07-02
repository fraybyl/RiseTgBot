from dataclasses import dataclass, asdict
import orjson

from bot.types.AccountInfo import AccountInfo
from bot.types.Inventory import Inventory
from bot.types.Item import Item


@dataclass
class Statistic:
    total_accounts: int = 0
    total_bans: int = 0
    total_vac: int = 0
    total_community: int = 0
    total_game_ban: int = 0
    bans_in_last_week: int = 0
    items: int = 0
    cases: int = 0
    prices: float = 0.0

    def __post_init__(self):
        self.prices = round(self.prices, 2)

    @classmethod
    def from_dict(cls, bans_list: list[AccountInfo], inventory_list: list[Inventory]):
        instance = cls()
        for bans in bans_list:
            instance.add_account_info(bans)
        for inventory in inventory_list:
            instance.add_inventory_info(inventory)
        return instance

    def add_account_info(self, bans: AccountInfo):
        self.total_bans += bans.is_banned()
        self.total_vac += bans.VACBanned
        self.total_community += bans.CommunityBanned
        self.total_game_ban += bans.NumberOfGameBans
        self.bans_in_last_week += bans.ban_in_last_week()

    def add_inventory_info(self, inventory: Inventory):
        self.items += len(inventory.items)
        self.cases += inventory.total_cases()
        self.prices = round(inventory.total_price())

    def to_dict(self) -> str:
        return orjson.dumps(asdict(self)).decode('utf-8')
