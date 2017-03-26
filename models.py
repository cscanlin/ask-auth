from datetime import datetime, timedelta

from pynamodb.models import Model
from pynamodb.attributes import NumberAttribute, UnicodeAttribute, UTCDateTimeAttribute

class AlexaUser(Model):
    class Meta:
        table_name = "alexa-users"

    userId = UnicodeAttribute(hash_key=True)
    name = UnicodeAttribute(null=True)

class Client(Model):
    class Meta:
        table_name = "alexa-clients"
    client_id = UnicodeAttribute(hash_key=True)
    name = UnicodeAttribute()
    client_secret = UnicodeAttribute()
    client_type = UnicodeAttribute()
    _redirect_uris = UnicodeAttribute()
    default_scope = UnicodeAttribute()

    @property
    def redirect_uris(self):
        if self._redirect_uris:
            return self._redirect_uris.split()
        return []

    @property
    def default_redirect_uri(self):
        return self.redirect_uris[0]

    @property
    def default_scopes(self):
        if self.default_scope:
            return self.default_scope.split()
        return []

class Grant(Model):
    class Meta:
        table_name = "alexa-grants"
    id = NumberAttribute(hash_key=True)
    userId = UnicodeAttribute(range_key=True)

    client_id = UnicodeAttribute()
    code = UnicodeAttribute()

    redirect_uri = UnicodeAttribute()
    scope = UnicodeAttribute()
    expires = UTCDateTimeAttribute()

    def user(self):
        return next(AlexaUser.query(self.userId))

    def delete(self):
        self.delete()

    @property
    def scopes(self):
        if self.scope:
            return self.scope.split()
        return None


class Token(Model):
    class Meta:
        table_name = "alexa-tokens"
    id = NumberAttribute(hash_key=True)
    client_id = UnicodeAttribute()
    userId = UnicodeAttribute(range_key=True)
    token_type = UnicodeAttribute()
    access_token = UnicodeAttribute()
    refresh_token = UnicodeAttribute()
    expires = UTCDateTimeAttribute()
    scope = UnicodeAttribute()

    def __init__(self, **kwargs):
        expires_in = kwargs.pop('expires_in', None)
        if expires_in is not None:
            self.expires = datetime.utcnow() + timedelta(seconds=expires_in)

        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def scopes(self):
        if self.scope:
            return self.scope.split()
        return []

    def delete(self):
        self.delete()


if __name__ == '__main__':
    AlexaUser.create_table(read_capacity_units=1, write_capacity_units=1)
    Client.create_table(read_capacity_units=1, write_capacity_units=1)
    Grant.create_table(read_capacity_units=1, write_capacity_units=1)
    Token.create_table(read_capacity_units=1, write_capacity_units=1)
