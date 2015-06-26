__author__ = 'Evren Esat Ozkan'


# form creation, validation etc.

def get_form(name, **kwargs):
    return [{
        "schema": {
            "title": "Add Student",
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "title": "Name"
                },
                "email": {
                    "type": "email",
                    "title": "Email"
                }
            },
            "required": ["email", "name"]
        },
        "form": [
            {
                "key": "email",
                "type": "email",
                "validationMessages": {
                    'emailNotValid': 'Email is not valid!'
                }
            },
            "name"
        ],
        "model": {
            "name": "evren kutar",
            "email": "a@a.com"
        }
    }]
