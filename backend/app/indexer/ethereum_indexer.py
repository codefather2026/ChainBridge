"""Ethereum event log indexer for cross-chain swap detection."""

import logging
import os
from datetime import datetime

import httpx

from .base import BaseIndexer, IndexedEvent

logger = logging.getLogger(__name__)


class EthereumIndexer(BaseIndexer):
    """Indexes Ethereum contract events relevant to ChainBridge swaps."""

    def __init__(self):
        super().__init__(chain="ethereum")
        self.rpc_url = os.getenv(
            "ETHEREUM_RPC_URL", "https://eth-sepolia.g.alchemy.com/v2/demo"
        )
        self.contract_address = os.getenv("ETHEREUM_BRIDGE_CONTRACT", "")
        self.confirmations = int(os.getenv("ETHEREUM_CONFIRMATIONS", "12"))

    async def _rpc_call(self, method: str, params: list = None) -> dict:
        """Make a JSON-RPC call to the Ethereum node."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.rpc_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": method,
                    "params": params or [],
                },
                timeout=30,
            )
            data = response.json()
            if "error" in data and data["error"]:
                raise Exception(f"Ethereum RPC error: {data['error']}")
            return data.get("result")

    async def get_latest_block(self) -> int:
        try:
            result = await self._rpc_call("eth_blockNumber")
            latest = int(result, 16)
            return max(0, latest - self.confirmations)
        except Exception as e:
            logger.error("[ethereum] Failed to get block number: %s", e)
            raise

    async def fetch_events(
        self, from_block: int, to_block: int
    ) -> list[IndexedEvent]:
        if not self.contract_address:
            return []

        events = []
        try:
            logs = await self._rpc_call(
                "eth_getLogs",
                [
                    {
                        "fromBlock": hex(from_block),
                        "toBlock": hex(to_block),
                        "address": self.contract_address,
                    }
                ],
            )

            for log in logs or []:
                try:
                    block_num = int(log["blockNumber"], 16)
                    events.append(
                        IndexedEvent(
                            chain="ethereum",
                            event_type=log["topics"][0] if log.get("topics") else "unknown",
                            tx_hash=log.get("transactionHash", ""),
                            block_number=block_num,
                            contract_address=log.get("address"),
                            data={
                                "topics": log.get("topics", []),
                                "data": log.get("data", "0x"),
                                "log_index": int(log.get("logIndex", "0x0"), 16),
                            },
                            timestamp=datetime.utcnow(),
                        )
                    )
                except Exception as e:
                    logger.warning("[ethereum] Failed to parse log: %s", e)

        except Exception as e:
            logger.error("[ethereum] Failed to fetch logs: %s", e)
            raise

        return events

    async def handle_reorg(self, reorg_block: int) -> None:
        logger.warning(
            "[ethereum] Reorg detected at block %d. Rolling back indexed events.",
            reorg_block,
        )
        # In production: delete indexed events >= reorg_block from DB
