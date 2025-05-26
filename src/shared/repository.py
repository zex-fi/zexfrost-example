class Repo:
    def __init__(self):
        self.db = {}

    def set(self, key: str, value):
        self.db[key] = value

    def get(self, key: str):
        return self.db.get(key)

    def delete(self, key: str):
        del self.db[key]
