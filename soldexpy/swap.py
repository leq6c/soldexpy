import asyncio
import json
import time

from solana.rpc.api import Client
from solders.keypair import Keypair

import soldexpy.solana.client_wrapper as client_wrapper
from soldexpy.common.direction import Direction
from soldexpy.common.unit import Unit
from soldexpy.raydium_pool import RaydiumPool
from soldexpy.solana_tx_util.swap_transaction_builder import SwapTransactionBuilder
from soldexpy.solana_util.solana_websocket_subscription import (
    subscribe_to_account_using_queue,
)


class Swap:
    def __init__(
        self,
        client: Client,
        pool: RaydiumPool,
        virtual_amount: int = 1,
        queue_size: int = 100,
        rate_limit_seconds: float = 0.1,
        rate_limit_sleep_seconds: float = 0.01,
        confirm_tx_sleep_seconds: float = 1,
    ):
        self.client = client
        self.pool = pool
        self.virtual_amount = virtual_amount
        self.queue_size = queue_size
        self.rate_limit_seconds = rate_limit_seconds
        self.rate_limit_sleep_seconds = rate_limit_sleep_seconds
        self.confirm_tx_sleep_seconds = confirm_tx_sleep_seconds
        self.price = None
        self.default_keypair = None
        # update local price on init
        self.update_local_price()

    async def run_updater(self):
        await asyncio.gather(
            self.update_local_price_on_changes(),
        )

    def update_local_price(self):
        whatever_the_amount_to_calculate = self.virtual_amount
        _, new_base_price, _, _ = self.pool.get_price(
            whatever_the_amount_to_calculate,
            Direction.SPEND_QUOTE_TOKEN,
            Unit.BASE_TOKEN,
            False,
        )
        if self.price != new_base_price:
            self.price = new_base_price

    async def update_local_price_on_changes(self, websocket_rpc_url: str = None):
        if websocket_rpc_url == None:
            # try to use the same endpoint as the client
            websocket_rpc_url = self.client._provider.endpoint_uri.replace(
                "https:", "wss:"
            )
        queue = asyncio.Queue(self.queue_size)

        async def update_price(queue: asyncio.Queue):
            last_time = time.time()
            while True:
                try:
                    await queue.get()
                    while not queue.empty():
                        queue.get_nowait()
                    self.pool.update_pool_vaults_balance(self.client.commitment)
                    self.update_local_price()
                    queue.task_done()
                    # rate limiting
                    while time.time() - last_time < self.rate_limit_seconds:
                        time.sleep(self.rate_limit_sleep_seconds)
                    last_time = time.time()
                except asyncio.CancelledError:
                    break

        await asyncio.gather(
            subscribe_to_account_using_queue(
                queue,
                websocket_rpc_url,
                self.pool.amm_id,
                self.client.commitment,
            ),
            update_price(queue),
        )

    def buy(
        self,
        amount_in: float,
        slippage_allowance: float,
        payer: Keypair,
        update_vault: bool = True,
        confirm_commitment: str = "confirmed",
    ):
        # get min amount out
        _, _, expect_amount_out, _ = self.pool.get_price(
            amount_in, Direction.SPEND_QUOTE_TOKEN, Unit.BASE_TOKEN, update_vault
        )
        amount_out = expect_amount_out * (1 - slippage_allowance)
        # convert to tx format
        amount_in = self.pool.convert_quote_token_amount_to_tx_format(amount_in)
        amount_out = self.pool.convert_base_token_amount_to_tx_format(amount_out)
        # buy
        swap_transaction_builder = SwapTransactionBuilder(self.client, self.pool, payer)
        swap_transaction_builder.append_buy(amount_in, amount_out, True)
        transaction = swap_transaction_builder.compile_versioned_transaction()
        txn_signature = client_wrapper.send_transaction(self.client, transaction).value
        # wait for confirmation
        resp = client_wrapper.confirm_transaction(
            self.client,
            txn_signature,
            confirm_commitment,
            self.confirm_tx_sleep_seconds,
        )
        return resp

    def sell(
        self,
        amount_in: float,
        slippage_allowance: float,
        payer: Keypair,
        update_vault: bool = True,
        confirm_commitment: str = "confirmed",
    ):
        # get min amount out
        _, _, expect_amount_out, _ = self.pool.get_price(
            amount_in, Direction.SPEND_BASE_TOKEN, Unit.BASE_TOKEN, update_vault
        )
        amount_out = expect_amount_out * (1 - slippage_allowance)
        # convert to tx format
        amount_in = self.pool.convert_base_token_amount_to_tx_format(amount_in)
        amount_out = self.pool.convert_quote_token_amount_to_tx_format(amount_out)
        # sell
        swap_transaction_builder = SwapTransactionBuilder(self.client, self.pool, payer)
        swap_transaction_builder.append_sell(amount_in, amount_out)
        transaction = swap_transaction_builder.compile_versioned_transaction()
        txn_signature = client_wrapper.send_transaction(self.client, transaction).value
        # wait for confirmation
        resp = client_wrapper.confirm_transaction(
            self.client,
            txn_signature,
            confirm_commitment,
            self.confirm_tx_sleep_seconds,
        )
        return resp

    def get_pool_lp_supply(self, signer: Keypair, commitment="confirmed"):
        swap_transaction_builder = SwapTransactionBuilder(
            self.client, self.pool, signer
        )
        swap_transaction_builder.append_get_pool_data()
        tx = swap_transaction_builder.compile_versioned_transaction()
        simulate_result = client_wrapper.simulate_transaction(
            self.client, tx, False, commitment
        )
        simulate_logs = simulate_result.value.logs
        pool_info_raw = ""

        program_log_expected = "Program log: GetPoolData: "

        for log in simulate_logs:
            if log.startswith(program_log_expected):
                pool_info_raw = log
                break

        if pool_info_raw == "":
            raise Exception(
                "failed to get pool info since the program log cannot be found"
            )

        pool_info_raw = pool_info_raw.replace(program_log_expected, "")
        try:
            pool_info = json.loads(pool_info_raw)
        except:
            print("failed to load pool json")
            print(simulate_logs)
            raise Exception("failed to load json")

        # pool_open_time is likely to be the time when the pool was created (unixtimestamp)

        lp_supply = int(pool_info["pool_lp_supply"])
        lp_supply_unlocked = int(
            client_wrapper.get_token_supply(
                self.client, self.pool.lp_token_address
            ).value.amount
        )
        lp_locked = lp_supply - lp_supply_unlocked

        return lp_supply, lp_locked, lp_locked / lp_supply

    def get_pool_lp_locked_ratio(
        self, signer: Keypair, max_retry_count=0, commitment="confirmed"
    ):
        try:
            retry_count = -1
            while retry_count < max_retry_count:
                retry_count += 1
                try:
                    _, _, lp_locked_ratio = self.get_pool_lp_supply(signer, commitment)
                    return lp_locked_ratio
                except:
                    print("failed to get pool lp locked ratio, retrying...")
                    continue
            raise Exception("failed to get pool lp locked ratio")
        except:
            print("failed to get pool lp locked ratio")
            return -1
