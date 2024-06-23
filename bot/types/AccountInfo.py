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
            steam_id=data.get('SteamId', 0),
            community_banned=data.get('CommunityBanned', False),
            vac_banned=data.get('VACBanned', False),
            number_of_vac_bans=data.get('NumberOfVACBans', 0),
            days_since_last_ban=data.get('DaysSinceLastBan', 0),
            number_of_game_bans=data.get('NumberOfGameBans', 0),
            economy_ban=data.get('EconomyBan', '')
        )

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



