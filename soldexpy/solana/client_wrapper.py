from solana.rpc.api import Client
from solana.rpc.commitment import Commitment
from solana.rpc.types import TokenAccountOpts
from solders.pubkey import Pubkey
from solders.signature import Signature
from solders.transaction import Transaction, VersionedTransaction


def get_token_account_balance(
    client: Client, address: Pubkey, commitment: Commitment = None
):
    return client.get_token_account_balance(address, commitment)


def get_balance(client: Client, address: Pubkey, commitment: Commitment = None):
    return client.get_balance(address, commitment)


def get_account_info(client: Client, address: Pubkey, commitment: Commitment = None):
    return client.get_account_info(address, commitment)


def get_account_info_json_parsed(
    client: Client, address: Pubkey, commitment: Commitment = None
):
    return client.get_account_info_json_parsed(address, commitment)


def get_token_accounts_by_owner(
    client: Client,
    address: Pubkey,
    opts: TokenAccountOpts,
    commitment: Commitment = None,
):
    return client.get_token_accounts_by_owner(address, opts, commitment)


def get_latest_blockhash(client: Client):
    if client.blockhash_cache:
        try:
            recent_blockhash = client.blockhash_cache.get()
        except:
            recent_blockhash = client.get_latest_blockhash(
                client.commitment
            ).value.blockhash
    else:
        recent_blockhash = client.get_latest_blockhash(
            client.commitment
        ).value.blockhash

    return recent_blockhash


def send_transaction(client: Client, transaction: VersionedTransaction):
    return client.send_transaction(transaction)


def confirm_transaction(
    client: Client,
    txn_signature: Signature,
    commitment: Commitment,
    sleep_seconds: float,
):
    return client.confirm_transaction(txn_signature, commitment, sleep_seconds)


def simulate_transaction(
    client: Client,
    transaction: VersionedTransaction,
    sig_verify: bool,
    commitment: Commitment,
):
    return client.simulate_transaction(transaction, sig_verify, commitment)


def get_token_supply(client: Client, address: Pubkey, commitment: Commitment):
    return client.get_token_supply(address)
