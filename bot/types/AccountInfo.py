from dataclasses import dataclass, asdict

import orjson


@dataclass
class AccountInfo:
    """Класс для хранения информации о Steam аккаунте."""

    SteamId: int
    CommunityBanned: bool
    VACBanned: bool
    NumberOfVACBans: int
    DaysSinceLastBan: int
    NumberOfGameBans: int
    EconomyBan: str

    @classmethod
    def from_dict(cls, data: dict[str, any]) -> 'AccountInfo':
        """Создает объект AccountInfo из словаря."""
        return cls(
            SteamId=data['SteamId'],
            CommunityBanned=data['CommunityBanned'],
            VACBanned=data['VACBanned'],
            NumberOfVACBans=data['NumberOfVACBans'],
            DaysSinceLastBan=data['DaysSinceLastBan'],
            NumberOfGameBans=data['NumberOfGameBans'],
            EconomyBan=data['EconomyBan']
        )

    @classmethod
    def from_json(cls, json_data: str) -> 'AccountInfo':
        """Создает объект AccountInfo из JSON данных."""
        data = orjson.loads(json_data)
        return cls.from_dict(data)

    def to_dict(self) -> dict:
        """Преобразует объект AccountInfo в словарь."""
        return asdict(self)

    def to_json(self) -> bytes:
        """Преобразует объект AccountInfo в JSON байты."""
        return orjson.dumps(self.to_dict())

    def ban_in_last_week(self) -> bool:
        """Проверяет, был ли бан в последнюю неделю."""
        return 0 < self.DaysSinceLastBan <= 7

    def is_banned(self) -> bool:
        """Проверяет, забанен ли аккаунт."""
        return (self.CommunityBanned or
                self.VACBanned or
                self.NumberOfVACBans > 0 or
                self.NumberOfGameBans > 0 or
                self.EconomyBan != 'none')
