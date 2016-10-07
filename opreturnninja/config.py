import os
import logging


class Config(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.__storage__ = self

    def __getattr__(self, item):
        if item in self:
            return self[item]

    def __setattr__(self, key, value):
        self[key] = value


config = Config()


def set_config(env_key, default, from_string_f=lambda x: x):
    config[env_key] = from_string_f(os.getenv(env_key, default))
    logging.info("Set config k,v: `%s`,`%s`" % (env_key, config[env_key]))


set_config('PORT', 5000, int)
set_config('DEBUG', 'True', str)
config['debug'] = config['DEBUG'].lower() == 'true'


set_config('DATABASE_URL', 'sqlite:///:memory:', str)


set_config('BITCOIN_RPC_USER', 'rpcuser', str)
set_config('BITCOIN_RPC_PASSWORD', 'rpcpassword', str)
set_config('BITCOIN_RPC_HOST', '127.0.0.1', str)
set_config('BITCOIN_RPC_PORT', 8332, int)
