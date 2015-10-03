import logging

class User:

    def __init__(self, data):
        self.data = data

        self.first_name = data['profile']['first_name'] if 'first_name' in data['profile'] else None
        self.last_name = data['profile']['last_name'] if 'last_name' in data['profile'] else None
        self.avatar = data['profile']['image_original'] if 'image_original' in data['profile'] else None
        self.is_bot = 'is_bot' in data and data['is_bot']

    def get_first_name(self):
        if self.first_name:
            return self.first_name

        return self.name

    def __eq__(self, other):
        return isinstance(other, User) and self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __getattr__(self, name):
        if not name in self.data:
            return None

        return self.data[name]

    def __str__(self):
        return 'User("%s" [%s])' % (self.name, self.id)