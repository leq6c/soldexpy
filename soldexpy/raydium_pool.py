import base58
from solana.rpc.api import Client
from solders.pubkey import Pubkey

from soldexpy.common.direction import Direction
from soldexpy.common.reference_address import RAYDIUM_AMM_AUTHORITY, SOL_MINT_ADDRESS
from soldexpy.common.unit import Unit
from soldexpy.solana_util.raydium_pool_info import (
    get_lp_token_address,
    get_mint_address,
    get_pool_info,
    get_pool_vaults_balance,
    get_pool_vaults_decimals,
    get_token_program_id,
)
from soldexpy.solana_util.serum_market_info import get_market_info, get_vault_signer


class RaydiumPool:
    def __init__(self, client: Client, pool_address: str):
        self.client = client
        self.subscription = None
        self.price_changes_callbacks = []
        self.pool_address = pool_address
        self.pool_info = get_pool_info(client, pool_address)
        self.market_info = get_market_info(client, self.pool_info.market_id)
        self.amm_id = Pubkey(base58.b58decode(pool_address))
        self.amm_authority = RAYDIUM_AMM_AUTHORITY
        self.amm_open_orders = Pubkey(self.pool_info.open_orders)
        self.amm_target_orders = Pubkey(self.pool_info.target_orders)
        self.pool_coin_token_account = Pubkey(self.pool_info.base_vault)
        self.pool_pc_token_account = Pubkey(self.pool_info.quote_vault)
        self.market_program_id = Pubkey(self.pool_info.market_program_id)
        self.serum_market = Pubkey(self.pool_info.market_id)
        self.serum_bids = Pubkey(self.market_info.bids)
        self.serum_asks = Pubkey(self.market_info.asks)
        self.serum_event_queue = Pubkey(self.market_info.event_queue)
        self.serum_coin_vault_account = Pubkey(self.market_info.base_vault)
        self.serum_pc_vault_account = Pubkey(self.market_info.quote_vault)
        self.serum_vault_signer = get_vault_signer(client, self.market_info.base_vault)
        self.base_mint_address = get_mint_address(client, self.pool_info.base_vault)
        self.quote_mint_address: Pubkey = get_mint_address(
            client, self.pool_info.quote_vault
        )
        self.base_decimals, self.quote_decimals = get_pool_vaults_decimals(
            client, self.pool_coin_token_account, self.pool_pc_token_account
        )
        self.token_program_id = get_token_program_id(client, self.base_mint_address)
        self.lp_token_address = get_lp_token_address(self.pool_info.market_id)

        if self.base_mint_address == SOL_MINT_ADDRESS:
            # reverse if base token is SOL
            self.base_mint_address, self.quote_mint_address = (
                self.quote_mint_address,
                self.base_mint_address,
            )
            self.base_decimals, self.quote_decimals = (
                self.quote_decimals,
                self.base_decimals,
            )
            self.token_program_id = get_token_program_id(client, self.base_mint_address)
            self.pool_info.base_vault, self.pool_info.quote_vault = (
                self.pool_info.quote_vault,
                self.pool_info.base_vault,
            )

        if self.quote_mint_address == SOL_MINT_ADDRESS:
            self.quote_token = "SOL"
        else:
            raise Exception("Unsupported quote token")

        self.update_pool_vaults_balance()

    def to_dict(self):
        return {
            "pool_address": self.pool_address,
            "pool_info": self.pool_info,
            "market_info": self.market_info,
            "amm_id": self.amm_id,
            "amm_authority": self.amm_authority,
            "amm_open_orders": self.amm_open_orders,
            "amm_target_orders": self.amm_target_orders,
            "pool_coin_token_account": self.pool_coin_token_account,
            "pool_pc_token_account": self.pool_pc_token_account,
            "market_program_id": self.market_program_id,
            "serum_market": self.serum_market,
            "serum_bids": self.serum_bids,
            "serum_asks": self.serum_asks,
            "serum_event_queue": self.serum_event_queue,
            "serum_coin_vault_account": self.serum_coin_vault_account,
            "serum_pc_vault_account": self.serum_pc_vault_account,
            "serum_vault_signer": self.serum_vault_signer,
            "base_mint_address": self.base_mint_address,
            "quote_mint_address": self.quote_mint_address,
            "base_decimals": self.base_decimals,
            "quote_decimals": self.quote_decimals,
            "token_program_id": self.token_program_id,
            "lp_token_address": self.lp_token_address,
        }

    def get_mint_address(self):
        return self.base_mint_address

    def update_pool_vaults_balance(self, commitment: str = "confirmed"):
        self.base_vault_balance, self.quote_vault_balance = get_pool_vaults_balance(
            self.client,
            Pubkey(self.pool_info.base_vault),
            Pubkey(self.pool_info.quote_vault),
            commitment,
        )

    def get_price(
        self,
        in_amount: float,
        direction: Direction,
        return_price_unit: Unit = Unit.QUOTE_TOKEN,
        update_vault_balance=False,
        commitment="confirmed",
    ):
        """
        Returns:
            [0]: estimated price based on in_amount (you can change the unit by return_price_unit)
            [1]: estimated price based on the pool balance
            [2]: expected amount-out. you can use this amount for the min amount out along with your slippage allowance
            [3]: expected amount-in that deducted the swap fee and the network fee
        """
        if update_vault_balance:
            self.update_pool_vaults_balance(commitment)
        base_vault_balance = self.base_vault_balance
        quote_vault_balance = self.quote_vault_balance

        # Swap fee: 0.25%
        swap_fee = 0.25
        # Network fee: don't consider network fee for now since it's pratically small (@TODO: fix me)
        network_fee = 0.00

        # k = x * y
        pool_k = base_vault_balance * quote_vault_balance

        if direction == Direction.SPEND_QUOTE_TOKEN:
            # for the quote pool, + in_amount
            delta_quote_vault = in_amount
            # swap fee would be deducted from the quote amount
            delta_quote_vault -= in_amount * (swap_fee / 100)
            # network fee
            delta_quote_vault -= network_fee
            # calculate delta base_vault
            delta_base_vault = base_vault_balance - pool_k / (
                quote_vault_balance + delta_quote_vault
            )
        elif direction == Direction.SPEND_BASE_TOKEN:
            # for the base pool, + in_amount
            delta_base_vault = in_amount
            # swap fee would be deducted from the base amount
            delta_base_vault -= in_amount * (swap_fee / 100)
            # network fee
            delta_base_vault -= network_fee
            # calculate delta quote_vault
            delta_quote_vault = quote_vault_balance - pool_k / (
                base_vault_balance + delta_base_vault
            )
        else:
            raise Exception("Unsupported direction")

        base_price = base_vault_balance / quote_vault_balance
        price = delta_base_vault / delta_quote_vault

        if return_price_unit == Unit.BASE_TOKEN:
            return_price = price
            return_base_price = base_price
        elif return_price_unit == Unit.QUOTE_TOKEN:
            return_price = 1 / price
            return_base_price = 1 / base_price
        else:
            raise Exception("Unsupported return price unit")

        if direction == Direction.SPEND_QUOTE_TOKEN:
            return return_price, return_base_price, delta_base_vault, delta_quote_vault
        elif direction == Direction.SPEND_BASE_TOKEN:
            return return_price, return_base_price, delta_quote_vault, delta_base_vault
        else:
            raise Exception("Unsupported direction")

    def convert_base_token_amount_to_tx_format(self, amount: float):
        return int(amount * 10 ** (self.base_decimals))

    def convert_quote_token_amount_to_tx_format(self, amount: float):
        return int(amount * 10 ** (self.quote_decimals))

    def convert_base_token_amount_from_tx_format(self, amount: int):
        return amount / 10 ** (self.base_decimals)

    def convert_quote_token_amount_from_tx_format(self, amount: int):
        return amount / 10 ** (self.quote_decimals)
