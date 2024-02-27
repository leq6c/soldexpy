import base58
from solana.rpc.api import Client
from solders.pubkey import Pubkey

import soldexpy.solana.client_wrapper as client_wrapper
from soldexpy.layout.serum_layout import MARKET_STATE_LAYOUT_V2


def get_market_info(client: Client, market_address: any):
    if type(market_address) == str:
        market_pub_key = Pubkey(base58.b58decode(market_address))
    else:
        market_pub_key = Pubkey(market_address)
    market_info = client_wrapper.get_account_info(client, market_pub_key)
    return MARKET_STATE_LAYOUT_V2.parse(market_info.value.data)


def get_vault_signer(client: Client, vault_address: any):
    if type(vault_address) == str:
        vault_pub_key = Pubkey(base58.b58decode(vault_address))
    else:
        vault_pub_key = Pubkey(vault_address)
    vault_info = client_wrapper.get_account_info_json_parsed(client, vault_pub_key)
    vault_signer_str = vault_info.value.data.parsed["info"]["owner"]
    return Pubkey(base58.b58decode(vault_signer_str))
