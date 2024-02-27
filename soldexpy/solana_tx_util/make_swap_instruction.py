from solana.rpc.api import Client
from solana.transaction import AccountMeta
from solders.instruction import Instruction
from solders.keypair import Keypair
from solders.pubkey import Pubkey

from soldexpy.common.reference_address import RAYDIUM_LIQUIDITY_POOL_V4
from soldexpy.layout.raydium_layout import ROUTE_DATA_LAYOUT
from soldexpy.raydium_pool import RaydiumPool


def make_swap_instruction(
    amount_in: int,
    token_account_in: Pubkey,
    token_account_out: Pubkey,
    pool: RaydiumPool,
    mint: Pubkey,
    ctx: Client,
    owner: Keypair,
    amount_out: int,
) -> Instruction:
    # TODO: check if this is the correct way to get the token program id
    accountProgramId = ctx.get_account_info_json_parsed(mint)
    TOKEN_PROGRAM_ID = accountProgramId.value.owner

    keys = [
        # Token Program
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        # AmmId
        AccountMeta(pubkey=pool.amm_id, is_signer=False, is_writable=True),
        # AmmAuthority
        AccountMeta(pubkey=pool.amm_authority, is_signer=False, is_writable=False),
        # AmmOpenOrders
        AccountMeta(pubkey=pool.amm_open_orders, is_signer=False, is_writable=True),
        # AmmTargetOrders
        AccountMeta(pubkey=pool.amm_target_orders, is_signer=False, is_writable=True),
        # PoolCoinTokenAccount
        AccountMeta(
            pubkey=pool.pool_coin_token_account, is_signer=False, is_writable=True
        ),
        # PoolPcTokenAccount
        AccountMeta(
            pubkey=pool.pool_pc_token_account, is_signer=False, is_writable=True
        ),
        # SerumProgramId
        AccountMeta(pubkey=pool.market_program_id, is_signer=False, is_writable=False),
        # SerumMakret
        AccountMeta(pubkey=pool.serum_market, is_signer=False, is_writable=True),
        # SerumBids
        AccountMeta(pubkey=pool.serum_bids, is_signer=False, is_writable=True),
        # SerumAsks
        AccountMeta(pubkey=pool.serum_asks, is_signer=False, is_writable=True),
        # SerumEventQueue
        AccountMeta(pubkey=pool.serum_event_queue, is_signer=False, is_writable=True),
        # SerumCoinVaultAccount
        AccountMeta(
            pubkey=pool.serum_coin_vault_account, is_signer=False, is_writable=True
        ),
        # SerumPcVaultAccount
        AccountMeta(
            pubkey=pool.serum_pc_vault_account, is_signer=False, is_writable=True
        ),
        # SerumVaultSigner
        AccountMeta(pubkey=pool.serum_vault_signer, is_signer=False, is_writable=False),
        # UserSourceTokenAccount
        AccountMeta(pubkey=token_account_in, is_signer=False, is_writable=True),
        # UserDestTokenAccount
        AccountMeta(pubkey=token_account_out, is_signer=False, is_writable=True),
        # UserOwner
        AccountMeta(pubkey=owner.pubkey(), is_signer=True, is_writable=False),
    ]

    data = ROUTE_DATA_LAYOUT.build(
        dict(instruction=9, amount_in=int(amount_in), amount_out=int(amount_out))
    )
    return Instruction(RAYDIUM_LIQUIDITY_POOL_V4, data, keys)
