"""Background Processor module for async cognitive tasks.

This module implements the BackgroundProcessor which handles background
cognitive tasks that run while the agent is "listening". It enables
deeper processing without blocking responses.

Phase 4 of the Cognitive Agent Engine.
"""

import asyncio
import logging
from typing import Callable, Optional

from src.cognitive.mind import InternalMind
from src.cognitive.accumulator import ThoughtAccumulator
from src.cognitive.processor import CognitiveProcessor
from src.cognitive.models import Thought

logger = logging.getLogger(__name__)


class BackgroundProcessor:
    """Handles background cognitive tasks that run while agent is listening.
    
    The BackgroundProcessor enables deeper processing without blocking
    responses. It runs a background loop that:
    - Checks streams for synthesis opportunities
    - Cleans up old/stale thoughts
    - Processes queued deep analysis tasks
    
    Attributes:
        mind: The InternalMind to process
        processor: The CognitiveProcessor for generating thoughts
        accumulator: The ThoughtAccumulator for synthesis
    """
    
    def __init__(
        self,
        mind: InternalMind,
        processor: CognitiveProcessor,
        accumulator: ThoughtAccumulator,
        cleanup_interval_seconds: float = 60.0,
        synthesis_check_interval_seconds: float = 1.0,
        max_thought_age_minutes: int = 30,
    ):
        """Initialize the background processor.
        
        Args:
            mind: The InternalMind to process
            processor: The CognitiveProcessor for generating thoughts
            accumulator: The ThoughtAccumulator for synthesis
            cleanup_interval_seconds: How often to run cleanup (default 60s)
            synthesis_check_interval_seconds: How often to check for synthesis (default 1s)
            max_thought_age_minutes: Max age for thoughts before cleanup (default 30 min)
        """
        self.mind = mind
        self.processor = processor
        self.accumulator = accumulator
        
        self.cleanup_interval = cleanup_interval_seconds
        self.synthesis_check_interval = synthesis_check_interval_seconds
        self.max_thought_age = max_thought_age_minutes
        
        self._running = False
        self._main_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        self._last_cleanup = 0.0
    
    async def start(self) -> None:
        """Start the background processing loop.
        
        Starts the main processing loop and cleanup task.
        """
        if self._running:
            logger.warning("Background processor already running")
            return
        
        self._running = True
        self._main_task = asyncio.create_task(self._process_loop())
        logger.info(f"Background processor started for agent {self.mind.agent_id}")
    
    async def stop(self) -> None:
        """Stop the background processing gracefully.
        
        Cancels the main task and waits for it to finish.
        """
        self._running = False
        
        if self._main_task:
            self._main_task.cancel()
            try:
                await self._main_task
            except asyncio.CancelledError:
                pass
            self._main_task = None
        
        logger.info(f"Background processor stopped for agent {self.mind.agent_id}")
    
    @property
    def is_running(self) -> bool:
        """Check if the background processor is running."""
        return self._running and self._main_task is not None and not self._main_task.done()
    
    async def _process_loop(self) -> None:
        """Main background processing loop.
        
        Runs continuously while _running is True, checking for
        synthesis opportunities and periodically cleaning up.
        """
        loop_count = 0
        
        while self._running:
            try:
                # Check for streams needing synthesis
                synthesized = await self.accumulator.check_streams_for_synthesis()
                if synthesized:
                    logger.debug(f"Background synthesized {len(synthesized)} streams")
                
                # Periodic cleanup
                loop_count += 1
                cleanup_interval_loops = int(self.cleanup_interval / self.synthesis_check_interval)
                if loop_count >= cleanup_interval_loops:
                    cleaned = self._cleanup_old_thoughts()
                    if cleaned > 0:
                        logger.debug(f"Background cleaned up {cleaned} old thoughts")
                    loop_count = 0
                
                # Clean up completed background tasks
                self._cleanup_completed_tasks()
                
                # Wait before next cycle
                await asyncio.sleep(self.synthesis_check_interval)
                
            except asyncio.CancelledError:
                logger.debug("Background processor cancelled")
                break
            except Exception as e:
                logger.error(f"Background processor error: {e}", exc_info=True)
                # Don't crash the loop, wait and retry
                await asyncio.sleep(5.0)
    
    def _cleanup_old_thoughts(self) -> int:
        """Remove thoughts older than the configured threshold.
        
        Returns:
            Number of thoughts removed
        """
        return self.mind.cleanup_old_thoughts(max_age_minutes=self.max_thought_age)
    
    def _cleanup_completed_tasks(self) -> None:
        """Remove completed tasks from the mind's background tasks list."""
        self.mind.background_tasks = [
            t for t in self.mind.background_tasks
            if not t.done()
        ]
    
    async def queue_deep_analysis(
        self,
        stimulus: str,
        purpose: str,
        callback: Optional[Callable[[Thought], None]] = None,
    ) -> asyncio.Task:
        """Queue a deep analysis task to run in the background.
        
        The analysis runs asynchronously and results can refine
        ongoing behavior through the callback or by being added
        to the mind.
        
        Args:
            stimulus: The stimulus to analyze
            purpose: Purpose of the analysis
            callback: Optional callback to call with the result
            
        Returns:
            The asyncio Task for the analysis
        """
        async def _run_analysis():
            try:
                result = await self.processor.process(
                    stimulus=stimulus,
                    urgency=0.1,  # Not urgent - background task
                    complexity=0.9,  # Deep analysis
                    relevance=0.7,
                    purpose=purpose,
                    context={"background": True},
                )
                
                if result.primary_thought:
                    self.mind.add_thought(result.primary_thought)
                    logger.debug(
                        f"Background analysis complete: {purpose} "
                        f"(confidence: {result.primary_thought.confidence:.2f})"
                    )
                    
                    if callback:
                        callback(result.primary_thought)
                    
                    return result.primary_thought
                
                return None
                
            except Exception as e:
                logger.error(f"Background analysis failed: {e}", exc_info=True)
                return None
        
        task = asyncio.create_task(_run_analysis())
        self.mind.background_tasks.append(task)
        logger.debug(f"Queued background analysis: {purpose}")
        
        return task
    
    async def queue_synthesis(self, topic: str) -> Optional[asyncio.Task]:
        """Queue a synthesis task for a specific topic.
        
        Args:
            topic: The topic to synthesize
            
        Returns:
            The asyncio Task, or None if no matching stream
        """
        stream = self.mind.get_stream_for_topic(topic)
        if not stream:
            return None
        
        async def _run_synthesis():
            return await self.accumulator.synthesize_stream(stream)
        
        task = asyncio.create_task(_run_synthesis())
        self.mind.background_tasks.append(task)
        logger.debug(f"Queued background synthesis for topic: {topic}")
        
        return task
    
    def get_status(self) -> dict:
        """Get the status of the background processor.
        
        Returns:
            Dictionary with processor status
        """
        active_tasks = [t for t in self.mind.background_tasks if not t.done()]
        pending_synthesis = self.accumulator.get_pending_synthesis_count()
        
        return {
            "running": self.is_running,
            "active_background_tasks": len(active_tasks),
            "pending_synthesis": pending_synthesis,
            "cleanup_interval_seconds": self.cleanup_interval,
            "synthesis_check_interval_seconds": self.synthesis_check_interval,
            "max_thought_age_minutes": self.max_thought_age,
        }


def create_background_processor(
    mind: InternalMind,
    processor: CognitiveProcessor,
) -> BackgroundProcessor:
    """Create a BackgroundProcessor with default accumulator.
    
    Convenience function for creating a fully-configured
    background processor.
    
    Args:
        mind: The InternalMind to process
        processor: The CognitiveProcessor for generating thoughts
        
    Returns:
        Configured BackgroundProcessor
    """
    accumulator = ThoughtAccumulator(mind=mind, processor=processor)
    return BackgroundProcessor(
        mind=mind,
        processor=processor,
        accumulator=accumulator,
    )

