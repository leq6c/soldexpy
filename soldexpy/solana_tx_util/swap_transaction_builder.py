import solders.system_program as sp
import spl.token.instructions as spl_token
from solana.rpc.api import Client
from solana.rpc.types import TokenAccountOpts
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from solders.instruction import AccountMeta, Instruction
from solders.keypair import Keypair
from solders.message import MessageV0
from solders.pubkey import Pubkey
from solders.token.associated import get_associated_token_address
from solders.transaction import VersionedTransaction
from spl.token.client import Token
from spl.token.constants import WRAPPED_SOL_MINT
from spl.token.instructions import (
    CloseAccountParams,
    close_account,
    create_associated_token_account,
)

import soldexpy.solana.client_wrapper as client_wrapper
from soldexpy.common.reference_address import RAYDIUM_LIQUIDITY_POOL_V4
from soldexpy.layout.raydium_layout import LIQUIDITY_STATE_LAYOUT_V4
from soldexpy.raydium_pool import RaydiumPool
from soldexpy.solana_tx_util.make_swap_instruction import make_swap_instruction


class SwapTransactionBuilder:
    def __init__(
        self,
        client: Client,
        pool: RaydiumPool,
        payer: Keypair,
        unit_price: int = 25000,
        unit_budget: int = 600000,
    ):
        self.client = client
        self.pool = pool
        self.payer = payer
        # token address
        self.mint = pool.base_mint_address
        self.TOKEN_PROGRAM_ID = pool.token_program_id
        # quote address (supposed to be SOL)
        self.quoteMint = pool.quote_mint_address
        # budget
        self.unit_price = unit_price
        self.unit_budget = unit_budget
        # initialize instructions
        self.instructions = []

    def append_get_pool_data(self):
        data = LIQUIDITY_STATE_LAYOUT_V4.build(dict(instruction=12, simulate_type=0))
        accounts = [
            # AMM
            AccountMeta(self.pool.amm_id, False, False),
            # Authority
            AccountMeta(self.pool.amm_authority, False, False),
            # open orders
            AccountMeta(self.pool.amm_open_orders, False, False),
            # base vault
            AccountMeta(self.pool.pool_coin_token_account, False, False),
            # quote vault
            AccountMeta(self.pool.pool_pc_token_account, False, False),
            # LP Mint
            AccountMeta(
                self.pool.lp_token_address,
                False,
                False,
            ),
            # Serum market ID
            AccountMeta(self.pool.serum_market, False, False),
            # serum market event queue
            AccountMeta(self.pool.serum_event_queue, False, False),
        ]
        self.instructions.append(
            Instruction(
                RAYDIUM_LIQUIDITY_POOL_V4,
                data,
                accounts,
            )
        )

    def append_sell(self, amount_in: int, amount_out: int):
        # compute budget
        self.append_set_compute_budget(self.unit_price, self.unit_budget)
        # pay target token (TOKEN)
        source = get_associated_token_address(self.payer.pubkey(), self.mint)
        # get quote token (SOL)
        dest = get_associated_token_address(self.payer.pubkey(), self.quoteMint)
        # this would opens the destination token account
        self.append_create_associated_token_account(self.quoteMint)
        # swap
        self.append_swap(amount_in, source, dest, amount_out)
        # close the account
        self.append_close_account(dest)

    def append_buy(
        self,
        amount_in: int,
        amount_out: int,
        check_associated_token_account_exists=True,
    ):
        # lamports to pay for rent + transfer
        pay_for_rent = Token.get_min_balance_rent_for_exempt_for_account(self.client)
        lamports = pay_for_rent + amount_in
        # compute budget
        self.append_set_compute_budget(self.unit_price, self.unit_budget)
        # create account with seed
        source = self.append_create_account_with_seed(lamports)
        # initialize account
        self.append_initialize_account(source)
        # open destination account if not exists
        if check_associated_token_account_exists:
            self.append_if_not_exists_create_associated_token_account(self.mint)
        # swap
        dest = get_associated_token_address(self.payer.pubkey(), self.mint)
        self.append_swap(amount_in, source, dest, amount_out)
        # close the account
        self.append_close_account(source)

    def compile_versioned_transaction(self):
        recent_blockhash = client_wrapper.get_latest_blockhash(self.client)

        compiled_message = MessageV0.try_compile(
            self.payer.pubkey(),
            self.instructions,
            [],  # lookup tables
            recent_blockhash,
        )
        return VersionedTransaction(compiled_message, [self.payer])

    def append_set_compute_budget(self, unit_price: int, unit_limit: int):
        # Compute Budget: Set Compute Unit Limit
        self.instructions.append(set_compute_unit_price(unit_price))
        self.instructions.append(set_compute_unit_limit(unit_limit))

    def append_swap(
        self, amount_in: int, source: Pubkey, dest: Pubkey, amount_out: int
    ):
        self.instructions.append(
            make_swap_instruction(
                amount_in,
                source,
                dest,
                self.pool,
                self.mint,
                self.client,
                self.payer,
                amount_out,
            )
        )

    def append_close_account(self, account: Pubkey):
        self.instructions.append(
            close_account(
                CloseAccountParams(
                    account=account,
                    dest=self.payer.pubkey(),
                    owner=self.payer.pubkey(),
                    program_id=self.TOKEN_PROGRAM_ID,
                )
            )
        )

    def append_create_associated_token_account(self, mint: Pubkey):
        self.instructions.append(
            create_associated_token_account(
                self.payer.pubkey(), self.payer.pubkey(), mint
            )
        )

    def append_create_account_with_seed(self, lamports: int):
        # create account with seed
        seed = str(Keypair().pubkey())[0:32]  # use this as the seed for the new account
        source = Pubkey.create_with_seed(
            self.payer.pubkey(), seed, self.TOKEN_PROGRAM_ID
        )
        self.instructions.append(
            sp.create_account_with_seed(
                sp.CreateAccountWithSeedParams(
                    # """The account that will transfer lamports to the created account."""
                    from_pubkey=self.payer.pubkey(),
                    # """Pubkey of the created account.
                    # Must be pre-calculated with :meth:`~solders.pubkey.Pubkey.create_with_seed`."""
                    to_pubkey=source,
                    # """Base public key to use to derive the address of the created account.
                    # Must be the same as the base key used to create ``to_pubkey``."""
                    base=self.payer.pubkey(),
                    # """Seed to use to derive the address of the created account.
                    # Must be the same as the seed used to create ``to_pubkey``."""
                    seed=seed,
                    # """Amount of lamports to transfer to the created account."""
                    lamports=lamports,
                    # """Amount of space in bytes to allocate to the created account."""
                    space=165,
                    # """Pubkey of the program to assign as the owner of the created account."""
                    owner=self.TOKEN_PROGRAM_ID,
                )
            )
        )
        return source

    def append_initialize_account(self, source: Pubkey):
        # initialize account
        self.instructions.append(
            spl_token.initialize_account(
                spl_token.InitializeAccountParams(
                    account=source,
                    mint=WRAPPED_SOL_MINT,
                    owner=self.payer.pubkey(),
                    program_id=self.TOKEN_PROGRAM_ID,
                )
            )
        )

    def append_if_not_exists_create_associated_token_account(self, mint: Pubkey):
        arr = client_wrapper.get_token_accounts_by_owner(
            self.client, self.payer.pubkey(), TokenAccountOpts(mint)
        ).value

        if len(arr) > 0:
            return

        # this would opens the destination token account
        # in case the user does not have a token account for the token they want to swap
        self.instructions.append(
            create_associated_token_account(
                self.payer.pubkey(), self.payer.pubkey(), mint
            )
        )
