"""
Multi-chain indexer manager.

Orchestrates multiple chain-specific indexers, manages their lifecycle,
and provides a unified status API.
"""

import asyncio
import logging
from datetime import datetime

from .base import BaseIndexer, IndexerStatus
from .stellar_indexer import StellarIndexer
from .bitcoin_indexer import BitcoinIndexer
from .ethereum_indexer import EthereumIndexer

logger = logging.getLogger(__name__)


class IndexerManager:
    """
    Manages all chain indexers and provides unified status monitoring.

    Usage:
        manager = IndexerManager()
        await manager.start_all()  # starts indexers as background tasks
        status = manager.get_all_status()
        await manager.stop_all()
    """

    def __init__(self):
        self.indexers: dict[str, BaseIndexer] = {
            "stellar": StellarIndexer(),
            "bitcoin": BitcoinIndexer(),
            "ethereum": EthereumIndexer(),
        }
        self._tasks: dict[str, asyncio.Task] = {}

    async def start_all(
        self,
        checkpoints: dict[str, int] | None = None,
    ) -> None:
        """Start all indexers from their last checkpoints."""
        checkpoints = checkpoints or {}

        for chain, indexer in self.indexers.items():
            from_block = checkpoints.get(chain, 0)
            task = asyncio.create_task(
                indexer.start(from_block=from_block),
                name=f"indexer-{chain}",
            )
            self._tasks[chain] = task
            logger.info("Started %s indexer from block %d", chain, from_block)

    async def stop_all(self) -> None:
        """Stop all running indexers."""
        for chain, indexer in self.indexers.items():
            indexer.stop()

        for chain, task in self._tasks.items():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        self._tasks.clear()
        logger.info("All indexers stopped")

    def get_all_status(self) -> dict[str, dict]:
        """Get status of all indexers."""
        statuses = {}
        for chain, indexer in self.indexers.items():
            s = indexer.status
            statuses[chain] = {
                "chain": s.chain,
                "is_running": s.is_running,
                "last_synced_block": s.last_synced_block,
                "latest_chain_block": s.latest_chain_block,
                "blocks_behind": s.blocks_behind,
                "events_processed": s.events_processed,
                "last_error": s.last_error,
                "last_sync_at": s.last_sync_at.isoformat()
                if s.last_sync_at
                else None,
            }
        return statuses

    def get_status(self, chain: str) -> dict | None:
        """Get status of a specific chain indexer."""
        statuses = self.get_all_status()
        return statuses.get(chain)

    async def catch_up(self, chain: str, from_block: int, to_block: int) -> int:
        """
        Sync historical events for a specific chain.
        Returns the number of events processed.
        """
        indexer = self.indexers.get(chain)
        if not indexer:
            raise ValueError(f"Unknown chain: {chain}")

        events = await indexer.fetch_events(from_block, to_block)
        logger.info(
            "Historical sync for %s: %d events (blocks %d-%d)",
            chain,
            len(events),
            from_block,
            to_block,
        )
        return len(events)
