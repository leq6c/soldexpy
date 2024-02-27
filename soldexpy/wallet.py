from decimal import Decimal

from solana.rpc.api import Client
from solders.pubkey import Pubkey
from solders.rpc.errors import InvalidParamsMessage
from solders.token.associated import get_associated_token_address

import soldexpy.solana.client_wrapper as client_wrapper
from soldexpy.raydium_pool import RaydiumPool


class Wallet:
    def __init__(self, client: Client, payer: Pubkey):
        self.client = client
        self.payer = payer

    def get_balance(self, pool: RaydiumPool, commitment: str = "confirmed"):
        address = get_associated_token_address(self.payer, pool.get_mint_address())
        balance_resp = client_wrapper.get_token_account_balance(
            self.client, address, commitment
        )
        if type(balance_resp) == InvalidParamsMessage:
            return 0
        return float(balance_resp.value.amount) / 10 ** int(
            balance_resp.value.decimals
        ), int(balance_resp.value.amount)

    def get_sol_balance(self):
        balance_resp = client_wrapper.get_balance(self.client, self.payer)
        return balance_resp.value / 10**9
