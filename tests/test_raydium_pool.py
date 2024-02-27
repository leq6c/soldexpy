from solana.rpc.api import Client
from solders.pubkey import Pubkey

from soldexpy.common.direction import Direction
from soldexpy.common.unit import Unit
from soldexpy.raydium_pool import RaydiumPool
from tests.solana.mock_client_cache import MockClientCache


def test_constructor_basics(
    client: Client, pool: RaydiumPool, mock_client_cache: MockClientCache
):
    pool = RaydiumPool(client, mock_client_cache.get_pool_address_for_tests())
    assert pool.client == client
    assert pool.amm_id == Pubkey.from_string(
        "AVs9TA4nWDzfPJE9gGVNJMVhcQy3V9PGazuz33BfG2RA"
    )
    assert pool.amm_authority == Pubkey.from_string(
        "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1"
    )
    assert pool.amm_open_orders == Pubkey.from_string(
        "6Su6Ea97dBxecd5W92KcVvv6SzCurE2BXGgFe9LNGMpE"
    )
    assert pool.amm_target_orders == Pubkey.from_string(
        "5hATcCfvhVwAjNExvrg8rRkXmYyksHhVajWLa46iRsmE"
    )
    assert pool.pool_coin_token_account == Pubkey.from_string(
        "Em6rHi68trYgBFyJ5261A2nhwuQWfLcirgzZZYoRcrkX"
    )
    assert pool.pool_pc_token_account == Pubkey.from_string(
        "3mEFzHsJyu2Cpjrz6zPmTzP7uoLFj9SbbecGVzzkL1mJ"
    )
    assert pool.market_program_id == Pubkey.from_string(
        "9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin"
    )
    assert pool.serum_market == Pubkey.from_string(
        "C6tp2RVZnxBPFbnAsfTjis8BN9tycESAT4SgDQgbbrsA"
    )
    assert pool.serum_bids == Pubkey.from_string(
        "C1nEbACFaHMUiKAUsXVYPWZsuxunJeBkqXHPFr8QgSj9"
    )
    assert pool.serum_asks == Pubkey.from_string(
        "4DNBdnTw6wmrK4NmdSTTxs1kEz47yjqLGuoqsMeHvkMF"
    )
    assert pool.serum_event_queue == Pubkey.from_string(
        "4HGvdannxvmAhszVVig9auH6HsqVH17qoavDiNcnm9nj"
    )
    assert pool.serum_coin_vault_account == Pubkey.from_string(
        "6U6U59zmFWrPSzm9sLX7kVkaK78Kz7XJYkrhP1DjF3uF"
    )
    assert pool.serum_pc_vault_account == Pubkey.from_string(
        "4YEx21yeUAZxUL9Fs7YU9Gm3u45GWoPFs8vcJiHga2eQ"
    )
    assert pool.serum_vault_signer == Pubkey.from_string(
        "7SdieGqwPJo5rMmSQM9JmntSEMoimM4dQn7NkGbNFcrd"
    )
    assert pool.base_mint_address == Pubkey.from_string(
        "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R"
    )
    assert pool.quote_mint_address == Pubkey.from_string(
        "So11111111111111111111111111111111111111112"
    )
    assert pool.base_decimals == 6
    assert pool.quote_decimals == 9
    assert pool.token_program_id == Pubkey.from_string(
        "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
    )
    assert pool.lp_token_address == Pubkey.from_string(
        "89ZKE4aoyfLBe2RuV6jM3JGNhaV18Nxh8eNtjRcndBip"
    )


def test_get_mint_address(
    client: Client, pool: RaydiumPool, mock_client_cache: MockClientCache
):
    assert pool.get_mint_address() == Pubkey.from_string(
        "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R"
    )


def test_update_pool_vaults_balance(
    client: Client, pool: RaydiumPool, mock_client_cache: MockClientCache
):
    pool.update_pool_vaults_balance()
    assert pool.base_vault_balance == 4757782.728947
    assert pool.quote_vault_balance == 41868.877422974


def test_get_price(
    client: Client, pool: RaydiumPool, mock_client_cache: MockClientCache
):
    assert pool.get_price(1, Direction.SPEND_BASE_TOKEN, Unit.BASE_TOKEN) == (
        113.63533060727889,
        113.6353067430545,
        0.008778079798503313,
        0.9975,
    )
    assert pool.get_price(1, Direction.SPEND_BASE_TOKEN, Unit.QUOTE_TOKEN) == (
        0.008800079998499561,
        0.008800081846579088,
        0.008778079798503313,
        0.9975,
    )
    assert pool.get_price(1, Direction.SPEND_QUOTE_TOKEN, Unit.BASE_TOKEN) == (
        113.63259951740427,
        113.6353067430545,
        113.34851801861078,
        0.9975,
    )
    assert pool.get_price(1, Direction.SPEND_QUOTE_TOKEN, Unit.QUOTE_TOKEN) == (
        0.00880029150302803,
        0.008800081846579088,
        113.34851801861078,
        0.9975,
    )

    assert pool.get_price(2.5, Direction.SPEND_BASE_TOKEN, Unit.BASE_TOKEN) == (
        113.63536626755993,
        113.6353067430545,
        0.0219451926095644,
        2.49375,
    )
    assert pool.get_price(2.5, Direction.SPEND_BASE_TOKEN, Unit.QUOTE_TOKEN) == (
        0.008800077236918056,
        0.008800081846579088,
        0.0219451926095644,
        2.49375,
    )
    assert pool.get_price(2.5, Direction.SPEND_QUOTE_TOKEN, Unit.BASE_TOKEN) == (
        113.62853891979483,
        113.6353067430545,
        283.36116893123835,
        2.49375,
    )
    assert pool.get_price(2.5, Direction.SPEND_QUOTE_TOKEN, Unit.QUOTE_TOKEN) == (
        0.008800605987777895,
        0.008800081846579088,
        283.36116893123835,
        2.49375,
    )


def test_convert_base_token_amount_to_tx_format(
    client: Client, pool: RaydiumPool, mock_client_cache: MockClientCache
):
    assert pool.convert_base_token_amount_to_tx_format(1) == 1000000
    assert pool.convert_base_token_amount_to_tx_format(2.5) == 2500000
    pool.base_decimals = 5
    assert pool.convert_base_token_amount_to_tx_format(1) == 100000
    assert pool.convert_base_token_amount_to_tx_format(2.5) == 250000


def test_convert_quote_token_amount_to_tx_format(
    client: Client, pool: RaydiumPool, mock_client_cache: MockClientCache
):
    assert pool.convert_quote_token_amount_to_tx_format(1) == 1000000000
    assert pool.convert_quote_token_amount_to_tx_format(2.5) == 2500000000
    pool.quote_decimals = 5
    assert pool.convert_quote_token_amount_to_tx_format(1) == 100000
    assert pool.convert_quote_token_amount_to_tx_format(2.5) == 250000


def test_convert_base_token_amount_from_tx_format(
    client: Client, pool: RaydiumPool, mock_client_cache: MockClientCache
):
    assert pool.convert_base_token_amount_from_tx_format(1000000) == 1
    assert pool.convert_base_token_amount_from_tx_format(2500000) == 2.5
    pool.base_decimals = 5
    assert pool.convert_base_token_amount_from_tx_format(100000) == 1
    assert pool.convert_base_token_amount_from_tx_format(250000) == 2.5


def test_convert_quote_token_amount_from_tx_format(
    client: Client, pool: RaydiumPool, mock_client_cache: MockClientCache
):
    assert pool.convert_quote_token_amount_from_tx_format(1000000000) == 1
    assert pool.convert_quote_token_amount_from_tx_format(2500000000) == 2.5
    pool.quote_decimals = 5
    assert pool.convert_quote_token_amount_from_tx_format(100000) == 1
    assert pool.convert_quote_token_amount_from_tx_format(250000) == 2.5


def test_constructor_market_info_parse(
    client: Client, pool: RaydiumPool, mock_client_cache: MockClientCache
):
    assert pool.market_info.account_flags.initialized == True
    assert pool.market_info.account_flags.market == True
    assert pool.market_info.account_flags.open_orders == False
    assert pool.market_info.account_flags.request_queue == False
    assert pool.market_info.account_flags.event_queue == False
    assert pool.market_info.account_flags.bids == False
    assert pool.market_info.account_flags.asks == False
    assert (
        pool.market_info.own_address
        == b"\xa4\xf3\n\xf8\xac\x99aUV\xb1R\\\x94\xf8\x82\x856\xa0A\\\x94\x8e5\x94\xbeU\x88\x92R\x13\xba\xd1"
    )
    assert pool.market_info.vault_signer_nonce == 1
    assert (
        pool.market_info.base_mint
        == b"7\x99\x8c\xcb\xf2\xd0E\x8ba\\\xbc\xc6\xb1\xa3g\xc4t\x9e\x9f\xefs\x06b.\x1b\x1bX\x91\x01 \xbc\x9a"
    )
    assert (
        pool.market_info.quote_mint
        == b"\x06\x9b\x88W\xfe\xab\x81\x84\xfbh\x7fcF\x18\xc05\xda\xc49\xdc\x1a\xeb;U\x98\xa0\xf0\x00\x00\x00\x00\x01"
    )
    assert (
        pool.market_info.base_vault
        == b"Q;L9\x91\xd1|I\x97\x0fSu\xcdW\x99\xa6\x9e\xbc\x8d\x9d\x99\xe6\x83\xf4\x04v\xaa<\xb6'\x19n"
    )
    assert pool.market_info.base_deposits_total == 69593500000
    assert pool.market_info.base_fees_accrued == 0
    assert (
        pool.market_info.quote_vault
        == b"4\x93\xd6j\xda\x91\x12\x03\x0e\x98\xbb\xc2\x86a\xb1\x92\xb7f(Z!\xd9\xf0qY\x8e@x\x16\x15\xaf\xf5"
    )
    assert pool.market_info.quote_deposits_total == 4135892464680
    assert pool.market_info.quote_fees_accrued == 8679765412
    assert pool.market_info.quote_dust_threshold == 100
    assert (
        pool.market_info.request_queue
        == b"A\xd1\xad\xda\x1c8O\x1a\x9c\x1fpe\xf6\xbc\x14Wj\xe2\x9dMs\x16\xdcV\x03wJ:W\xfa\x11\xaf"
    )
    assert (
        pool.market_info.event_queue
        == b"0\xbe\\\x1c\x16SB\xa8\xe8)\x87.\x15\xd0n\xd9\xd2\xf3\x01\xed\xf7\xed\xb7G\x01\xc1uV\xbc\xd9\x86\xcc"
    )
    assert (
        pool.market_info.bids
        == b"\xa3\xa3\xb3\xe8\x89X[h\xaep\xe1\xbc7h\xd5tM\x8fd7\xb5_\x03\x95,\x84\x92\x92U>\xf58"
    )
    assert (
        pool.market_info.asks
        == b"/\xbd\xfb\x8a\x1e\xe2\xae{\xa2\x8b\x936e\xfb\xe7\x8e\xe6\xad\xe8\xd4\x99\xe1:q\x185a\x1aY\xa9S\n"
    )
    assert pool.market_info.base_lot_size == 100000
    assert pool.market_info.quote_lot_size == 100000
    assert pool.market_info.fee_rate_bps == 0
    assert pool.market_info.referrer_rebates_accrued == 320936676783


def test_constructor_pool_info_parse(
    client: Client, pool: RaydiumPool, mock_client_cache: MockClientCache
):
    # Check if pool_info is properly parsed
    assert pool.pool_info.status == 6
    assert pool.pool_info.nonce == 254
    assert pool.pool_info.max_order == 7
    assert pool.pool_info.depth == 3
    assert pool.pool_info.base_decimal == 6
    assert pool.pool_info.quote_decimal == 9
    assert pool.pool_info.state == 2
    assert pool.pool_info.reset_flag == 0
    assert pool.pool_info.min_size == 100000000
    assert pool.pool_info.vol_max_cut_ratio == 500
    assert pool.pool_info.amount_wave_ratio == 0
    assert pool.pool_info.base_lot_size == 100000
    assert pool.pool_info.quote_lot_size == 1000000
    assert pool.pool_info.min_price_multiplier == 1
    assert pool.pool_info.max_price_multiplier == 1000000000
    assert pool.pool_info.system_decimal_value == 1000000000
    assert pool.pool_info.min_separate_numerator == 5
    assert pool.pool_info.min_separate_denominator == 10000
    assert pool.pool_info.trade_fee_numerator == 25
    assert pool.pool_info.trade_fee_denominator == 10000
    assert pool.pool_info.pnl_numerator == 12
    assert pool.pool_info.pnl_denominator == 100
    assert pool.pool_info.swap_fee_numerator == 25
    assert pool.pool_info.swap_fee_denominator == 10000
    assert pool.pool_info.base_need_take_pnl == 628249
    assert pool.pool_info.quote_need_take_pnl == 5531365
    assert pool.pool_info.quote_total_pnl == 59813427324701
    assert pool.pool_info.base_total_pnl == 2165806762233
    assert pool.pool_info.punish_pc_amount == 0
    assert pool.pool_info.punish_coin_amount == 0
    assert pool.pool_info.swap_base_in_amount == 841604976034564
    assert pool.pool_info.swap_quote_out_amount == 23163014813365249
    assert pool.pool_info.swap_base2_quote_fee == 57163480188951
    assert pool.pool_info.swap_quote_in_amount == 22850931937005121
    assert pool.pool_info.swap_base_out_amount == 830174109992596
    assert pool.pool_info.swap_quote2_base_fee == 2104716679842
    assert (
        pool.pool_info.base_vault
        == b"\xcct\x19\x9bE\xba\xcf\x98-6^F\xbf\xefj\x11\xa1z\x9d\xc7S\x1e\x17*g\xe2J\xe6oq\xad8"
    )
    assert (
        pool.pool_info.quote_vault
        == b")\x0b\xeb\xb8}s\x9e\x02\x89\x13{:\xc1\x1f\xc1\xd79\x00\xf0\xa2\x9a\xc5\xb6f`[e\x1d\x1f?\xa8\x91"
    )
    assert (
        pool.pool_info.base_mint
        == b"7\x99\x8c\xcb\xf2\xd0E\x8ba\\\xbc\xc6\xb1\xa3g\xc4t\x9e\x9f\xefs\x06b.\x1b\x1bX\x91\x01 \xbc\x9a"
    )
    assert (
        pool.pool_info.quote_mint
        == b"\x06\x9b\x88W\xfe\xab\x81\x84\xfbh\x7fcF\x18\xc05\xda\xc49\xdc\x1a\xeb;U\x98\xa0\xf0\x00\x00\x00\x00\x01"
    )
    assert (
        pool.pool_info.lp_mint
        == b"j2\xfe&9,\xa6\x81,\xeaN\xe5\xbb\xc4d\xb6)An\xef\xa1\x90P\xef\xf9\t\x0c\xfbM\xc7\x8b1"
    )
    assert (
        pool.pool_info.open_orders
        == b"P\xec\xda}\xce\x046\xfe\xa5\xb6\xec\x7f\xe8\x9au\xabi\x85\xba\xa3\xce\xc9\x9fF\n\x11\x8a\xef\x15%m\x8b"
    )
    assert (
        pool.pool_info.market_id
        == b"\xa4\xf3\n\xf8\xac\x99aUV\xb1R\\\x94\xf8\x82\x856\xa0A\\\x94\x8e5\x94\xbeU\x88\x92R\x13\xba\xd1"
    )
    assert (
        pool.pool_info.market_program_id
        == b"\x85\x0f-n\x02\xa4z\xf8$\xd0\x9a\xb6\x9d\xc4-p\xcb(\xcb\xfa$\x9f\xb7\xeeW\xb9\xd2V\xc1'b\xef"
    )
    assert (
        pool.pool_info.target_orders
        == b"E\xb8\xac\xd3V\xd7\x1d\xb0R\xd1\x02\xc6\xcd\xcfK\x98\xc9#V\xa9\xcd\x9d\x8e\x90`\xeb\xe4\xf9\xcc\xf9\xd4\xbd"
    )
    assert (
        pool.pool_info.withdraw_queue
        == b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    )
    assert (
        pool.pool_info.lp_vault
        == b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    )
    assert (
        pool.pool_info.owner
        == b"\xe5\xb6+e\xcb;\xbd\xa6\xf5h\x88\xe6o\xee\x8ed\xdcU`\x19\x9c\x0f\x88\xb1\x1f\xe2s\xbd\x05\x9e\x8a\xa1"
    )
    assert pool.pool_info.lp_reserve == 1119806588206
