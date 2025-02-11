# app.models/wallet_utility_balance_schema.py
from marshmallow import Schema, fields

class WalletBalanceSchema(Schema):
    user_email = fields.Email(required=True)
    balance = fields.Float(required=True, validate=lambda x: x >= 0)

class UtilitiesBalanceSchema(Schema):
    user_email = fields.Email(required=True)
    type = fields.Str(required=True, validate=lambda x: x in ["water", "gas", "energy"])
    units = fields.Float(required=True, validate=lambda x: x >= 0)
