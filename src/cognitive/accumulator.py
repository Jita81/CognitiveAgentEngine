"""Thought Accumulator module for managing thought synthesis.

This module implements the ThoughtAccumulator which enables "listening"
behavior where thoughts build up before the agent speaks. It manages
the synthesis of related thoughts into coherent contributions.

Phase 4 of the Cognitive Agent Engine.
"""

import logging
from typing import List, Optional

from src.cognitive.mind import InternalMind, ThoughtStream, StreamStatus
from src.cognitive.models import Thought, ThoughtType
from src.cognitive.processor import CognitiveProcessor

logger = logging.getLogger(__name__)


class ThoughtAccumulator:
    """Accumulates thoughts from stimuli and manages synthesis.
    
    The ThoughtAccumulator enables "listening" behavior where thoughts
    build up before the agent speaks. It:
    - Processes observations with low cognitive effort
    - Tracks when streams need synthesis
    - Synthesizes accumulated thoughts into coherent contributions
    - Prepares synthesized thoughts for sharing
    
    Attributes:
        mind: The InternalMind to accumulate thoughts into
        processor: The CognitiveProcessor for generating thoughts
    """
    
    def __init__(
        self,
        mind: InternalMind,
        processor: CognitiveProcessor,
    ):
        """Initialize the thought accumulator.
        
        Args:
            mind: The InternalMind to accumulate thoughts into
            processor: The CognitiveProcessor for generating thoughts
        """
        self.mind = mind
        self.processor = processor
    
    async def process_observation(
        self,
        stimulus: str,
        relevance: float,
        context: Optional[dict] = None,
    ) -> Optional[Thought]:
        """Process an observation with low cognitive effort.
        
        Creates small thought bubbles that accumulate in the mind.
        Used for passive listening, e.g., when others speak in a meeting.
        
        Args:
            stimulus: The observation to process
            relevance: How relevant this is to the agent (0-1)
            context: Optional additional context
            
        Returns:
            The thought created, or None if processing failed
        """
        # Use low urgency and complexity for observations
        result = await self.processor.process(
            stimulus=stimulus,
            urgency=0.2,  # Not urgent
            complexity=0.3,  # Simple observation
            relevance=relevance,
            purpose="observation",
            context=context,
        )
        
        if result.primary_thought:
            self.mind.add_thought(result.primary_thought)
            logger.debug(
                f"Processed observation, added thought to mind "
                f"(confidence: {result.primary_thought.confidence:.2f})"
            )
        
        return result.primary_thought
    
    async def synthesize_stream(
        self,
        stream: ThoughtStream,
    ) -> Optional[Thought]:
        """Synthesize accumulated thoughts in a stream into a coherent contribution.
        
        Takes all thoughts in the stream and produces a single synthesized
        thought that captures the essence of the accumulated observations.
        
        Args:
            stream: The ThoughtStream to synthesize
            
        Returns:
            The synthesized thought, or None if synthesis wasn't possible
        """
        if len(stream.thoughts) < 2:
            logger.debug(f"Stream '{stream.topic}' has too few thoughts for synthesis")
            return None
        
        # Format thoughts for synthesis prompt
        thoughts_text = "\n".join([
            f"- {t.content} (confidence: {t.confidence:.1f})"
            for t in stream.thoughts
        ])
        
        # Create synthesis prompt
        synthesis_stimulus = f"""I've been thinking about: {stream.topic}

My observations and thoughts so far:
{thoughts_text}

Synthesize these into ONE clear, coherent point that captures the key insight or conclusion."""
        
        # Get prior thoughts for context
        prior_context = {
            "prior_thoughts": thoughts_text,
            "stream_topic": stream.topic,
            "thought_count": len(stream.thoughts),
        }
        
        # Use DELIBERATE tier for synthesis (moderate complexity)
        result = await self.processor.process(
            stimulus=synthesis_stimulus,
            urgency=0.3,  # Not urgent
            complexity=0.6,  # Moderate complexity for synthesis
            relevance=0.8,  # Synthesis is always relevant to me
            purpose="synthesis",
            context=prior_context,
        )
        
        if result.primary_thought:
            synthesis = result.primary_thought
            
            # Override thought type to INSIGHT for synthesis
            synthesis.thought_type = ThoughtType.INSIGHT
            
            # Update stream
            stream.synthesized_output = synthesis
            stream.ready_to_externalize = True
            stream.status = StreamStatus.CONCLUDED
            
            # Mark source thoughts as superseded
            for thought in stream.thoughts:
                thought.still_relevant = False
                thought.superseded_by = synthesis.thought_id
            
            # Prepare to share if confidence is sufficient
            if synthesis.confidence > 0.6:
                self.mind.prepare_to_share(synthesis)
                logger.debug(
                    f"Synthesis ready to share: '{stream.topic}' "
                    f"(confidence: {synthesis.confidence:.2f})"
                )
            else:
                # Hold as insight if confidence is lower
                self.mind.hold_insight(synthesis)
                logger.debug(
                    f"Synthesis held as insight: '{stream.topic}' "
                    f"(confidence: {synthesis.confidence:.2f})"
                )
            
            # Add to mind's active thoughts
            self.mind.active_thoughts[str(synthesis.thought_id)] = synthesis
            
            return synthesis
        
        logger.warning(f"Synthesis failed for stream '{stream.topic}'")
        return None
    
    async def check_streams_for_synthesis(self) -> List[Thought]:
        """Check all streams and synthesize those that need it.
        
        Returns:
            List of synthesized thoughts
        """
        synthesized = []
        
        streams_to_process = self.mind.get_streams_needing_synthesis()
        
        for stream in streams_to_process:
            logger.debug(f"Synthesizing stream: '{stream.topic}'")
            result = await self.synthesize_stream(stream)
            
            if result:
                synthesized.append(result)
        
        if synthesized:
            logger.info(f"Synthesized {len(synthesized)} streams")
        
        return synthesized
    
    def get_pending_synthesis_count(self) -> int:
        """Get count of streams needing synthesis.
        
        Returns:
            Number of streams with NEEDS_SYNTHESIS status
        """
        return len(self.mind.get_streams_needing_synthesis())
    
    async def force_synthesis_on_topic(self, topic: str) -> Optional[Thought]:
        """Force synthesis of thoughts on a specific topic.
        
        Useful when an agent needs to contribute and has accumulated
        thoughts on the current topic.
        
        Args:
            topic: The topic to synthesize
            
        Returns:
            The synthesized thought, or None if no matching stream
        """
        stream = self.mind.get_stream_for_topic(topic)
        
        if not stream:
            logger.debug(f"No stream found for topic: '{topic}'")
            return None
        
        if stream.thought_count < 2:
            logger.debug(f"Stream '{topic}' has too few thoughts for synthesis")
            return None
        
        # Force synthesis even if not yet triggered
        return await self.synthesize_stream(stream)
    
    def get_accumulation_summary(self) -> dict:
        """Get a summary of current thought accumulation.
        
        Returns:
            Dictionary with accumulation statistics
        """
        streams = list(self.mind.streams.values())
        
        return {
            "total_streams": len(streams),
            "active_streams": len([s for s in streams if s.status == StreamStatus.ACTIVE]),
            "needs_synthesis": len([s for s in streams if s.status == StreamStatus.NEEDS_SYNTHESIS]),
            "concluded": len([s for s in streams if s.status == StreamStatus.CONCLUDED]),
            "total_accumulated_thoughts": sum(s.thought_count for s in streams),
            "ready_to_share": len(self.mind.ready_to_share),
            "held_insights": len(self.mind.held_insights),
        }

