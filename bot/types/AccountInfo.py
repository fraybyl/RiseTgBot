import orjson


class AccountInfo(dict):
    def __init__(self,
                 steam_id: int,
                 community_banned: bool,
                 vac_banned: bool,
                 number_of_vac_bans: int,
                 days_since_last_ban: int,
                 number_of_game_bans: int,
                 economy_ban: str):
        super().__init__(
            SteamId=steam_id,
            CommunityBanned=community_banned,
            VACBanned=vac_banned,
            NumberOfVACBans=number_of_vac_bans,
            DaysSinceLastBan=days_since_last_ban,
            NumberOfGameBans=number_of_game_bans,
            EconomyBan=economy_ban
        )

    @classmethod
    def from_dict(cls, data: dict[str, any]):
        return cls(
            steam_id=data['SteamId'],
            community_banned=data['CommunityBanned'],
            vac_banned=data['VACBanned'],
            number_of_vac_bans=data['NumberOfVACBans'],
            days_since_last_ban=data['DaysSinceLastBan'],
            number_of_game_bans=data['NumberOfGameBans'],
            economy_ban=data['EconomyBan']
        )

    def to_dict(self) -> bytes:
        return orjson.dumps(self)

    @property
    def steam_id(self) -> str:
        return self['SteamId']

    @property
    def community_banned(self) -> bool:
        return self['CommunityBanned']

    @property
    def vac_banned(self) -> bool:
        return self['VACBanned']

    @property
    def number_of_vac_bans(self) -> int:
        return self['NumberOfVACBans']

    @property
    def days_since_last_ban(self) -> int:
        return self['DaysSinceLastBan']

    @property
    def number_of_game_bans(self) -> int:
        return self['NumberOfGameBans']

    @property
    def economy_ban(self) -> str:
        return self['EconomyBan']
