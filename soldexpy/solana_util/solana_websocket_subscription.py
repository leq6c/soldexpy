import asyncio

from solana.rpc.commitment import Commitment
from solana.rpc.websocket_api import SolanaWsClientProtocol, connect
from solders.pubkey import Pubkey


async def subscribe_to_account_using_queue(
    queue: asyncio.Queue,
    websocket_rpc_url: str,
    pub_key: Pubkey,
    commitment: Commitment,
):
    websocket: SolanaWsClientProtocol
    async with connect(websocket_rpc_url) as websocket:
        await websocket.account_subscribe(pub_key, commitment, "jsonParsed")
        response = await websocket.recv()
        subscription_id = response[0].result
        while True:
            try:
                response = await websocket.recv()
                if queue.full():
                    # remove the oldest item
                    try:
                        queue.get_nowait()
                    except:
                        # there is a chance that the queue is empty
                        pass
                await queue.put(response)
            except asyncio.CancelledError:
                break
            except:
                break
        await websocket.account_unsubscribe(subscription_id)


async def subscribe_to_account_using_yield(
    websocket_rpc_url: str, pub_key: Pubkey, commitment: Commitment
):
    websocket: SolanaWsClientProtocol
    async with connect(websocket_rpc_url) as websocket:
        await websocket.account_subscribe(pub_key, commitment)
        response = await websocket.recv()
        subscription_id = response[0].result
        while True:
            try:
                response = await super(SolanaWsClientProtocol, websocket).recv()
                yield response
            except:
                break
        await websocket.account_unsubscribe(subscription_id)
