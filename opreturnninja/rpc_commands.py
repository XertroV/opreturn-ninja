

def list_nulldata(params):
    return None

whitelist = [
    'getinfo',
    'gettransaction',
    'sendrawtransaction',
    'getrawtransaction',
    'gettxout',
]

custom_methods = {
    'listnulldata': list_nulldata,
}