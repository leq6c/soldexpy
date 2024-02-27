from solana.rpc.api import Client
from solana.rpc.commitment import Commitment
from solana.rpc.types import TokenAccountOpts
from solders.pubkey import Pubkey
from solders.rpc.responses import (
    GetAccountInfoJsonParsedResp,
    GetAccountInfoResp,
    GetBalanceResp,
    GetLatestBlockhashResp,
    GetTokenAccountBalanceResp,
    GetTokenAccountsByOwnerResp,
)

from tests.solana.mock_client_cache import MockClientCache


# override the client wrapper to use the mock client cache
class MockClientWrapper:
    def __init__(self, cache: MockClientCache):
        self.cache = cache

    def get_token_account_balance(
        self, client: Client, address: Pubkey, commitment: Commitment = None
    ):
        resp_json = self.cache["get_token_account_balance"][str(address)]
        return GetTokenAccountBalanceResp.from_json(resp_json)

    def get_balance(
        self, client: Client, address: Pubkey, commitment: Commitment = None
    ):
        resp_json = self.cache["get_balance"][str(address)]
        return GetBalanceResp.from_json(resp_json)

    def get_account_info(
        self, client: Client, address: Pubkey, commitment: Commitment = None
    ):
        resp_json = self.cache["get_account_info"][str(address)]
        return GetAccountInfoResp.from_json(resp_json)

    def get_account_info_json_parsed(
        self, client: Client, address: Pubkey, commitment: Commitment = None
    ):
        resp_json = self.cache["get_account_info_json_parsed"][str(address)]
        return GetAccountInfoJsonParsedResp.from_json(resp_json)

    def get_token_accounts_by_owner(
        self,
        client: Client,
        address: Pubkey,
        opts: TokenAccountOpts,
        commitment: Commitment = None,
    ):
        resp_json = self.cache["get_token_accounts_by_owner"][str(address)]
        return GetTokenAccountsByOwnerResp.from_json(resp_json)

    def get_latest_blockhash(self, client: Client):
        resp_json = self.cache["get_latest_blockhash"]
        return GetLatestBlockhashResp.from_json(resp_json)
