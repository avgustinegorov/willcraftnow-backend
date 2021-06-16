class BaseParser:
    def __init__(self, data=None, user=None, entities=[], assets=[]):
        self.data = data
        self.user = user
        self.entities = entities
        self.assets = assets

    def parse(self):
        return self.data
