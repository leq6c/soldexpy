# holding the mock client cache class for testing and having the ability to amend the cache for testing purposes
class MockClientCache:
    def __init__(self, cache):
        self.cache = cache

    def get_pool_address_for_tests(self):
        return self.cache["pool_address"]

    def amend_cache_for_balance(self, address, ui_amount, decimals, amount):
        self.cache["get_token_account_balance"][str(address)] = (
            '{"result":{"context":{"slot":0,"apiVersion":"0"},"value":{"uiAmount":'
            + str(ui_amount)
            + ',"decimals":'
            + str(decimals)
            + ',"amount":"'
            + str(amount)
            + '","uiAmountString":"'
            + str(ui_amount)
            + '"}},"id":0}'
        )

    def amend_cache_for_sol_balance(self, address, amount):
        self.cache["get_balance"][str(address)] = (
            '{"jsonrpc":"2.0","result":{"context":{"slot":0,"apiVersion":"0"},"value":'
            + str(amount)
            + '},"id":0}'
        )

    def __getitem__(self, key):
        return self.cache[key]

    def __setitem__(self, key, value):
        self.cache[key] = value
