class InventoryDescription(dict):
    def __init__(
            self,
            app_id: int,
            class_id: str,
            instance_id: str,
            currency: int,
            background_color: str,
            icon_url: str,
            descriptions: list[any],
            tradable: int,
            actions: list[any],
            name: str,
            name_color: str,
            type: str,
            market_name: str,
            market_hash_name: str,
            market_actions: list[any],
            commodity: int,
            market_tradable_restriction: int,
            marketable: int,
            tags: list[any]
    ):
        super().__init__(
            appid=app_id,
            classid=class_id,
            instanceid=instance_id,
            currency=currency,
            background_color=background_color,
            icon_url=icon_url,
            descriptions=descriptions,
            tradable=tradable,
            actions=actions,
            name=name,
            name_color=name_color,
            type=type,
            market_name=market_name,
            market_hash_name=market_hash_name,
            market_actions=market_actions,
            commodity=commodity,
            market_tradable_restriction=market_tradable_restriction,
            marketable=marketable,
            tags=tags
        )

    @classmethod
    def from_dict(cls, data: dict[str, any]):
        return cls(
            app_id=data['appid'],
            class_id=data['classid'],
            instance_id=data['instanceid'],
            currency=data['currency'],
            background_color=data['background_color'],
            icon_url=data['icon_url'],
            descriptions=data['descriptions'],
            tradable=data['tradable'],
            actions=data.get('actions', []),
            name=data['name'],
            name_color=data['name_color'],
            type=data['type'],
            market_name=data['market_name'],
            market_hash_name=data['market_hash_name'],
            market_actions=data.get('market_actions', []),
            commodity=data['commodity'],
            market_tradable_restriction=data['market_tradable_restriction'],
            marketable=data['marketable'],
            tags=data['tags']
        )

    @classmethod
    def from_list(cls, list_of_dicts: list[dict]):
        return [cls.from_dict(item) for item in list_of_dicts]

    @property
    def app_id(self):
        return self['appid']

    @property
    def class_id(self):
        return self['classid']

    @property
    def instance_id(self):
        return self['instanceid']

    @property
    def currency(self):
        return self['currency']

    @property
    def background_color(self):
        return self['background_color']

    @property
    def icon_url(self):
        return self['icon_url']

    @property
    def descriptions(self):
        return self['descriptions']

    @property
    def tradable(self):
        return self['tradable']

    @property
    def actions(self):
        return self['actions']

    @property
    def name(self):
        return self['name']

    @property
    def name_color(self):
        return self['name_color']

    @property
    def type(self):
        return self['type']

    @property
    def market_name(self):
        return self['market_name']

    @property
    def market_hash_name(self):
        return self['market_hash_name']

    @property
    def market_actions(self):
        return self['market_actions']

    @property
    def commodity(self):
        return self['commodity']

    @property
    def market_tradable_restriction(self):
        return self['market_tradable_restriction']

    @property
    def marketable(self):
        return self['marketable']

    @property
    def tags(self):
        return self['tags']
