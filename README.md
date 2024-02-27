
## Solana Raydium Experiment

This is an experimental Python toolkit to work with Raydium Liquidity Pool V4 by using only Solana RPC. You can swap tokens, get price and even get the lp locked ratio by simulating transaction. 

## Disclaimer

This is written just for research purpose and it may contain old or unsafe way. Keep this code here as a reference only. 

## Features

- `RaydiumPool`
    - `get_price`: You can get price based on the pool status. It supports simulating slippage.
        - *Only supports basic and network fee is not considered. 
- `Swap`
    - `update_local_price_on_changes`: Uses websocket to watch price changes and reflect price on object immediately.
    - `buy`: Use `SOL` to buy token. 
    - `sell`: Use token to buy `SOL`. 
    - `get_pool_lp_locked_ratio`: Retrieve locked ratio of liquidity pool. 
- `Wallet`
    - `get_balance`: Get specified token balance of the user. 
    - `get_sol_balance`: Get SOL balance of the user. 

*Only supports the pool that has `SOL` as the base or quote token. 

## Example

```
# load private key
keypair = Keypair.from_bytes(base58.b58decode(PRIVATE_KEY))
# configure rpc client
client = Client("https://api.mainnet-beta.solana.com")

# get pool
pool = RaydiumPool(client, "AVs9TA4nWDzfPJE9gGVNJMVhcQy3V9PGazuz33BfG2RA")
# initialize Swap
swap = Swap(client, pool)

# buy
swap.buy(1.0, 0.1, keypair)
```

## Development

### Testing

```
pytest
```