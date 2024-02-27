from construct import Struct

from soldexpy.layout.utils import WideBitsBuilder, blob, preprocess_key, publicKey, u64


def accountFlagsLayout(property="accountFlags"):
    builder = WideBitsBuilder(preprocess_key(property))
    builder.add_boolean("initialized")
    builder.add_boolean("market")
    builder.add_boolean("openOrders")
    builder.add_boolean("requestQueue")
    builder.add_boolean("eventQueue")
    builder.add_boolean("bids")
    builder.add_boolean("asks")
    return preprocess_key(property) / builder.get_layout()


MARKET_STATE_LAYOUT_V2 = Struct(
    blob("none", 5),
    accountFlagsLayout("accountFlags"),
    publicKey("ownAddress"),
    u64("vaultSignerNonce"),
    publicKey("baseMint"),
    publicKey("quoteMint"),
    publicKey("baseVault"),
    u64("baseDepositsTotal"),
    u64("baseFeesAccrued"),
    publicKey("quoteVault"),
    u64("quoteDepositsTotal"),
    u64("quoteFeesAccrued"),
    u64("quoteDustThreshold"),
    publicKey("requestQueue"),
    publicKey("eventQueue"),
    publicKey("bids"),
    publicKey("asks"),
    u64("baseLotSize"),
    u64("quoteLotSize"),
    u64("feeRateBps"),
    u64("referrerRebatesAccrued"),
    blob("none", 7),
)
