# Cognitive Agent Engine - Requirements Document

**Version:** 1.0  
**Date:** December 2, 2024  
**Status:** Draft for Review  
**Project Code:** CAE-MVP-001

---

## Document Control

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Product Owner | [To be assigned] | | |
| Technical Lead | [To be assigned] | | |
| Architect | [To be assigned] | | |

### Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2024-12-02 | Initial | Complete MVP requirements specification |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Project Overview](#2-project-overview)
3. [System Architecture](#3-system-architecture)
4. [Cognitive Architecture](#4-cognitive-architecture)
5. [Social Intelligence Model](#5-social-intelligence-model)
6. [Agent Profile Model](#6-agent-profile-model)
7. [Memory Architecture](#7-memory-architecture)
8. [Functional Requirements](#8-functional-requirements)
9. [Non-Functional Requirements](#9-non-functional-requirements)
10. [Data Models](#10-data-models)
11. [API Specifications](#11-api-specifications)
12. [Model Serving Infrastructure](#12-model-serving-infrastructure)
13. [Performance Requirements](#13-performance-requirements)
14. [Security Requirements](#14-security-requirements)
15. [Technology Stack](#15-technology-stack)
16. [Testing Requirements](#16-testing-requirements)
17. [Deployment Requirements](#17-deployment-requirements)
18. [Monitoring & Observability](#18-monitoring--observability)
19. [Budget & Cost Management](#19-budget--cost-management)
20. [Acceptance Criteria](#20-acceptance-criteria)
21. [Risks & Dependencies](#21-risks--dependencies)
22. [Appendices](#22-appendices)

---

## 1. Executive Summary

### 1.1 Project Vision

Build a cognitive agent engine that creates AI team members with human-like social intelligence. Each agent possesses skills, personality, and emotional intelligence that enables them to:

- **Think independently** — Process information and form thoughts without necessarily speaking
- **Know when to speak** — Understand context, read the room, and contribute when valuable
- **Know when to listen** — Recognize when others are more qualified or when silence is appropriate
- **Learn from experience** — Accumulate patterns of success and failure from projects
- **Scale naturally** — Operate effectively whether alone, in small teams, or in groups of thousands

### 1.2 Business Objectives

| Priority | Objective |
|----------|-----------|
| Primary | Create cognitively realistic AI agents for collaborative work |
| Secondary | Demonstrate cost-effective multi-agent operation on self-hosted infrastructure |
| Tertiary | Establish foundation for AI-augmented development teams |

### 1.3 Core Value Proposition

Instead of orchestrating agents externally, this engine creates agents with **intrinsic social intelligence**:

- **Emergent coordination** through individual emotional intelligence, not top-down control
- **Layered cognition** matching human thinking patterns (fast reflexes to deep analysis)
- **Continuous thought** that exists whether externalized or not
- **Adaptive behavior** based on group size, role, and social context
- **Cost efficiency** through tiered model selection and self-hosted infrastructure

### 1.4 Success Criteria Summary

| Metric | Target | Measurement |
|--------|--------|-------------|
| Infrastructure Cost | ≤$15/hour | Cloud billing |
| Concurrent Agents | 20 in active collaboration | Load testing |
| Reflex Response Time | <200ms | p95 latency |
| Deliberate Response Time | <2s | p95 latency |
| Social Appropriateness | >85% | Human evaluation |
| Thought-to-Speech Quality | >90% | Human evaluation |
| Pattern Learning Accuracy | >75% | Retrospective analysis |

### 1.5 Primary Use Case

**AI Development Team**: A team of 20 AI consultants with distinct skills, personalities, and experience. They collaborate on software projects, participating in meetings, making decisions, and learning from outcomes. Each agent knows:

- Their expertise and limitations
- When to contribute vs. defer
- How to build on others' ideas
- How to facilitate vs. participate
- What patterns have worked before

### 1.6 Out of Scope (Post-MVP)

| Feature | Reason |
|---------|--------|
| ❌ Voice synthesis/recognition | Complexity, focus on text first |
| ❌ Visual perception | Separate capability |
| ❌ Real-time code execution | Security/complexity |
| ❌ External tool integration | Phase 2 feature |
| ❌ Multi-language support | English first |
| ❌ Fine-tuned models | Use base models initially |
| ❌ Agent self-modification | Safety considerations |

---

## 2. Project Overview

### 2.1 Problem Statement

Current multi-agent AI systems suffer from:

1. **External Orchestration Dependency** — Agents cannot decide when to speak; a controller must manage turns
2. **Binary Speaking Model** — Agents either respond or don't; no internal thought process
3. **Uniform Processing** — All requests processed the same way regardless of urgency
4. **No Social Awareness** — Agents don't consider who else is present or what others know
5. **Expensive Inference** — Commercial API costs prohibit realistic team simulations
6. **No Learning** — Each interaction is independent; no accumulated wisdom

### 2.2 Proposed Solution

A **cognitive agent engine** where each agent has:

1. **Layered Cognition** — Multiple tiers of thinking from reflexive to analytical
2. **Internal Mind** — Thoughts exist and evolve whether spoken or not
3. **Social Intelligence** — Awareness of context, role, and others' expertise
4. **Selective Externalization** — Intelligent decisions about when to share thoughts
5. **Tiered Model Architecture** — Right-sized models for each cognitive need
6. **Pattern Memory** — Accumulated learning from project outcomes

### 2.3 Key Design Principles

| Principle | Description |
|-----------|-------------|
| **Cognition First** | Thinking happens continuously; speaking is optional |
| **Social Intelligence** | Agents read the room, not receive instructions |
| **Right-Sized Processing** | Match model size/cost to cognitive need |
| **Emergent Coordination** | Good group behavior emerges from individual intelligence |
| **Graceful Scaling** | Same architecture works for 1 or 1000 agents |
| **Budget Conscious** | Stay within $15/hour through smart resource allocation |

### 2.4 Scaling Scenarios

The same agent architecture must work across:

| Scenario | Group Size | Agent Behavior |
|----------|------------|----------------|
| Solo Work | 1 | Full engagement, comprehensive thinking |
| Pair | 2 | Active collaboration, frequent exchange |
| Small Team | 3-6 | Role-based contribution, focused expertise |
| Meeting | 7-20 | Selective contribution, active listening |
| Large Group | 21-100 | Highly selective, speak only when critical |
| Army Scale | 100+ | Follow structure, respond to direct address only |

---

## 3. System Architecture

### 3.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                    │
│         (Meeting Interface / Project Dashboard / Chat Interface)            │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │ HTTP/WebSocket
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           API GATEWAY (FastAPI)                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │   Agent     │  │   Meeting   │  │   Project   │  │   Admin     │       │
│  │   Routes    │  │   Routes    │  │   Routes    │  │   Routes    │       │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘       │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │
┌─────────────────────────────────────┼───────────────────────────────────────┐
│                          AGENT RUNTIME LAYER                                 │
│                                     │                                        │
│  ┌──────────────────────────────────┴──────────────────────────────────┐   │
│  │                        AGENT MANAGER                                 │   │
│  │         (Lifecycle, Loading, Actor Supervision)                      │   │
│  └──────────────────────────────────┬──────────────────────────────────┘   │
│                                     │                                        │
│    ┌─────────────┐  ┌─────────────┐ │ ┌─────────────┐  ┌─────────────┐     │
│    │   Agent 1   │  │   Agent 2   │ │ │   Agent N   │  │   Agent 20  │     │
│    │  (Actor)    │  │  (Actor)    │...│  (Actor)    │  │  (Actor)    │     │
│    │             │  │             │ │ │             │  │             │     │
│    │ ┌─────────┐ │  │ ┌─────────┐ │ │ │ ┌─────────┐ │  │ ┌─────────┐ │     │
│    │ │Cognitive│ │  │ │Cognitive│ │ │ │ │Cognitive│ │  │ │Cognitive│ │     │
│    │ │Processor│ │  │ │Processor│ │ │ │ │Processor│ │  │ │Processor│ │     │
│    │ └─────────┘ │  │ └─────────┘ │ │ │ └─────────┘ │  │ └─────────┘ │     │
│    │ ┌─────────┐ │  │ ┌─────────┐ │ │ │ ┌─────────┐ │  │ ┌─────────┐ │     │
│    │ │Internal │ │  │ │Internal │ │ │ │ │Internal │ │  │ │Internal │ │     │
│    │ │  Mind   │ │  │ │  Mind   │ │ │ │ │  Mind   │ │  │ │  Mind   │ │     │
│    │ └─────────┘ │  │ └─────────┘ │ │ │ └─────────┘ │  │ └─────────┘ │     │
│    │ ┌─────────┐ │  │ ┌─────────┐ │ │ │ ┌─────────┐ │  │ ┌─────────┐ │     │
│    │ │ Social  │ │  │ │ Social  │ │ │ │ │ Social  │ │  │ │ Social  │ │     │
│    │ │  Intel  │ │  │ │  Intel  │ │ │ │ │  Intel  │ │  │ │  Intel  │ │     │
│    │ └─────────┘ │  │ └─────────┘ │ │ │ └─────────┘ │  │ └─────────┘ │     │
│    └─────────────┘  └─────────────┘ │ └─────────────┘  └─────────────┘     │
│                                     │                                        │
└─────────────────────────────────────┼───────────────────────────────────────┘
                                      │
┌─────────────────────────────────────┼───────────────────────────────────────┐
│                       COGNITIVE SERVICES LAYER                               │
│                                     │                                        │
│  ┌──────────────────────────────────┴──────────────────────────────────┐   │
│  │                      MODEL ROUTER                                    │   │
│  │      (Tier Selection, Load Balancing, Fallback, Budget)             │   │
│  └──────────────────────────────────┬──────────────────────────────────┘   │
│                                     │                                        │
│         ┌───────────────────────────┼───────────────────────────┐           │
│         ▼                           ▼                           ▼           │
│  ┌─────────────┐            ┌─────────────┐            ┌─────────────┐     │
│  │ SMALL TIER  │            │MEDIUM TIER  │            │ LARGE TIER  │     │
│  │ Qwen2.5-3B  │            │ Qwen2.5-7B  │            │Qwen2.5-14B  │     │
│  │   (vLLM)    │            │   (vLLM)    │            │   (vLLM)    │     │
│  │             │            │             │            │             │     │
│  │ REFLEX      │            │ REACTIVE    │            │ DELIBERATE  │     │
│  │ <200ms      │            │ <500ms      │            │ <2000ms     │     │
│  └─────────────┘            └─────────────┘            └─────────────┘     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
┌─────────────────────────────────────┼───────────────────────────────────────┐
│                         PERSISTENCE LAYER                                    │
│                                     │                                        │
│  ┌─────────────┐  ┌─────────────┐  │  ┌─────────────┐  ┌─────────────┐     │
│  │ PostgreSQL  │  │    Redis    │  │  │   Pattern   │  │   Metrics   │     │
│  │  (State)    │  │   (Cache)   │  │  │   Store     │  │   (Prom)    │     │
│  └─────────────┘  └─────────────┘     └─────────────┘  └─────────────┘     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Component Overview

#### 3.2.1 API Gateway

- **Technology**: FastAPI (Python)
- **Responsibilities**: HTTP/WebSocket handling, authentication, request routing
- **Key Endpoints**: Agent management, stimulus delivery, meeting coordination, project management

#### 3.2.2 Agent Manager

- **Technology**: Python with asyncio
- **Responsibilities**: Agent lifecycle, actor supervision, lazy loading, LRU eviction
- **Capacity**: 20 concurrent agents (MVP target)

#### 3.2.3 Agent Actor

- **Technology**: Python actor pattern
- **Responsibilities**: Encapsulates single agent's complete state and processing
- **Components**: Cognitive Processor, Internal Mind, Social Intelligence

#### 3.2.4 Model Router

- **Technology**: Python with async HTTP
- **Responsibilities**: Route cognitive requests to appropriate model tier, manage load balancing, enforce budget
- **Latency Target**: <10ms routing overhead

#### 3.2.5 Model Serving (vLLM)

- **Technology**: vLLM with OpenAI-compatible API
- **Models**: Qwen2.5 family (3B, 7B, 14B)
- **Features**: Continuous batching, prefix caching, quantization support

### 3.3 Data Flow: Stimulus to Possible Response

```
STIMULUS ARRIVES (e.g., someone speaks in meeting)
        │
        ▼
┌───────────────────────────────────────────────────────────────────┐
│                    1. STIMULUS RECEPTION                          │
│   - Received by Agent Actor                                       │
│   - Timestamped and categorized                                   │
│   - Social context attached                                       │
└───────────────────────────────────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────────────────────────────────┐
│                 2. COGNITIVE DISPATCH                             │
│   - Assess urgency (0-1)                                         │
│   - Assess complexity (0-1)                                      │
│   - Assess my relevance (0-1)                                    │
│   - Plan cognitive strategy (which tiers, parallel/sequential)    │
└───────────────────────────────────────────────────────────────────┘
        │
        ├──────────────────────────┬─────────────────────────┐
        ▼                          ▼                         ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ 3a. REFLEX       │    │ 3b. REACTIVE     │    │ 3c. DELIBERATE   │
│ (if urgent)      │    │ (if relevant)    │    │ (if complex)     │
│                  │    │                  │    │                  │
│ Model: 3B        │    │ Model: 7B        │    │ Model: 14B       │
│ Tokens: ≤150     │    │ Tokens: ≤400     │    │ Tokens: ≤1200    │
│ Latency: <200ms  │    │ Latency: <500ms  │    │ Latency: <2000ms │
└────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘
         │                       │                        │
         ▼                       ▼                        ▼
┌───────────────────────────────────────────────────────────────────┐
│                    4. THOUGHT CREATION                            │
│   - Each tier produces Thought objects                           │
│   - Thoughts added to Internal Mind                              │
│   - Later thoughts can refine earlier ones                       │
└───────────────────────────────────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────────────────────────────────┐
│               5. THOUGHT ACCUMULATION & SYNTHESIS                 │
│   - Related thoughts grouped into streams                        │
│   - Streams synthesized when ready                               │
│   - Synthesis may produce "ready to share" thought               │
└───────────────────────────────────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────────────────────────────────┐
│              6. EXTERNALIZATION DECISION                          │
│   (Social Intelligence Module)                                    │
│                                                                   │
│   Should I speak?                                                 │
│   - Am I directly addressed?              → MUST_RESPOND          │
│   - Is my expertise specifically needed?  → SHOULD_CONTRIBUTE     │
│   - Do I have unique value to add?        → MAY_CONTRIBUTE        │
│   - Should I learn from this?             → ACTIVE_LISTEN         │
│   - Is this background noise?             → PASSIVE_AWARENESS     │
│                                                                   │
│   Additional factors:                                             │
│   - Have I already said enough?                                   │
│   - Is there conversational space?                                │
│   - Is someone more qualified present?                            │
│   - What does my role suggest?                                    │
└───────────────────────────────────────────────────────────────────┘
        │
        ├── SPEAK ──────────────────────────────────────────┐
        │                                                    ▼
        │                                    ┌─────────────────────────┐
        │                                    │ 7a. EXTERNALIZE         │
        │                                    │ - Get best ready thought│
        │                                    │ - Format as speech      │
        │                                    │ - Deliver response      │
        │                                    │ - Mark thought spoken   │
        │                                    └─────────────────────────┘
        │
        └── HOLD ───────────────────────────────────────────┐
                                                            ▼
                                            ┌─────────────────────────┐
                                            │ 7b. INTERNAL UPDATE     │
                                            │ - Store insight         │
                                            │ - Update working memory │
                                            │ - Continue accumulating │
                                            │ - Maybe share later     │
                                            └─────────────────────────┘
```

---

## 4. Cognitive Architecture

### 4.1 Overview

The cognitive architecture models human-like thinking with multiple parallel processing tiers. Unlike request-response systems, agents **think continuously**—thoughts exist whether spoken or not.

### 4.2 Cognitive Tiers

| Tier | Name | Max Tokens | Target Latency | Model | Use Case |
|------|------|------------|----------------|-------|----------|
| 0 | REFLEX | 150 | <200ms | Qwen2.5-3B | Immediate reactions, survival responses |
| 1 | REACTIVE | 400 | <500ms | Qwen2.5-7B | Quick assessments, tactical decisions |
| 2 | DELIBERATE | 1,200 | <2,000ms | Qwen2.5-14B | Considered responses, synthesis |
| 3 | ANALYTICAL | 2,500 | <5,000ms | Qwen2.5-14B | Deep analysis, pattern matching |
| 4 | COMPREHENSIVE | 4,000 | <10,000ms | Qwen2.5-14B | Full exploration, complex reasoning |

### 4.3 Tier Characteristics

#### 4.3.1 REFLEX Tier

```yaml
Purpose: Immediate, instinctive responses
When Used:
  - Direct threats requiring instant action
  - Simple acknowledgments
  - Pattern-matched familiar situations
  
Memory Access: Cached only (no retrieval)
Context Depth: Minimal (identity + immediate stimulus)
Can Interrupt: No (too fast)
Runs Parallel: Yes

Example Prompt:
  "You are {name}, a {role}. Core trait: {primary_trait}
   STIMULUS: {content}
   IMMEDIATE REACTION (one thought or action):"

Example Use:
  - "DUCK!" when sword swings
  - "Interesting..." when noting a point
  - Quick nod of acknowledgment
```

#### 4.3.2 REACTIVE Tier

```yaml
Purpose: Quick but slightly considered responses
When Used:
  - Tactical assessments
  - Immediate concerns
  - Quick questions or clarifications
  
Memory Access: Recent only (working memory + last hour)
Context Depth: Shallow (identity + recent context + stimulus)
Can Interrupt: Yes
Runs Parallel: Yes (multiple reactive thoughts can process simultaneously)

Example Prompt:
  "You are {name}, a {role}.
   Key skills: {top_3_skills}
   Current state: {brief_state}
   
   SITUATION: {content}
   
   Your quick assessment (2-3 sentences):"

Example Use:
  - "That could affect our timeline"
  - "Have we considered the security implications?"
  - Rapid tactical evaluation
```

#### 4.3.3 DELIBERATE Tier

```yaml
Purpose: Considered, thoughtful responses
When Used:
  - Forming opinions
  - Synthesizing multiple thoughts
  - Preparing contributions to share
  
Memory Access: Indexed (query short-term memory by topic)
Context Depth: Standard (full identity + relevant memory + full stimulus)
Can Interrupt: Yes
Runs Parallel: No (sequential to manage cost)

Example Prompt:
  "IDENTITY:
   You are {name}, a {role}. {backstory_summary}
   
   SKILLS & EXPERTISE: {skills_formatted}
   
   CURRENT STATE: {state_formatted}
   
   RELEVANT MEMORY: {queried_memory}
   
   SITUATION: {content}
   
   YOUR THINKING SO FAR: {prior_thoughts}
   
   Provide your considered thoughts:"

Example Use:
  - Well-formed opinions on technical approaches
  - Synthesized viewpoints for sharing
  - Comprehensive answers to questions
```

#### 4.3.4 ANALYTICAL Tier

```yaml
Purpose: Deep analysis with full context
When Used:
  - Complex decisions
  - Pattern recognition
  - Risk assessment
  
Memory Access: Full search (all memory tiers + pattern library)
Context Depth: Deep (everything relevant)
Can Interrupt: Yes
Runs Parallel: No

Example Prompt:
  "IDENTITY: {full_identity}
   
   EXPERTISE: {full_skills_with_experience}
   
   RELEVANT EXPERIENCE: {historical_context}
   
   PATTERNS YOU'VE LEARNED: {relevant_patterns}
   
   RELATIONSHIP CONTEXT: {relationships}
   
   CURRENT STATE: {full_state}
   
   SITUATION: {full_context}
   
   YOUR THINKING PROCESS: {thought_chain}
   
   Provide thorough analysis:
   1. What's really going on here?
   2. What patterns apply?
   3. What are the risks/opportunities?
   4. What's my considered position?"

Example Use:
  - Architecture decision analysis
  - Risk assessment for project approaches
  - Complex problem decomposition
```

#### 4.3.5 COMPREHENSIVE Tier

```yaml
Purpose: Full exploration of complex topics
When Used:
  - Major decisions
  - Creating detailed plans
  - Comprehensive reviews
  
Memory Access: Full search + external context
Context Depth: Maximum
Can Interrupt: Yes
Runs Parallel: No

Example Use:
  - Project retrospective analysis
  - Full technical design review
  - Strategic planning
```

### 4.4 Parallel Processing Model

```
HIGH URGENCY + HIGH RELEVANCE:
────────────────────────────────────────────────────────────────────────

T0 (0ms)     │ REFLEX ─────► ACTION (immediate)
             │    │
T1 (100ms)   │    │  ┌─── REACTIVE (tactical) ──► Refines action
             │    │  │
             │    │  └─── REACTIVE (strategic) ──► Informs next move
             │    │
T2 (500ms)   │    └──────► DELIBERATE ──────────► Updates ongoing response
             │
T3 (2000ms)  │              ANALYTICAL ─────────► Deep refinement (background)
             │
             ▼
             Time

LOW URGENCY + HIGH RELEVANCE (e.g., listening in meeting):
────────────────────────────────────────────────────────────────────────

Stimulus 1   │ REFLEX (observation) ──► Internal Mind
             │
Stimulus 2   │ REFLEX (observation) ──► Internal Mind
             │                              │
Stimulus 3   │ REACTIVE (implication) ──────┘
             │                              │
             │                         Accumulate
             │                              │
             │                              ▼
             │                    ┌─────────────────┐
             │                    │ Stream has 3+   │
             │                    │ related thoughts│
             │                    └────────┬────────┘
             │                             │
             │                    DELIBERATE (synthesis)
             │                             │
             │                             ▼
             │                    ┌─────────────────┐
             │                    │ Ready to Share  │
             │                    │ (when appropriate)
             │                    └─────────────────┘
             ▼
```

### 4.5 Thought Model

```python
@dataclass
class Thought:
    """A single unit of cognition."""
    
    thought_id: str
    created_at: datetime
    
    # Origin
    tier: CognitiveTier
    trigger: str  # stimulus_id, thought_id, or "spontaneous"
    
    # Content
    content: str
    thought_type: str  # insight, concern, question, observation, plan, reaction
    
    # Quality
    confidence: float  # 0.0-1.0
    completeness: float  # 0.0-1.0
    
    # Lifecycle
    externalized: bool = False
    externalized_at: Optional[datetime] = None
    superseded_by: Optional[str] = None
    still_relevant: bool = True
    
    # Relationships
    related_thoughts: List[str] = field(default_factory=list)
    synthesized_into: Optional[str] = None
```

### 4.6 Internal Mind

```python
@dataclass
class InternalMind:
    """The agent's cognitive workspace."""
    
    # Active processing
    active_thoughts: Dict[str, Thought]
    thought_streams: Dict[str, ThoughtStream]  # Trains of thought
    
    # Held for later
    held_insights: List[Thought]  # Things I know but haven't shared
    ready_to_share: List[Thought]  # Ready when appropriate
    
    # Background
    background_tasks: List[CognitiveTask]  # Ongoing deeper processing
```

### 4.7 Cognitive Strategy Planning

The Cognitive Dispatcher determines which tiers to engage based on:

| Factor | Low (0-0.3) | Medium (0.3-0.7) | High (0.7-1.0) |
|--------|-------------|------------------|----------------|
| **Urgency** | Take time to think | Balance speed/depth | REFLEX first, parallel REACTIVE |
| **Complexity** | REACTIVE sufficient | DELIBERATE needed | ANALYTICAL needed |
| **Relevance** | Note only (REFLEX) | Engage proportionally | Full cognitive engagement |

**Strategy Matrix:**

| Urgency | Relevance | Complexity | Strategy |
|---------|-----------|------------|----------|
| High | High | Any | REFLEX → Parallel REACTIVE → Background DELIBERATE |
| High | Low | Any | REFLEX only (note but don't engage) |
| Low | High | High | DELIBERATE → ANALYTICAL |
| Low | High | Low | REACTIVE → DELIBERATE |
| Low | Low | Any | REFLEX only (passive awareness) |

---

## 5. Social Intelligence Model

### 5.1 Overview

Social intelligence is the agent's ability to **read the room** and make appropriate decisions about when and how to contribute. This replaces external orchestration with internal judgment.

### 5.2 Social Context Model

```python
@dataclass
class SocialContext:
    """What the agent perceives about the current social situation."""
    
    # Group composition
    participants: List[ParticipantInfo]
    group_size: int
    group_type: str  # solo, pair, small_team, meeting, large_group, army
    
    # My position
    my_role: str  # facilitator, expert, participant, observer, leader, junior
    my_status_relative: str  # senior, peer, junior, outsider
    
    # Current dynamics
    current_speaker: Optional[str]
    topic_under_discussion: str
    discussion_phase: str  # opening, exploring, debating, deciding, closing
    
    # Expertise map
    expertise_present: Dict[str, List[str]]  # skill → agent_ids
    expertise_gaps: List[str]  # Needed skills not well-represented
    
    # Conversational state
    speaking_distribution: Dict[str, int]  # agent_id → contribution count
    energy_level: str  # heated, engaged, neutral, flagging
    consensus_level: str  # aligned, discussing, divided, conflicted

@dataclass
class ParticipantInfo:
    """What I know about another participant."""
    
    agent_id: str
    name: str
    role: str
    expertise_areas: List[str]
    
    # From my relationship memory
    my_relationship: Optional[RelationshipState]
    
    # Current observation
    has_spoken: bool
    seems_engaged: bool
    apparent_position: Optional[str]  # On current topic
```

### 5.3 Externalization Intent

```python
class ExternalizationIntent(Enum):
    """The agent's decision about whether/how to contribute."""
    
    MUST_RESPOND = "must_respond"       # Directly addressed, must answer
    SHOULD_CONTRIBUTE = "should"        # My expertise is specifically needed
    MAY_CONTRIBUTE = "may"              # I have value to add
    ACTIVE_LISTEN = "listen"            # Learning, not contributing
    PASSIVE_AWARENESS = "passive"       # Background noise
```

### 5.4 Social Intelligence Evaluation

The Social Intelligence module evaluates multiple factors:

#### 5.4.1 Self-Awareness Factors

| Factor | Question | Evaluation |
|--------|----------|------------|
| Expertise Match | How much do I know about this topic? | Skills overlap with topic keywords |
| Confidence | Am I confident enough to speak? | Expertise × personality confidence |
| Contribution Saturation | Have I said enough already? | My share vs. fair share for my role |

#### 5.4.2 Social Awareness Factors

| Factor | Question | Evaluation |
|--------|----------|------------|
| Deference Appropriate | Is someone more qualified here? | Others' expertise > mine by threshold |
| Conversational Space | Is there room for me to speak? | No one currently speaking, phase allows |
| Role Expectation | What does my role suggest? | Role-behavior mapping |
| Group Size Adjustment | How selective should I be? | Larger groups → higher threshold |

#### 5.4.3 Decision Algorithm

```python
def should_i_speak(
    self,
    stimulus: Stimulus,
    context: SocialContext
) -> ExternalizationDecision:
    """Core social intelligence decision."""
    
    # 1. Direct address always gets response
    if self._am_i_directly_addressed(stimulus):
        return ExternalizationDecision(
            intent=ExternalizationIntent.MUST_RESPOND,
            confidence=1.0,
            reason="directly_addressed"
        )
    
    # 2. Calculate expertise relevance
    relevance = self._calculate_expertise_match(stimulus.topic)
    if relevance < 0.3:
        return ExternalizationDecision(
            intent=ExternalizationIntent.PASSIVE_AWARENESS,
            confidence=0.9,
            reason="not_my_area"
        )
    
    # 3. Check if I should defer
    if self._is_someone_more_qualified_present(stimulus.topic, context):
        if not self._has_that_person_spoken(context):
            return ExternalizationDecision(
                intent=ExternalizationIntent.ACTIVE_LISTEN,
                confidence=0.7,
                reason="defer_to_expert"
            )
    
    # 4. Check conversational space
    if not self._is_there_conversational_space(context):
        return ExternalizationDecision(
            intent=ExternalizationIntent.ACTIVE_LISTEN,
            confidence=0.8,
            reason="no_space",
            timing="wait_for_opening"
        )
    
    # 5. Check if I've said enough
    if self._have_i_said_enough(context):
        if not self._is_my_input_critical(stimulus):
            return ExternalizationDecision(
                intent=ExternalizationIntent.ACTIVE_LISTEN,
                confidence=0.6,
                reason="said_enough"
            )
    
    # 6. Check role appropriateness
    role_action = self._what_does_role_suggest(context)
    if role_action == "mostly_listen" and not self._is_this_exceptional():
        return ExternalizationDecision(
            intent=ExternalizationIntent.ACTIVE_LISTEN,
            confidence=0.7,
            reason="role_is_observer"
        )
    
    # 7. Passed all checks - should contribute
    contribution_type = self._determine_contribution_type(stimulus, context)
    
    return ExternalizationDecision(
        intent=ExternalizationIntent.SHOULD_CONTRIBUTE 
               if relevance > 0.6 
               else ExternalizationIntent.MAY_CONTRIBUTE,
        confidence=relevance,
        contribution_type=contribution_type,
        reason="have_valuable_input"
    )
```

### 5.5 Role-Based Behavior

| Role | Default Behavior | Speaking Threshold | Listen Emphasis |
|------|------------------|-------------------|-----------------|
| Facilitator | Enable others to contribute | Low (often speak) | High (monitor room) |
| Expert | Contribute in domain | Medium | Medium |
| Participant | Contribute when relevant | Medium-High | High |
| Observer | Mostly listen | Very High (rare) | Very High |
| Leader | Guide and decide | Low | High |
| Junior | Learn and ask | High (selective) | Very High |

### 5.6 Group Size Adaptation

| Group Size | Contribution Threshold | Speaking Style | Listening Emphasis |
|------------|----------------------|----------------|-------------------|
| Solo (1) | Always contribute | Comprehensive | N/A |
| Pair (2) | High engagement | Conversational | Active |
| Small (3-6) | Moderate threshold | Focused | Balanced |
| Meeting (7-20) | Higher threshold | Selective | High |
| Large (21-100) | Very high threshold | Only when critical | Very high |
| Army (100+) | Respond to commands only | Minimal | Follow structure |

### 5.7 Personality Influence on Social Behavior

```python
social_personality_markers = {
    # How readily I share views
    "confidence": 7,           # 0-10
    
    # How strongly I push my position
    "assertiveness": 5,        # 0-10
    
    # How much I yield to others' expertise
    "deference": 4,            # 0-10
    
    # How much I ask questions
    "curiosity": 8,            # 0-10
    
    # How well I read rooms
    "social_calibration": 7,   # 0-10
    
    # How much hierarchy affects my behavior
    "status_sensitivity": 5,   # 0-10
    
    # Preference for group vs solo contribution
    "collaboration_drive": 8,  # 0-10
    
    # Tendency to help others contribute
    "facilitation_instinct": 6, # 0-10
    
    # Comfort speaking to large groups
    "comfort_in_spotlight": 4, # 0-10
    
    # Willingness to disagree
    "comfort_with_conflict": 6, # 0-10
}
```

---

## 6. Agent Profile Model

### 6.1 Overview

Each agent has a comprehensive profile representing their identity, skills, personality, and behavioral characteristics. This is the "CV" of the consultant.

### 6.2 Profile Structure

```python
@dataclass
class AgentProfile:
    """Complete agent profile - the 'CV' and personality."""
    
    # Identity
    agent_id: str
    name: str
    role: str  # "Senior Architect", "Backend Developer", "QA Lead"
    title: str  # "Principal Consultant", "Senior Associate"
    
    # Background
    backstory_summary: str  # 200-500 chars
    years_experience: int
    education: List[str]
    certifications: List[str]
    
    # Skills (0-10 scale)
    skills: Dict[str, int]
    
    # Personality
    personality_markers: Dict[str, int]  # 0-10 scale
    social_markers: Dict[str, int]  # Social behavior traits
    
    # Communication style
    communication_style: CommunicationStyle
    
    # Constraints
    knowledge_domains: List[str]
    knowledge_gaps: List[str]
    
    # Preferences
    working_preferences: WorkingPreferences
```

### 6.3 Skills Model

```python
@dataclass
class SkillSet:
    """Hierarchical skill model."""
    
    # Technical skills (0-10)
    technical: Dict[str, int] = field(default_factory=lambda: {
        # Languages
        "python": 0,
        "javascript": 0,
        "typescript": 0,
        "java": 0,
        "go": 0,
        "rust": 0,
        
        # Frameworks
        "react": 0,
        "fastapi": 0,
        "django": 0,
        "spring": 0,
        
        # Infrastructure
        "kubernetes": 0,
        "docker": 0,
        "aws": 0,
        "gcp": 0,
        "terraform": 0,
        
        # Data
        "postgresql": 0,
        "mongodb": 0,
        "redis": 0,
        "kafka": 0,
        
        # Practices
        "system_design": 0,
        "api_design": 0,
        "security": 0,
        "performance": 0,
        "testing": 0,
    })
    
    # Domain knowledge (0-10)
    domains: Dict[str, int] = field(default_factory=lambda: {
        "fintech": 0,
        "healthcare": 0,
        "ecommerce": 0,
        "gaming": 0,
        "enterprise": 0,
        "startup": 0,
        "ai_ml": 0,
    })
    
    # Soft skills (0-10)
    soft_skills: Dict[str, int] = field(default_factory=lambda: {
        "communication": 0,
        "leadership": 0,
        "mentoring": 0,
        "negotiation": 0,
        "presentation": 0,
        "facilitation": 0,
        "conflict_resolution": 0,
    })
    
    def get_top_skills(self, n: int = 5) -> List[Tuple[str, int]]:
        """Get top N skills across all categories."""
        all_skills = {**self.technical, **self.domains, **self.soft_skills}
        sorted_skills = sorted(all_skills.items(), key=lambda x: -x[1])
        return sorted_skills[:n]
    
    def get_relevance(self, topic: str, keywords: List[str]) -> float:
        """Calculate relevance to a topic based on skill overlap."""
        all_skills = {**self.technical, **self.domains, **self.soft_skills}
        
        matched_skills = []
        for keyword in keywords:
            keyword_lower = keyword.lower()
            for skill, level in all_skills.items():
                if keyword_lower in skill or skill in keyword_lower:
                    matched_skills.append(level)
        
        if not matched_skills:
            return 0.0
        
        return sum(matched_skills) / (len(matched_skills) * 10)
```

### 6.4 Personality Markers

```python
PERSONALITY_MARKERS = {
    # Core personality (stable)
    "openness": 7,           # Openness to new ideas
    "conscientiousness": 8,  # Attention to detail, reliability
    "extraversion": 5,       # Energy from social interaction
    "agreeableness": 6,      # Cooperative vs competitive
    "neuroticism": 3,        # Emotional stability (lower = more stable)
    
    # Professional traits
    "perfectionism": 6,      # Standards for work quality
    "pragmatism": 7,         # Practical vs idealistic
    "risk_tolerance": 5,     # Comfort with uncertainty
    "autonomy_preference": 6, # Solo vs collaborative work
    
    # Cognitive style
    "analytical_thinking": 8, # Data-driven vs intuitive
    "big_picture": 6,        # Strategic vs detail-oriented
    "creativity": 5,         # Novel solutions vs proven approaches
}
```

### 6.5 Communication Style

```python
@dataclass
class CommunicationStyle:
    """How the agent communicates."""
    
    # Verbal style
    vocabulary_level: str  # "simple", "moderate", "technical", "academic"
    sentence_structure: str  # "terse", "moderate", "elaborate"
    formality: str  # "casual", "professional", "formal"
    
    # Patterns
    uses_analogies: bool = True
    uses_examples: bool = True
    asks_clarifying_questions: bool = True
    summarizes_frequently: bool = False
    
    # Quirks
    verbal_tics: List[str] = field(default_factory=list)  # "Actually...", "In my experience..."
    avoids_phrases: List[str] = field(default_factory=list)
    
    # Response style
    default_response_length: str = "moderate"  # "brief", "moderate", "thorough"
    explanation_depth: str = "moderate"  # "surface", "moderate", "deep"
```

---

## 7. Memory Architecture

### 7.1 Overview

Memory is organized in tiers matching human memory systems, with cognitive tier-appropriate access patterns.

### 7.2 Memory Tiers

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         MEMORY ARCHITECTURE                              │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                    TIER 1: WORKING MEMORY                         │ │
│  │                        (In-Process)                               │ │
│  │                                                                   │ │
│  │   • Current conversation context                                  │ │
│  │   • Active thoughts and thought streams                          │ │
│  │   • Immediate emotional/confidence state                         │ │
│  │   • Ring buffer: Last 10-20 turns                                │ │
│  │                                                                   │ │
│  │   Access: REFLEX, REACTIVE tiers                                 │ │
│  │   Latency: <1ms                                                  │ │
│  │   TTL: Session only                                              │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                              │                                          │
│                              │ Promotion: significance > 0.5            │
│                              ▼                                          │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                 TIER 2: SHORT-TERM MEMORY                         │ │
│  │                    (Redis + PostgreSQL)                           │ │
│  │                                                                   │ │
│  │   • Recent significant events (last 7 days)                      │ │
│  │   • Current project context                                      │ │
│  │   • Recent decisions and their outcomes                          │ │
│  │   • Active relationship states                                   │ │
│  │   • Max 100 entries per agent                                    │ │
│  │                                                                   │ │
│  │   Access: REACTIVE, DELIBERATE tiers                             │ │
│  │   Latency: <10ms                                                 │ │
│  │   TTL: 7 days, then promotion or deletion                        │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                              │                                          │
│                              │ Promotion: significance > 0.7            │
│                              │           OR relationship_change > 1     │
│                              ▼                                          │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                  TIER 3: LONG-TERM MEMORY                         │ │
│  │                      (PostgreSQL)                                 │ │
│  │                                                                   │ │
│  │   • Project chapters (completed project summaries)               │ │
│  │   • Permanent relationship records                               │ │
│  │   • Significant decisions with outcomes                          │ │
│  │   • Character-defining experiences                               │ │
│  │                                                                   │ │
│  │   Access: DELIBERATE, ANALYTICAL, COMPREHENSIVE tiers            │ │
│  │   Latency: <50ms                                                 │ │
│  │   TTL: Permanent                                                 │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                              │                                          │
│                              │ Pattern extraction                       │
│                              ▼                                          │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                   TIER 4: PATTERN LIBRARY                         │ │
│  │                      (PostgreSQL)                                 │ │
│  │                                                                   │ │
│  │   • Success patterns from past projects                          │ │
│  │   • Failure patterns and anti-patterns                           │ │
│  │   • Best practices with confidence scores                        │ │
│  │   • Cross-project learnings                                      │ │
│  │                                                                   │ │
│  │   Access: ANALYTICAL, COMPREHENSIVE tiers                        │ │
│  │   Latency: <100ms                                                │ │
│  │   TTL: Permanent (with confidence decay)                         │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 7.3 Memory Access by Cognitive Tier

| Cognitive Tier | Memory Access | Max Memory Tokens |
|----------------|---------------|-------------------|
| REFLEX | Working only (cached) | 50 |
| REACTIVE | Working + recent short-term | 150 |
| DELIBERATE | Working + indexed short-term | 400 |
| ANALYTICAL | All tiers + pattern query | 800 |
| COMPREHENSIVE | Full retrieval | 1200 |

### 7.4 Working Memory

```python
@dataclass
class WorkingMemory:
    """Active cognitive workspace."""
    
    # Conversation context
    conversation_turns: deque[ConversationTurn]  # Ring buffer, max 20
    
    # Current cognitive state
    active_thoughts: Dict[str, Thought]
    thought_streams: Dict[str, ThoughtStream]
    
    # Immediate state
    current_topic: str
    current_mood: str
    confidence_level: float
    
    # Quick access cache
    cached_responses: Dict[str, str]  # For repeated queries
    
    def get_for_reflex(self, topic: str) -> str:
        """Minimal context for reflex tier."""
        return f"Current topic: {self.current_topic}\n" + \
               f"Mood: {self.current_mood}"
    
    def get_for_reactive(self, topic: str) -> str:
        """Recent context for reactive tier."""
        recent = list(self.conversation_turns)[-5:]
        return self._format_turns(recent)
```

### 7.5 Short-Term Memory

```python
@dataclass
class ShortTermMemory:
    """Recent significant events and project context."""
    
    async def query(
        self,
        topic: str,
        max_results: int = 10,
        max_tokens: int = 300
    ) -> str:
        """Query memories relevant to topic."""
        
        # Simple keyword matching for MVP
        # Future: vector similarity search
        memories = await self.db.query("""
            SELECT content, significance, created_at
            FROM short_term_memories
            WHERE agent_id = $1
              AND expires_at > NOW()
              AND content ILIKE ANY($2)
            ORDER BY significance DESC, created_at DESC
            LIMIT $3
        """, self.agent_id, self._extract_keywords(topic), max_results)
        
        return self._format_memories(memories, max_tokens)
```

### 7.6 Long-Term Memory

```python
@dataclass
class LongTermMemory:
    """Permanent records of significant experiences."""
    
    async def search(
        self,
        topic: str,
        max_results: int = 5,
        max_tokens: int = 500
    ) -> str:
        """Search long-term memories."""
        
        chapters = await self.db.query("""
            SELECT title, summary, significance, outcome, lessons_learned
            FROM project_chapters
            WHERE agent_id = $1
              AND (title ILIKE $2 OR summary ILIKE $2)
            ORDER BY significance DESC
            LIMIT $3
        """, self.agent_id, f"%{topic}%", max_results)
        
        return self._format_chapters(chapters, max_tokens)
```

### 7.7 Pattern Library

```python
@dataclass
class Pattern:
    """A learned pattern from experience."""
    
    pattern_id: str
    name: str
    category: str  # architecture, process, communication, testing
    
    # When to apply
    context_triggers: List[str]
    preconditions: List[str]
    
    # What to do
    recommendation: str
    implementation_notes: str
    
    # Evidence
    success_count: int
    failure_count: int
    confidence: float  # Calculated from outcomes
    
    # Source
    source_projects: List[str]
    discovered_at: datetime
    last_applied: datetime

class PatternLibrary:
    """Institutional knowledge accumulated from projects."""
    
    async def query(
        self,
        topic: str,
        max_results: int = 3,
        max_tokens: int = 300
    ) -> str:
        """Find relevant patterns."""
        
        patterns = await self.db.query("""
            SELECT name, recommendation, confidence, success_count, failure_count
            FROM patterns
            WHERE $1 = ANY(context_triggers)
               OR name ILIKE $2
            ORDER BY confidence DESC
            LIMIT $3
        """, topic, f"%{topic}%", max_results)
        
        return self._format_patterns(patterns, max_tokens)
    
    async def record_outcome(
        self,
        pattern_id: str,
        project_id: str,
        outcome: str,  # success, partial_success, failure
        notes: str
    ):
        """Update pattern based on project outcome."""
        
        if outcome == "success":
            await self.db.execute("""
                UPDATE patterns 
                SET success_count = success_count + 1,
                    confidence = (success_count + 1.0) / (success_count + failure_count + 1.0),
                    last_applied = NOW()
                WHERE pattern_id = $1
            """, pattern_id)
        elif outcome == "failure":
            await self.db.execute("""
                UPDATE patterns 
                SET failure_count = failure_count + 1,
                    confidence = success_count / (success_count + failure_count + 1.0),
                    last_applied = NOW()
                WHERE pattern_id = $1
            """, pattern_id)
```

### 7.8 Relationship State

```python
@dataclass
class RelationshipState:
    """Agent's relationship with another agent or user."""
    
    agent_id: str
    other_id: str
    
    # Professional relationship (0-10)
    collaboration_quality: int  # How well we work together
    trust: int  # Professional trust
    respect: int  # Professional respect
    communication_alignment: int  # How well we communicate
    
    # History
    projects_together: int
    successful_collaborations: int
    conflicts_resolved: int
    conflicts_unresolved: int
    
    # Learned dynamics
    interaction_count: int
    first_interaction: datetime
    last_interaction: datetime
    working_style_notes: str  # "Prefers direct feedback"
    strengths_together: List[str]  # "API design discussions"
    friction_points: List[str]  # "Different testing philosophies"
```

### 7.9 Memory Promotion Logic

```python
async def evaluate_memory_promotion(
    entry: MemoryEntry,
    agent_state: AgentState
) -> Optional[str]:
    """Determine if memory should be promoted to higher tier."""
    
    # Tier 1 → Tier 2 (Working → Short-term)
    if entry.tier == 1:
        if entry.significance >= 0.5:
            return "tier_2"
        if entry.contains_decision:
            return "tier_2"
        if entry.relationship_delta != 0:
            return "tier_2"
    
    # Tier 2 → Tier 3 (Short-term → Long-term)
    if entry.tier == 2:
        if entry.significance >= 0.7:
            return "tier_3"
        if abs(entry.relationship_delta) >= 1:
            return "tier_3"
        if entry.is_project_milestone:
            return "tier_3"
    
    return None  # No promotion
```

---

## 8. Functional Requirements

### 8.1 Agent Lifecycle Management

#### FR-ALM-001: Create Agent

**Priority**: P0 (Critical)

**Description**: Create a new agent with complete profile.

**Endpoint**: `POST /v1/agents`

**Request**:
```json
{
  "profile": {
    "name": "Alex Chen",
    "role": "Senior Backend Developer",
    "title": "Principal Consultant",
    "backstory_summary": "10 years building distributed systems...",
    "years_experience": 10,
    "skills": {
      "python": 9,
      "system_design": 8,
      "postgresql": 8,
      "kubernetes": 7
    },
    "personality_markers": {
      "openness": 7,
      "conscientiousness": 8,
      "extraversion": 5
    },
    "social_markers": {
      "confidence": 7,
      "assertiveness": 6,
      "deference": 4
    },
    "communication_style": {
      "vocabulary_level": "technical",
      "formality": "professional"
    }
  }
}
```

**Response** (201):
```json
{
  "agent_id": "uuid",
  "status": "created",
  "created_at": "timestamp"
}
```

**Acceptance Criteria**:
- Agent persisted to database
- All required fields validated
- Agent actor can be instantiated
- Returns unique agent_id

---

#### FR-ALM-002: Load Agent

**Priority**: P0 (Critical)

**Description**: Load agent into active memory (lazy loading).

**Behavior**:
- Agent loaded on first interaction
- State restored from database
- Actor started for message processing
- Memory tiers initialized

**Acceptance Criteria**:
- Cold start <500ms
- State fully restored
- Ready to process stimuli

---

#### FR-ALM-003: Unload Agent (LRU)

**Priority**: P1 (High)

**Description**: Unload least recently used agents when at capacity.

**Behavior**:
- Triggered when active agents exceed limit (20 for MVP)
- State persisted before unload
- Background tasks cancelled gracefully
- Memory freed

**Acceptance Criteria**:
- State fully persisted
- No data loss
- Clean resource release

---

#### FR-ALM-004: Delete Agent

**Priority**: P2 (Medium)

**Description**: Permanently delete agent and all data.

**Endpoint**: `DELETE /v1/agents/{agent_id}`

**Acceptance Criteria**:
- Soft delete (30-day retention)
- All related data marked deleted
- Cannot be loaded after deletion

---

### 8.2 Stimulus Processing

#### FR-SP-001: Receive Stimulus

**Priority**: P0 (Critical)

**Description**: Accept stimulus events for agent processing.

**Endpoint**: `POST /v1/agents/{agent_id}/stimulus`

**Request**:
```json
{
  "stimulus": {
    "type": "message",
    "content": "What do you think about using microservices here?",
    "source_id": "agent_or_user_id",
    "source_name": "Sarah",
    "directed_at": ["agent_id"] | "all" | null,
    "metadata": {}
  },
  "social_context": {
    "group_size": 5,
    "group_type": "meeting",
    "participants": [...],
    "current_topic": "architecture discussion",
    "discussion_phase": "exploring"
  },
  "timestamp": "ISO-8601"
}
```

**Response** (200):
```json
{
  "received": true,
  "agent_state": {
    "processing": true,
    "has_pending_thought": false,
    "externalization_intent": "active_listen" | "may_contribute" | etc.
  }
}
```

**Acceptance Criteria**:
- Stimulus queued for processing
- Social context attached
- Response within 50ms (acknowledgment only)

---

#### FR-SP-002: Cognitive Processing

**Priority**: P0 (Critical)

**Description**: Process stimulus through cognitive tiers.

**Behavior**:
1. Cognitive dispatcher assesses urgency/complexity/relevance
2. Appropriate cognitive tiers engaged
3. Thoughts created and added to internal mind
4. Externalization decision made

**Acceptance Criteria**:
- Correct tier selection based on stimulus
- Parallel processing where appropriate
- Thoughts accumulated in streams
- Budget constraints respected

---

#### FR-SP-003: Externalization Decision

**Priority**: P0 (Critical)

**Description**: Decide whether to externalize (speak) or hold thoughts.

**Behavior**:
1. Social intelligence module evaluates factors
2. Returns ExternalizationIntent
3. If speaking, selects best ready thought
4. If holding, thought remains in internal mind

**Acceptance Criteria**:
- Decision made within cognitive budget
- Appropriate for social context
- Role-appropriate behavior
- Group size adaptation

---

### 8.3 Response Generation

#### FR-RG-001: Generate Response

**Priority**: P0 (Critical)

**Description**: When externalizing, generate appropriate response.

**Endpoint**: `GET /v1/agents/{agent_id}/response`

**Response** (200 - Has response):
```json
{
  "has_response": true,
  "response": {
    "content": "I have concerns about microservices for this scale...",
    "contribution_type": "concern",
    "confidence": 0.8,
    "thought_id": "uuid"
  },
  "agent_state": {
    "current_topic_engagement": "high",
    "has_more_thoughts": true
  }
}
```

**Response** (200 - No response):
```json
{
  "has_response": false,
  "reason": "defer_to_expert",
  "agent_state": {
    "externalization_intent": "active_listen",
    "accumulating_thoughts": true
  }
}
```

**Acceptance Criteria**:
- Response matches personality/communication style
- Contribution type appropriate
- Thought marked as externalized
- State updated

---

#### FR-RG-002: Thought Accumulation

**Priority**: P0 (Critical)

**Description**: Accumulate related thoughts into streams.

**Behavior**:
1. New thoughts added to relevant stream
2. Streams synthesized when threshold met
3. Synthesis may produce ready-to-share thought

**Synthesis Triggers**:
- 3+ related thoughts accumulated
- Thoughts span >30 seconds
- Explicit synthesis request

**Acceptance Criteria**:
- Related thoughts grouped correctly
- Synthesis at appropriate threshold
- Ready thoughts added to sharing queue

---

### 8.4 Meeting Support

#### FR-MT-001: Join Meeting

**Priority**: P0 (Critical)

**Description**: Agent joins a meeting context.

**Endpoint**: `POST /v1/meetings/{meeting_id}/join`

**Request**:
```json
{
  "agent_id": "uuid",
  "role_in_meeting": "expert",
  "topics_of_interest": ["backend", "security"]
}
```

**Acceptance Criteria**:
- Agent added to meeting participants
- Role assigned
- Social context updated

---

#### FR-MT-002: Meeting State Tracking

**Priority**: P1 (High)

**Description**: Track meeting state for social context.

**Tracked State**:
- Current speaker
- Discussion phase
- Topic under discussion
- Speaking distribution
- Consensus level

**Acceptance Criteria**:
- State updated on each contribution
- Available to all agents
- Accurate speaking distribution

---

### 8.5 Pattern Learning

#### FR-PL-001: Record Project Outcome

**Priority**: P1 (High)

**Description**: Record project outcome for pattern learning.

**Endpoint**: `POST /v1/projects/{project_id}/outcome`

**Request**:
```json
{
  "outcome": "success",
  "metrics": {
    "on_time": true,
    "on_budget": false,
    "client_satisfaction": 8.5,
    "quality_score": 9
  },
  "retrospective": {
    "what_worked": ["Early design reviews", "Pair programming"],
    "what_failed": ["Underestimated OAuth complexity"],
    "patterns_applied": ["pattern_id_1", "pattern_id_2"]
  }
}
```

**Acceptance Criteria**:
- Outcome recorded
- Pattern confidence updated
- Agent memories updated
- New patterns extracted

---

#### FR-PL-002: Query Patterns

**Priority**: P1 (High)

**Description**: Query patterns relevant to current context.

**Endpoint**: `GET /v1/agents/{agent_id}/patterns?topic={topic}`

**Response**:
```json
{
  "patterns": [
    {
      "pattern_id": "uuid",
      "name": "Early API Design Review",
      "recommendation": "Conduct API design review in week 1",
      "confidence": 0.85,
      "success_rate": "17/20"
    }
  ]
}
```

**Acceptance Criteria**:
- Relevant patterns returned
- Sorted by confidence
- Include success/failure counts

---

### 8.6 State Management

#### FR-SM-001: Get Agent State

**Priority**: P1 (High)

**Description**: Retrieve current agent state.

**Endpoint**: `GET /v1/agents/{agent_id}/state`

**Response**:
```json
{
  "agent_id": "uuid",
  "cognitive_state": {
    "active_thoughts": 3,
    "thought_streams": 2,
    "ready_to_share": 1,
    "background_processing": true
  },
  "social_state": {
    "current_role": "expert",
    "engagement_level": "high",
    "contribution_count_this_session": 5
  },
  "emotional_state": {
    "confidence": "high",
    "confidence_intensity": 0.8,
    "active_concerns": ["Timeline risk"]
  }
}
```

---

#### FR-SM-002: Confidence State

**Priority**: P1 (High)

**Description**: Track agent confidence (replaces mood for consultants).

**Confidence States**:
- `high` - Confident in contributions
- `moderate` - Normal operating state  
- `uncertain` - Lacking information
- `concerned` - Seeing risks

**Decay Behavior**:
- Extreme states decay toward moderate
- Half-life: 10 minutes for temporary states

---

## 9. Non-Functional Requirements

### 9.1 Performance Requirements

#### NFR-PERF-001: Reflex Latency

**Requirement**: REFLEX tier responses in <200ms (p95)

**Measurement**: End-to-end from stimulus receipt to thought creation
**Model**: Qwen2.5-3B
**Tokens**: ≤150

---

#### NFR-PERF-002: Reactive Latency

**Requirement**: REACTIVE tier responses in <500ms (p95)

**Measurement**: End-to-end from stimulus receipt to thought creation
**Model**: Qwen2.5-7B
**Tokens**: ≤400

---

#### NFR-PERF-003: Deliberate Latency

**Requirement**: DELIBERATE tier responses in <2,000ms (p95)

**Measurement**: End-to-end from stimulus receipt to thought creation
**Model**: Qwen2.5-14B
**Tokens**: ≤1,200

---

#### NFR-PERF-004: Concurrent Agents

**Requirement**: Support 20 concurrent active agents

**Test Condition**: All agents processing stimuli
**Acceptance**: No degradation in latency targets

---

#### NFR-PERF-005: Stimulus Throughput

**Requirement**: Process 100 stimuli/second across all agents

**Test Condition**: 20 agents, mixed stimulus types
**Acceptance**: All processed within tier latency targets

---

### 9.2 Scalability Requirements

#### NFR-SCALE-001: Memory Per Agent

**Requirement**: ≤100MB per active agent

**Includes**: Profile, working memory, cached state
**Test**: 20 agents for 1 hour
**Total**: <2GB for agent state

---

#### NFR-SCALE-002: Model Serving Capacity

**Requirement**: Model servers handle peak load

**Capacities**:
- Small (3B): 500 tokens/sec
- Medium (7B): 300 tokens/sec
- Large (14B): 200 tokens/sec

---

### 9.3 Reliability Requirements

#### NFR-REL-001: Availability

**Requirement**: 99% uptime during testing

**Measurement**: 30-day rolling period
**Acceptable Downtime**: <7.2 hours/month

---

#### NFR-REL-002: Model Fallback

**Requirement**: Graceful degradation when model tier unavailable

**Behavior**:
- Timeout after tier-specific deadline
- Fallback to next available tier
- Never lose stimulus

---

#### NFR-REL-003: State Durability

**Requirement**: No state loss on graceful shutdown

**Behavior**:
- SIGTERM triggers state flush
- 30-second grace period
- All agents persisted

---

### 9.4 Budget Requirements

#### NFR-BUDGET-001: Hourly Cost Limit

**Requirement**: Total infrastructure cost ≤$15/hour

**Breakdown**:
- GPU inference: ≤$12/hour
- Supporting infrastructure: ≤$3/hour

---

#### NFR-BUDGET-002: Token Budget Management

**Requirement**: Active monitoring and throttling of token usage

**Behavior**:
- Per-tier budget allocation
- Throttle when approaching limits
- Alert at 80% utilization

---

## 10. Data Models

### 10.1 Agent Profile Table

```sql
CREATE TABLE agent_profiles (
    agent_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Identity
    name VARCHAR(100) NOT NULL,
    role VARCHAR(100) NOT NULL,
    title VARCHAR(100),
    backstory_summary TEXT NOT NULL,
    years_experience INT,
    
    -- Skills and personality (JSONB for flexibility)
    skills JSONB NOT NULL,
    personality_markers JSONB NOT NULL,
    social_markers JSONB NOT NULL,
    communication_style JSONB NOT NULL,
    
    -- Knowledge
    knowledge_domains JSONB,
    knowledge_gaps JSONB,
    
    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP,
    
    CONSTRAINT valid_skills CHECK (jsonb_typeof(skills) = 'object'),
    CONSTRAINT valid_personality CHECK (jsonb_typeof(personality_markers) = 'object')
);

CREATE INDEX idx_agent_profiles_name ON agent_profiles(name) WHERE deleted_at IS NULL;
CREATE INDEX idx_agent_profiles_role ON agent_profiles(role) WHERE deleted_at IS NULL;
```

### 10.2 Short-Term Memory Table

```sql
CREATE TABLE short_term_memories (
    memory_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agent_profiles(agent_id) ON DELETE CASCADE,
    
    -- Content
    memory_type VARCHAR(50) NOT NULL,  -- observation, decision, interaction, insight
    content TEXT NOT NULL,
    significance FLOAT NOT NULL CHECK (significance >= 0 AND significance <= 1),
    
    -- Context
    project_id UUID,
    related_agents JSONB,  -- Array of agent IDs involved
    topic_keywords JSONB,  -- For querying
    
    -- Emotional context
    confidence_at_time VARCHAR(20),
    
    -- Lifecycle
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    promoted_to UUID,  -- Reference to long-term memory if promoted
    
    CONSTRAINT valid_significance CHECK (significance >= 0 AND significance <= 1)
);

CREATE INDEX idx_stm_agent ON short_term_memories(agent_id);
CREATE INDEX idx_stm_expires ON short_term_memories(expires_at);
CREATE INDEX idx_stm_project ON short_term_memories(project_id);
CREATE INDEX idx_stm_significance ON short_term_memories(significance DESC);
```

### 10.3 Long-Term Memory (Project Chapters)

```sql
CREATE TABLE project_chapters (
    chapter_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agent_profiles(agent_id) ON DELETE CASCADE,
    project_id UUID NOT NULL,
    
    -- Content
    title VARCHAR(200) NOT NULL,
    summary TEXT NOT NULL,
    role_in_project VARCHAR(100),
    
    -- Timeline
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP,
    
    -- Outcome
    outcome VARCHAR(50),  -- success, partial_success, failure, ongoing
    significance FLOAT NOT NULL,
    lessons_learned TEXT,
    
    -- Participants
    collaborators JSONB,  -- Array of agent IDs
    
    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_chapters_agent ON project_chapters(agent_id);
CREATE INDEX idx_chapters_project ON project_chapters(project_id);
CREATE INDEX idx_chapters_outcome ON project_chapters(outcome);
```

### 10.4 Pattern Library

```sql
CREATE TABLE patterns (
    pattern_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Identity
    name VARCHAR(200) NOT NULL,
    category VARCHAR(50) NOT NULL,  -- architecture, process, communication, testing
    
    -- Applicability
    context_triggers JSONB NOT NULL,  -- Array of keywords/contexts
    preconditions JSONB,  -- Conditions for applicability
    
    -- Content
    recommendation TEXT NOT NULL,
    implementation_notes TEXT,
    anti_pattern_warning TEXT,  -- What not to do
    
    -- Evidence
    success_count INT NOT NULL DEFAULT 0,
    failure_count INT NOT NULL DEFAULT 0,
    confidence FLOAT NOT NULL DEFAULT 0.5,
    
    -- Provenance
    source_projects JSONB,  -- Array of project IDs
    discovered_by UUID,  -- Agent who first identified
    discovered_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_applied TIMESTAMP,
    
    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_patterns_category ON patterns(category);
CREATE INDEX idx_patterns_confidence ON patterns(confidence DESC);
CREATE INDEX idx_patterns_triggers ON patterns USING GIN(context_triggers);
```

### 10.5 Relationship State

```sql
CREATE TABLE agent_relationships (
    relationship_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agent_profiles(agent_id) ON DELETE CASCADE,
    other_agent_id UUID NOT NULL,
    
    -- Relationship quality (0-10)
    collaboration_quality INT NOT NULL DEFAULT 5,
    trust INT NOT NULL DEFAULT 5,
    respect INT NOT NULL DEFAULT 5,
    communication_alignment INT NOT NULL DEFAULT 5,
    
    -- History
    projects_together INT NOT NULL DEFAULT 0,
    successful_collaborations INT NOT NULL DEFAULT 0,
    conflicts_resolved INT NOT NULL DEFAULT 0,
    conflicts_unresolved INT NOT NULL DEFAULT 0,
    
    -- Interaction tracking
    interaction_count INT NOT NULL DEFAULT 0,
    first_interaction TIMESTAMP,
    last_interaction TIMESTAMP,
    
    -- Notes
    working_style_notes TEXT,
    strengths_together JSONB,
    friction_points JSONB,
    
    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    UNIQUE(agent_id, other_agent_id),
    CONSTRAINT valid_quality CHECK (collaboration_quality >= 0 AND collaboration_quality <= 10)
);

CREATE INDEX idx_relationships_agent ON agent_relationships(agent_id);
CREATE INDEX idx_relationships_other ON agent_relationships(other_agent_id);
```

### 10.6 Inference Log (for Budget Tracking)

```sql
CREATE TABLE inference_log (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Request info
    agent_id UUID NOT NULL,
    cognitive_tier VARCHAR(20) NOT NULL,
    model_used VARCHAR(50) NOT NULL,
    
    -- Tokens
    prompt_tokens INT NOT NULL,
    completion_tokens INT NOT NULL,
    total_tokens INT NOT NULL,
    
    -- Cost (for budget tracking)
    estimated_cost_usd DECIMAL(10, 8),
    
    -- Timing
    request_timestamp TIMESTAMP NOT NULL,
    response_timestamp TIMESTAMP,
    latency_ms INT,
    
    -- Status
    status VARCHAR(20) NOT NULL,  -- success, timeout, error, fallback
    error_message TEXT,
    
    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_inference_agent ON inference_log(agent_id);
CREATE INDEX idx_inference_timestamp ON inference_log(request_timestamp);
CREATE INDEX idx_inference_tier ON inference_log(cognitive_tier);

-- Partition by month for efficient cleanup
-- CREATE TABLE inference_log_2024_12 PARTITION OF inference_log
--     FOR VALUES FROM ('2024-12-01') TO ('2025-01-01');
```

---

## 11. API Specifications

### 11.1 Authentication

All endpoints require API key authentication.

**Header**: `X-API-Key: <key>`

**Responses**:
- `401 Unauthorized`: Missing or invalid key
- `403 Forbidden`: Insufficient permissions
- `429 Too Many Requests`: Rate limit exceeded

### 11.2 Core Endpoints

#### Health Check

```
GET /health
```

**Response** (200):
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "models": {
    "small": "available",
    "medium": "available",
    "large": "available"
  },
  "active_agents": 5,
  "budget_utilization": 0.45
}
```

---

#### Create Agent

```
POST /v1/agents
```

See FR-ALM-001 for request/response format.

---

#### Get Agent

```
GET /v1/agents/{agent_id}
```

**Response** (200):
```json
{
  "agent_id": "uuid",
  "profile": { ... },
  "status": "active" | "inactive",
  "created_at": "timestamp"
}
```

---

#### Send Stimulus

```
POST /v1/agents/{agent_id}/stimulus
```

See FR-SP-001 for request/response format.

---

#### Get Response

```
GET /v1/agents/{agent_id}/response
```

See FR-RG-001 for response format.

**Query Parameters**:
- `wait_ms` (optional): Max time to wait for response (default: 0)

---

#### Get Agent State

```
GET /v1/agents/{agent_id}/state
```

See FR-SM-001 for response format.

---

#### Batch Stimulus (Meeting)

```
POST /v1/meetings/{meeting_id}/stimulus
```

**Request**:
```json
{
  "stimulus": {
    "type": "message",
    "content": "Let's discuss the authentication approach.",
    "source_id": "speaker_agent_id",
    "source_name": "Sarah"
  },
  "broadcast": true
}
```

**Response** (200):
```json
{
  "delivered_to": 5,
  "meeting_state": {
    "current_speaker": "speaker_agent_id",
    "phase": "exploring"
  }
}
```

---

#### Get Meeting Responses

```
GET /v1/meetings/{meeting_id}/responses
```

**Response** (200):
```json
{
  "responses": [
    {
      "agent_id": "uuid",
      "agent_name": "Alex",
      "has_response": true,
      "response": {
        "content": "I have thoughts on this...",
        "contribution_type": "insight"
      },
      "intent": "should_contribute"
    },
    {
      "agent_id": "uuid",
      "agent_name": "Jordan",
      "has_response": false,
      "intent": "active_listen",
      "reason": "defer_to_expert"
    }
  ],
  "summary": {
    "want_to_speak": 2,
    "listening": 3
  }
}
```

---

### 11.3 Error Format

```json
{
  "error": {
    "code": "AGENT_NOT_FOUND",
    "message": "Agent with ID {id} not found",
    "details": {}
  },
  "timestamp": "ISO-8601",
  "request_id": "uuid"
}
```

---

## 12. Model Serving Infrastructure

### 12.1 Model Tiers

| Tier | Model | GPU | Quantization | Purpose |
|------|-------|-----|--------------|---------|
| Small | Qwen2.5-3B-Instruct | T4 (16GB) | FP16 | REFLEX |
| Medium | Qwen2.5-7B-Instruct | A10G (24GB) | FP16 | REACTIVE |
| Large | Qwen2.5-14B-Instruct | A100 40GB | FP16 | DELIBERATE+ |

### 12.2 vLLM Configuration

```python
VLLM_CONFIGS = {
    "small": {
        "model": "Qwen/Qwen2.5-3B-Instruct",
        "tensor_parallel_size": 1,
        "dtype": "float16",
        "max_model_len": 2048,
        "gpu_memory_utilization": 0.90,
        "max_num_batched_tokens": 4096,
        "max_num_seqs": 32,
        "enable_prefix_caching": True,
    },
    "medium": {
        "model": "Qwen/Qwen2.5-7B-Instruct",
        "tensor_parallel_size": 1,
        "dtype": "float16",
        "max_model_len": 4096,
        "gpu_memory_utilization": 0.90,
        "max_num_batched_tokens": 8192,
        "max_num_seqs": 24,
        "enable_prefix_caching": True,
    },
    "large": {
        "model": "Qwen/Qwen2.5-14B-Instruct",
        "tensor_parallel_size": 1,
        "dtype": "float16",
        "max_model_len": 8192,
        "gpu_memory_utilization": 0.90,
        "max_num_batched_tokens": 16384,
        "max_num_seqs": 16,
        "enable_prefix_caching": True,
    }
}
```

### 12.3 Model Router

```python
class ModelRouter:
    """Routes requests to appropriate model tier."""
    
    def __init__(self):
        self.endpoints = {
            ModelTier.SMALL: "http://vllm-small:8001",
            ModelTier.MEDIUM: "http://vllm-medium:8002",
            ModelTier.LARGE: "http://vllm-large:8003",
        }
        self.budget_manager = TokenBudgetManager()
    
    async def route(self, request: InferenceRequest) -> InferenceResponse:
        # Map cognitive tier to model tier
        model_tier = self._cognitive_to_model(request.cognitive_tier)
        
        # Check budget
        if self.budget_manager.should_throttle(model_tier):
            model_tier = self.budget_manager.recommend_downgrade(model_tier)
        
        # Make request
        return await self._call_model(model_tier, request)
```

### 12.4 Fallback Strategy

| Primary Tier | Fallback 1 | Fallback 2 | Condition |
|--------------|------------|------------|-----------|
| Large | Medium | Small | Timeout or overload |
| Medium | Small | - | Timeout or overload |
| Small | - | - | No fallback (fastest) |

---

## 13. Performance Requirements

### 13.1 Latency Targets

| Tier | p50 | p95 | p99 | Max |
|------|-----|-----|-----|-----|
| REFLEX | 80ms | 200ms | 300ms | 500ms |
| REACTIVE | 200ms | 500ms | 750ms | 1,000ms |
| DELIBERATE | 800ms | 2,000ms | 3,000ms | 5,000ms |
| ANALYTICAL | 2,000ms | 5,000ms | 7,000ms | 10,000ms |

### 13.2 Throughput Targets

| Model Tier | Tokens/Second | Requests/Minute |
|------------|---------------|-----------------|
| Small (3B) | 500 | 200 |
| Medium (7B) | 300 | 100 |
| Large (14B) | 200 | 50 |

### 13.3 Resource Limits

| Resource | Per Agent | 20 Agents | Limit |
|----------|-----------|-----------|-------|
| Memory | 100MB | 2GB | 4GB |
| CPU | 2% idle, 10% active | 40% peak | 80% |
| DB Connections | 1 | 20 | 50 pool |

---

## 14. Security Requirements

### 14.1 Authentication

- API key required for all endpoints
- Keys scoped to organization
- Rate limiting per key

### 14.2 Data Isolation

- Agent data isolated by organization
- No cross-organization queries
- Audit logging for data access

### 14.3 Input Validation

- JSON schema validation
- Prompt injection prevention
- Content length limits

### 14.4 Model Security

- No direct model access from clients
- Request sanitization before inference
- Output filtering for safety

---

## 15. Technology Stack

### 15.1 Core Service

| Component | Technology | Version |
|-----------|------------|---------|
| Language | Python | 3.11+ |
| Framework | FastAPI | 0.104+ |
| Async | asyncio | stdlib |
| Validation | Pydantic | 2.5+ |

### 15.2 Data

| Component | Technology | Version |
|-----------|------------|---------|
| Primary DB | PostgreSQL | 15+ |
| Cache | Redis | 7.0+ |
| Migrations | Alembic | 1.12+ |

### 15.3 Model Serving

| Component | Technology | Version |
|-----------|------------|---------|
| Serving | vLLM | 0.4+ |
| Models | Qwen2.5 | 3B, 7B, 14B |
| Protocol | OpenAI-compatible | - |

### 15.4 Infrastructure

| Component | Technology |
|-----------|------------|
| Container | Docker |
| Orchestration | Docker Compose (MVP) |
| Monitoring | Prometheus + Grafana |
| Logging | Structured JSON |

### 15.5 Dependencies

```toml
[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.104.1"
uvicorn = {extras = ["standard"], version = "^0.24.0"}
pydantic = "^2.5.0"
sqlalchemy = "^2.0.23"
asyncpg = "^0.29.0"
redis = "^5.0.1"
httpx = "^0.25.2"
prometheus-client = "^0.19.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.3"
pytest-asyncio = "^0.21.1"
pytest-cov = "^4.1.0"
ruff = "^0.1.6"
mypy = "^1.7.0"
```

---

## 16. Testing Requirements

### 16.1 Unit Tests

**Coverage Target**: 80%

**Critical Areas**:
- Cognitive tier selection
- Social intelligence evaluation
- Memory promotion logic
- Token budget management

### 16.2 Integration Tests

**Scenarios**:
1. Full stimulus → thought → response flow
2. Multi-agent meeting simulation
3. Pattern learning from project outcome
4. Memory tier promotion
5. Model fallback on timeout

### 16.3 Social Intelligence Tests

```python
async def test_expert_speaks_on_topic():
    """Agent with expertise should contribute."""
    agent = create_agent(skills={"security": 9})
    context = create_meeting_context(topic="authentication")
    
    decision = await agent.evaluate_externalization(
        stimulus=Stimulus(content="How should we handle auth?"),
        context=context
    )
    
    assert decision.intent == ExternalizationIntent.SHOULD_CONTRIBUTE

async def test_defers_to_greater_expertise():
    """Agent should defer when more qualified agent present."""
    junior = create_agent(skills={"security": 4})
    context = create_meeting_context(
        topic="authentication",
        participants=[
            ParticipantInfo(name="Senior", expertise={"security": 9})
        ]
    )
    
    decision = await junior.evaluate_externalization(stimulus, context)
    
    assert decision.intent == ExternalizationIntent.ACTIVE_LISTEN
    assert decision.reason == "defer_to_expert"

async def test_adapts_to_group_size():
    """Agent should be more selective in larger groups."""
    agent = create_agent(skills={"backend": 7})
    
    small_context = create_meeting_context(group_size=3)
    large_context = create_meeting_context(group_size=15)
    
    small_decision = await agent.evaluate_externalization(stimulus, small_context)
    large_decision = await agent.evaluate_externalization(stimulus, large_context)
    
    # Should be more hesitant in large group
    assert large_decision.confidence < small_decision.confidence
```

### 16.4 Cognitive Tests

```python
async def test_parallel_processing_urgent():
    """Urgent stimulus should trigger parallel REFLEX + REACTIVE."""
    agent = create_agent()
    
    stimulus = Stimulus(
        type="urgent",
        content="Security breach detected!"
    )
    
    thoughts = await agent.process_stimulus(stimulus)
    
    # Should have both reflex and reactive thoughts
    tiers = [t.tier for t in thoughts]
    assert CognitiveTier.REFLEX in tiers
    assert CognitiveTier.REACTIVE in tiers

async def test_thought_accumulation():
    """Related thoughts should accumulate into streams."""
    agent = create_agent()
    
    # Send related stimuli
    await agent.process_stimulus(Stimulus(content="API design point 1"))
    await agent.process_stimulus(Stimulus(content="API design point 2"))
    await agent.process_stimulus(Stimulus(content="API design point 3"))
    
    # Should have synthesized stream
    streams = agent.mind.get_streams_for_topic("API design")
    assert len(streams) == 1
    assert len(streams[0].thoughts) >= 3
```

### 16.5 Load Tests

**Scenario**: 20 agents in active meeting

**Parameters**:
- Duration: 30 minutes
- Stimulus rate: 1 per 5 seconds
- All agents processing

**Success Criteria**:
- All latency targets met
- Budget <$15/hour
- No errors

---

## 17. Deployment Requirements

### 17.1 Infrastructure

**Minimum for MVP**:

| Component | Specification | Cost/Hour |
|-----------|---------------|-----------|
| T4 GPU × 1 | 16GB VRAM | $0.40 |
| A10G GPU × 1 | 24GB VRAM | $1.25 |
| A100 40GB × 1 | 40GB VRAM | $3.50 |
| App Server | 4 vCPU, 16GB RAM | $0.20 |
| PostgreSQL | 2 vCPU, 8GB RAM | $0.15 |
| Redis | 2GB | $0.10 |
| **Total** | | **~$5.60/hr** |

### 17.2 Docker Compose

```yaml
version: '3.8'

services:
  api:
    build: ./api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/cae
      - REDIS_URL=redis://redis:6379
      - VLLM_SMALL_URL=http://vllm-small:8001
      - VLLM_MEDIUM_URL=http://vllm-medium:8002
      - VLLM_LARGE_URL=http://vllm-large:8003
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=cae
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7
    volumes:
      - redis_data:/data
  
  vllm-small:
    image: vllm/vllm-openai:latest
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    command: >
      --model Qwen/Qwen2.5-3B-Instruct
      --port 8001
  
  vllm-medium:
    image: vllm/vllm-openai:latest
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    command: >
      --model Qwen/Qwen2.5-7B-Instruct
      --port 8002
  
  vllm-large:
    image: vllm/vllm-openai:latest
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    command: >
      --model Qwen/Qwen2.5-14B-Instruct
      --port 8003

volumes:
  postgres_data:
  redis_data:
```

### 17.3 Environment Variables

```bash
# Service
SERVICE_PORT=8000
LOG_LEVEL=INFO
ENVIRONMENT=development

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/cae
DATABASE_POOL_SIZE=20

# Redis
REDIS_URL=redis://localhost:6379

# Model Endpoints
VLLM_SMALL_URL=http://localhost:8001
VLLM_MEDIUM_URL=http://localhost:8002
VLLM_LARGE_URL=http://localhost:8003

# Budget
HOURLY_BUDGET_USD=15.00
BUDGET_ALERT_THRESHOLD=0.8

# Agents
MAX_ACTIVE_AGENTS=20
AGENT_MEMORY_LIMIT_MB=100
```

---

## 18. Monitoring & Observability

### 18.1 Metrics

```python
# Agent metrics
active_agents = Gauge('cae_active_agents', 'Active agents')
agent_thoughts = Counter('cae_thoughts_total', 'Thoughts created', ['tier', 'agent_id'])
externalizations = Counter('cae_externalizations_total', 'Externalized thoughts', ['agent_id'])

# Cognitive metrics
cognitive_latency = Histogram(
    'cae_cognitive_latency_seconds', 
    'Cognitive processing latency',
    ['tier'],
    buckets=[0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0]
)

# Social intelligence metrics
externalization_decisions = Counter(
    'cae_externalization_decisions_total',
    'Externalization decisions',
    ['intent', 'reason']
)

# Model metrics
model_requests = Counter('cae_model_requests_total', 'Model requests', ['tier', 'status'])
model_tokens = Counter('cae_model_tokens_total', 'Tokens consumed', ['tier', 'type'])
model_latency = Histogram('cae_model_latency_seconds', 'Model latency', ['tier'])

# Budget metrics
budget_utilization = Gauge('cae_budget_utilization', 'Budget utilization', ['tier'])
estimated_hourly_cost = Gauge('cae_estimated_hourly_cost_usd', 'Estimated hourly cost')
```

### 18.2 Alerts

```yaml
groups:
  - name: cae_alerts
    rules:
      - alert: HighLatency
        expr: histogram_quantile(0.95, cae_cognitive_latency_seconds_bucket{tier="REFLEX"}) > 0.3
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "REFLEX tier latency exceeds target"
      
      - alert: BudgetOverrun
        expr: cae_budget_utilization > 0.9
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Budget utilization above 90%"
      
      - alert: ModelDown
        expr: up{job="vllm"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Model server is down"
```

### 18.3 Dashboards

**Overview Dashboard**:
- Active agents count
- Thoughts per minute by tier
- Externalization rate
- Budget utilization

**Cognitive Dashboard**:
- Latency distribution by tier
- Thought accumulation rates
- Synthesis frequency
- Parallel processing stats

**Social Intelligence Dashboard**:
- Externalization intent distribution
- Deferral reasons
- Speaking distribution across agents
- Group size adaptation metrics

**Cost Dashboard**:
- Token consumption by tier
- Hourly cost projection
- Budget remaining
- Throttling events

---

## 19. Budget & Cost Management

### 19.1 Cost Model

```python
# GPU costs per hour (typical cloud pricing)
GPU_COSTS = {
    "t4": 0.40,
    "a10g": 1.25,
    "a100_40gb": 3.50,
}

# Derived token costs (GPU cost / tokens per hour)
TOKEN_COSTS_PER_1K = {
    ModelTier.SMALL: 0.40 / (500 * 3600) * 1000,   # ~$0.0002/1K
    ModelTier.MEDIUM: 1.25 / (300 * 3600) * 1000,  # ~$0.0012/1K
    ModelTier.LARGE: 3.50 / (200 * 3600) * 1000,   # ~$0.0049/1K
}
```

### 19.2 Budget Allocation

| Tier | % of Budget | Hourly Allocation |
|------|-------------|-------------------|
| Small (REFLEX) | 10% | $1.50 |
| Medium (REACTIVE) | 25% | $3.75 |
| Large (DELIBERATE+) | 50% | $7.50 |
| Infrastructure | 15% | $2.25 |
| **Total** | **100%** | **$15.00** |

### 19.3 Throttling Rules

```python
class ThrottlingPolicy:
    def should_throttle(self, tier: ModelTier, utilization: float) -> bool:
        thresholds = {
            ModelTier.SMALL: 0.95,   # Almost never throttle REFLEX
            ModelTier.MEDIUM: 0.85,  # Some flexibility
            ModelTier.LARGE: 0.75,   # Throttle earlier for expensive tier
        }
        return utilization > thresholds[tier]
    
    def get_downgrade(self, tier: ModelTier) -> Optional[ModelTier]:
        downgrades = {
            ModelTier.LARGE: ModelTier.MEDIUM,
            ModelTier.MEDIUM: ModelTier.SMALL,
            ModelTier.SMALL: None,  # Cannot downgrade further
        }
        return downgrades[tier]
```

---

## 20. Acceptance Criteria

### 20.1 Functional Acceptance

| ID | Criteria | Test |
|----|----------|------|
| FA-01 | Agents can be created with full profile | Create 20 diverse agents |
| FA-02 | Cognitive tiers process correctly | Stimulus triggers appropriate tier |
| FA-03 | Thoughts accumulate and synthesize | 3+ thoughts create synthesis |
| FA-04 | Social intelligence evaluates correctly | Expert speaks, non-expert defers |
| FA-05 | Externalization decisions appropriate | 85% human agreement |
| FA-06 | Memory tiers function correctly | Promotion at significance thresholds |
| FA-07 | Patterns learned from outcomes | Success updates confidence |

### 20.2 Performance Acceptance

| ID | Criteria | Test |
|----|----------|------|
| PA-01 | REFLEX <200ms p95 | Load test with 20 agents |
| PA-02 | REACTIVE <500ms p95 | Load test with 20 agents |
| PA-03 | DELIBERATE <2000ms p95 | Load test with 20 agents |
| PA-04 | 20 concurrent agents | All processing simultaneously |
| PA-05 | Budget ≤$15/hour | 1-hour sustained operation |

### 20.3 Quality Acceptance

| ID | Criteria | Test |
|----|----------|------|
| QA-01 | Test coverage ≥80% | pytest coverage report |
| QA-02 | Social appropriateness ≥85% | Human evaluation of 100 decisions |
| QA-03 | Thought quality ≥90% | Human evaluation of 100 thoughts |
| QA-04 | No critical bugs | Beta testing period |

---

## 21. Risks & Dependencies

### 21.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Model quality insufficient | Medium | High | Test multiple models, allow swapping |
| Latency targets missed | Medium | Medium | Aggressive optimization, tier fallback |
| Budget exceeded | Medium | Medium | Active monitoring, throttling |
| GPU availability | Low | High | Multi-cloud strategy |
| Memory leaks | Low | High | Comprehensive testing, monitoring |

### 21.2 Dependencies

| Dependency | Criticality | Risk | Mitigation |
|------------|-------------|------|------------|
| Qwen2.5 models | Critical | Low | Alternative: Llama, Mistral |
| vLLM | High | Low | Alternative: TGI, Ollama |
| GPU cloud | Critical | Medium | Multi-provider |
| PostgreSQL | Critical | Low | Managed service |

### 21.3 Resource Dependencies

| Resource | Required | Status |
|----------|----------|--------|
| Development | 2 FTE | TBD |
| DevOps | 0.5 FTE | TBD |
| GPU Budget | $15/hr testing | TBD |
| Cloud Account | AWS/GCP | TBD |

---

## 22. Appendices

### Appendix A: Example Agent Profile

```json
{
  "agent_id": "550e8400-e29b-41d4-a716-446655440001",
  "name": "Alex Chen",
  "role": "Senior Backend Developer",
  "title": "Principal Consultant",
  "backstory_summary": "10 years building distributed systems at scale. Led teams of 5-15 engineers. Specializes in Python and Go backends. Known for pragmatic architecture decisions and mentoring junior developers.",
  "years_experience": 10,
  "skills": {
    "python": 9,
    "go": 7,
    "system_design": 8,
    "postgresql": 8,
    "redis": 7,
    "kubernetes": 7,
    "api_design": 8,
    "performance": 7,
    "security": 6,
    "testing": 8,
    "mentoring": 7,
    "communication": 7
  },
  "personality_markers": {
    "openness": 7,
    "conscientiousness": 8,
    "extraversion": 5,
    "agreeableness": 6,
    "neuroticism": 3,
    "perfectionism": 6,
    "pragmatism": 8,
    "risk_tolerance": 5
  },
  "social_markers": {
    "confidence": 7,
    "assertiveness": 6,
    "deference": 4,
    "curiosity": 7,
    "social_calibration": 7,
    "facilitation_instinct": 5,
    "comfort_with_conflict": 6
  },
  "communication_style": {
    "vocabulary_level": "technical",
    "sentence_structure": "moderate",
    "formality": "professional",
    "uses_analogies": true,
    "uses_examples": true
  },
  "knowledge_domains": ["fintech", "ecommerce", "enterprise"],
  "knowledge_gaps": ["frontend", "mobile", "ml_ops"]
}
```

### Appendix B: Example Cognitive Flow

```
STIMULUS: "What do you think about using microservices for this project?"

AGENT: Alex Chen (Backend Expert)
CONTEXT: 5-person architecture meeting, Alex's expertise is relevant

COGNITIVE DISPATCH:
- Urgency: 0.3 (not urgent, open question)
- Complexity: 0.6 (requires considered response)
- Relevance: 0.8 (high - system design is my area)
→ Strategy: REACTIVE for initial assessment, then DELIBERATE for response

T1 (200ms) - REACTIVE:
"Microservices could work, but need to consider team size and complexity.
 This is definitely my area - I should contribute."

T2 (1500ms) - DELIBERATE:
"Given this is a team of 4 developers and an MVP, microservices might be
 premature. I've seen this pattern fail in projects like X. However, we
 could design for future separation. Let me synthesize a balanced view..."

THOUGHT CREATED:
- Type: Insight
- Content: "For an MVP with 4 devs, I'd recommend a modular monolith..."
- Confidence: 0.85
- Completeness: 0.9

EXTERNALIZATION DECISION:
- Expertise match: 0.8 (my area)
- Has someone more qualified spoken? No
- Have I said enough? No (2 contributions so far)
- Conversational space? Yes
→ Intent: SHOULD_CONTRIBUTE

RESPONSE:
"For an MVP with a team of four, I'd actually lean toward a modular monolith.
 I've seen microservices add significant overhead for small teams - we had that
 challenge on the Fintech project last year. But we can structure the code so
 it's easy to extract services later if we need to scale specific components."
```

### Appendix C: Social Context Example

```json
{
  "group_size": 5,
  "group_type": "meeting",
  "my_role": "expert",
  "my_status_relative": "senior",
  "current_speaker": null,
  "topic_under_discussion": "architecture approach",
  "discussion_phase": "exploring",
  "expertise_present": {
    "system_design": ["alex_chen", "sarah_johnson"],
    "frontend": ["mike_wilson"],
    "security": ["sarah_johnson"],
    "qa": ["lisa_park"]
  },
  "expertise_gaps": ["devops", "database_admin"],
  "speaking_distribution": {
    "facilitator": 5,
    "alex_chen": 2,
    "sarah_johnson": 3,
    "mike_wilson": 1,
    "lisa_park": 1
  },
  "energy_level": "engaged",
  "consensus_level": "discussing"
}
```

### Appendix D: Glossary

| Term | Definition |
|------|------------|
| **Agent** | An AI entity with profile, memory, and cognitive capabilities |
| **Cognitive Tier** | Level of processing depth (REFLEX to COMPREHENSIVE) |
| **Thought** | A unit of cognition that may or may not be externalized |
| **Thought Stream** | Related thoughts accumulating toward synthesis |
| **Externalization** | Decision to share a thought (speak) |
| **Social Context** | Perceived information about current social situation |
| **Working Memory** | Active cognitive workspace (current session) |
| **Pattern** | Learned success/failure pattern from experience |
| **Significance** | Importance score (0-1) for memory promotion |

---

## Document Approval

- [ ] Product Owner: _________________ Date: _______
- [ ] Technical Lead: _________________ Date: _______
- [ ] Architect: _________________ Date: _______

---

**End of Requirements Document**

**Version**: 1.0
**Status**: Draft for Review
