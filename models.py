from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute

class AlexaUser(Model):

    class Meta:
        table_name = "alexa-users"

    userId = UnicodeAttribute(hash_key=True)
    name = UnicodeAttribute()

if __name__ == '__main__':
    AlexaUser.create_table(read_capacity_units=1, write_capacity_units=1)
