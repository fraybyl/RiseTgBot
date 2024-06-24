class InventoryAsset(dict):
    def __init__(
        self,
        app_id: int,
        context_id: str,
        asset_id: str,
        class_id: str,
        instance_id: str,
        amount: str
    ):
        super().__init__(
            appid=app_id,
            contextid=context_id,
            assetid=asset_id,
            classid=class_id,
            instanceid=instance_id,
            amount=amount
        )

    @classmethod
    def from_dict(cls, data: dict[str, any]):
        return cls(
            app_id=data['appid'],
            context_id=data['contextid'],
            asset_id=data['assetid'],
            class_id=data['classid'],
            instance_id=data['instanceid'],
            amount=data['amount']
        )

    @classmethod
    def from_list(cls, list_of_dicts: list[dict]):
        return [cls.from_dict(item) for item in list_of_dicts]

    @property
    def app_id(self):
        return self['appid']

    @property
    def context_id(self):
        return self['contextid']

    @property
    def asset_id(self):
        return self['assetid']

    @property
    def class_id(self):
        return self['classid']

    @property
    def instance_id(self):
        return self['instanceid']

    @property
    def amount(self):
        return self['amount']
