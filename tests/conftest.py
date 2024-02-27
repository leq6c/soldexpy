import json
from unittest.mock import MagicMock, patch

from pytest import fixture
from solana.rpc.api import Client
from solders.keypair import Keypair

from soldexpy.raydium_pool import RaydiumPool
from soldexpy.wallet import Wallet
from tests.solana.mock_client_cache import MockClientCache
from tests.solana.mock_client_wrapper import MockClientWrapper


@fixture
def mock_client_cache():
    with open("tests/expected_response.json", "r") as f:
        cache = json.load(f)
    return MockClientCache(cache)


@fixture
def mock_client_wrapper(mock_client_cache: MockClientCache):
    return MockClientWrapper(mock_client_cache)


@fixture
def patch_client_wrapper(mock_client_wrapper: MockClientWrapper):
    with patch.multiple(
        "soldexpy.solana.client_wrapper",
        get_token_account_balance=mock_client_wrapper.get_token_account_balance,
        get_balance=mock_client_wrapper.get_balance,
        get_account_info=mock_client_wrapper.get_account_info,
        get_account_info_json_parsed=mock_client_wrapper.get_account_info_json_parsed,
        get_token_accounts_by_owner=mock_client_wrapper.get_token_accounts_by_owner,
        get_latest_blockhash=mock_client_wrapper.get_latest_blockhash,
    ) as mocks:
        yield mocks


@fixture
def client(patch_client_wrapper) -> Client:
    return Client(None)


@fixture
def pool(client: Client, patch_client_wrapper, mock_client_cache: MockClientCache):
    return RaydiumPool(client, mock_client_cache.get_pool_address_for_tests())


@fixture
def wallet(client) -> Wallet:
    payer = Keypair().pubkey()
    wallet = Wallet(client, payer)
    return wallet
