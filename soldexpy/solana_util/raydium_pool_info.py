import base58
from solana.rpc.api import Client
from solders.pubkey import Pubkey

import soldexpy.solana.client_wrapper as client_wrapper
from soldexpy.common.reference_address import RAYDIUM_LIQUIDITY_POOL_V4
from soldexpy.layout.raydium_layout import LIQUIDITY_STATE_LAYOUT_V4


def get_pool_info(client: Client, pool_address: str):
    target_token_pool_pub_key = Pubkey(base58.b58decode(pool_address))
    pool_info = client_wrapper.get_account_info(client, target_token_pool_pub_key)
    return LIQUIDITY_STATE_LAYOUT_V4.parse(pool_info.value.data)


def get_pool_vaults(client: Client, pool_address: str):
    pool_info = get_pool_info(client, pool_address)
    base_vault = pool_info.base_vault
    quote_vault = pool_info.quote_vault
    return Pubkey(base_vault), Pubkey(quote_vault)


def get_lp_token_address(pool_info_market_id: str):
    buffer_text = b"lp_mint_associated_seed"
    program_addr, _ = Pubkey.find_program_address(
        [
            bytes(RAYDIUM_LIQUIDITY_POOL_V4),
            bytes(pool_info_market_id),
            buffer_text,
        ],
        RAYDIUM_LIQUIDITY_POOL_V4,
    )
    return program_addr


def get_pool_vaults_balance(
    client: Client, base_vault: Pubkey, quote_vault: Pubkey, commitment="confirmed"
):
    base_vault_token_account_balance = client_wrapper.get_token_account_balance(
        client, base_vault, commitment=commitment
    )
    quote_vault_token_account_balance = client_wrapper.get_token_account_balance(
        client, quote_vault, commitment=commitment
    )
    return int(base_vault_token_account_balance.value.amount) / 10 ** int(
        base_vault_token_account_balance.value.decimals
    ), int(quote_vault_token_account_balance.value.amount) / 10 ** int(
        quote_vault_token_account_balance.value.decimals
    )


def get_pool_vaults_decimals(client: Client, base_vault: Pubkey, quote_vault: Pubkey):
    base_vault_token_account_balance = client_wrapper.get_token_account_balance(
        client, base_vault
    )
    quote_vault_token_account_balance = client_wrapper.get_token_account_balance(
        client, quote_vault
    )
    return int(base_vault_token_account_balance.value.decimals), int(
        quote_vault_token_account_balance.value.decimals
    )


def get_mint_address(client: Client, token_account: any):
    if type(token_account) == str:
        token_account_pub_key = Pubkey(base58.b58decode(token_account))
    else:
        token_account_pub_key = Pubkey(token_account)
    token_account_info = client_wrapper.get_account_info_json_parsed(
        client, token_account_pub_key
    )
    addr_str = token_account_info.value.data.parsed["info"]["mint"]
    return Pubkey(base58.b58decode(addr_str))


def get_token_program_id(client: Client, mint_address: Pubkey):
    token_account_info = client_wrapper.get_account_info_json_parsed(
        client, mint_address
    )
    return token_account_info.value.owner
