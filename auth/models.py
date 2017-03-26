from datetime import datetime, timedelta

from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, UTCDateTimeAttribute

class AlexaUser(Model):

    class Meta:
        table_name = "alexa-users"

    userId = UnicodeAttribute(hash_key=True)
    name = UnicodeAttribute(null=True)

class Client(Model):

    class Meta:
        table_name = "alexa-clients"

    client_id = UnicodeAttribute(hash_key=True)
    client_secret = UnicodeAttribute()
    _redirect_uris = UnicodeAttribute()
    scope = UnicodeAttribute()

    @property
    def client_type(self):
        return 'confidential'

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
        if self.scope:
            return self.scope.split()
        return []

class Grant(Model):

    class Meta:
        table_name = "alexa-grants"

    userId = UnicodeAttribute()

    client_id = UnicodeAttribute(hash_key=True)
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

    access_token = UnicodeAttribute(hash_key=True)
    client_id = UnicodeAttribute()
    userId = UnicodeAttribute()
    token_type = UnicodeAttribute()
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

    client = Client(
        client_id='ask-auth-dev',
        client_secret='ask-auth-dev',
        scope='ask-auth-dev',
        _redirect_uris=' '.join((
            'https://layla.amazon.com/api/skill/link/M1GSQ6I3501WFX',
            'https://pitangui.amazon.com/api/skill/link/M1GSQ6I3501WFX',
        ))
    )
    client.save()
