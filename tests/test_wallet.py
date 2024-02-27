from solana.rpc.api import Client
from solders.keypair import Keypair
from solders.token.associated import get_associated_token_address

from soldexpy.raydium_pool import RaydiumPool
from soldexpy.wallet import Wallet
from tests.solana.mock_client_cache import MockClientCache


def test_constructor(client: Client):
    """
    Test the constructor of Wallet
    """
    payer = Keypair().pubkey()
    wallet = Wallet(client, payer)
    assert wallet.client == client
    assert wallet.payer == payer


def test_get_balance(
    pool: RaydiumPool, wallet: Wallet, mock_client_cache: MockClientCache
):
    """
    Test get_balance method of Wallet
    """
    associated_addr = get_associated_token_address(
        wallet.payer, pool.get_mint_address()
    )
    mock_client_cache.amend_cache_for_balance(
        associated_addr, 4757782.728947, 6, 4757782728947
    )
    balance_decimal, balance_full = wallet.get_balance(pool)
    assert balance_decimal == 4757782.728947
    assert balance_full == 4757782728947


def test_get_sol_balance(wallet: Wallet, mock_client_cache: MockClientCache):
    """
    Test get_sol_balance method of Wallet
    """
    mock_client_cache.amend_cache_for_sol_balance(wallet.payer, 1050000000)
    balance = wallet.get_sol_balance()
    assert balance == 1.05
