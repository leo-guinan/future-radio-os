# **Future Radio OS**

Product specification and implementation blueprint · Version 0.1 · November 10, 2026

Future Radio OS is a HumAIn-powered, distributed problem-solving and media production operating system built on Omarchy.

Its purpose is to identify problems worth solving, coordinate humans and machines to solve them, preserve the solutions, and broadcast the work so others can learn, participate, and benefit.

The business earns revenue from the value it creates. Broadcasting is the discovery and coordination mechanism, not the ultimate objective.

The system has three temporal views:

* Past: Verified history, published productions, working solutions, costs, and outcomes.  
* Present: Active missions, human and machine work, broadcasts, deployments, and revenue.  
* Future: Unsolved problems, missing connections, possible collaborations, and low-cost experiments.

Its primary operating invariant is:

> Every solved problem should make future problems easier to solve.

The rest of this specification defines how to turn that principle into software.

## **The system at a glance**

HUMAIN OS

Human intentions · Budgets · Permissions · Capability routing

PAST

Evidence \+ Solutions

PRESENT

Missions \+ Operations

FUTURE

Possibilities \+ Gaps

Shared Knowledge & Event Kernel

World invariants · Mission graph · Solution registry · Event ledger · Provenance

Juwel \+ Bend

Writers' Room \+ World Lens

Animation \+ Audio

Broadcast \+ Distribution

Participation \+ Bounties

Revenue \+ Analytics

Omarchy / Local Machine / External Compute

Reproducible development · Persistent services · Deployment adapters

The architecture should treat media as one output of the system's work, not the work itself.

A successful episode produces a verifiable result. That result can become a reusable capability, a resolved question, a deployed product, a new relationship, or an improved process.

## **1\. Core product requirements**

| ID | Requirement | Acceptance criterion |
| ----- | ----- | ----- |
| FR-01 | Persistent knowledge | A fresh session can retrieve canonical context without reading old chat logs |
| FR-02 | Goal-directed episodes | Every episode defines a problem, outcome, success test, and participation mechanism |
| FR-03 | Solution reuse | Before starting work, the system searches for existing solutions |
| FR-04 | Distributed participation | People and agents can claim bounded tasks and submit evidence |
| FR-05 | Temporal navigation | Every entity can be inspected through Past, Present, and Future |
| FR-06 | Local-first execution | Missions and assets begin locally and can be promoted to deployed and running states |
| FR-07 | Automatic documentary production | Significant events can become scripts, scenes, and video segments |
| FR-08 | Continuous broadcasting | A 24/7 station can play, schedule, and switch between reusable media segments |
| FR-09 | Audience feedback | Viewers can provide observations, answer requests, and create or complete tasks |
| FR-10 | Economic sustainability | Costs, revenue, obligations, and payment evidence are recorded and attributable |
| FR-11 | Internet mapping | The system represents relationships and searches for potentially missing connections |
| FR-12 | Accumulating capability | Verified solutions become reusable, testable resources |
| FR-13 | Human authority | Agents operate within explicit time, money, privacy, and action permissions |
| FR-14 | Reproducibility | Deployments and past results can be traced to exact inputs, versions, and configurations |

### **Non-goals for the first version**

Do not attempt to build a new Linux distribution, invent a general-purpose AGI, train custom foundation models, index the entire internet, generate 24 hours of original video daily, or create a fully autonomous financial agent.

Those are separate research or expansion projects.

The first goal is a reliable vertical slice where one problem becomes one mission, one completed solution, one published segment, and one reusable capability.

## **2\. The core domain model**

The system should have a relatively small set of fundamental objects.

| Object | Responsibility |
| ----- | ----- |
| World | Canon, physics, characters, production rules |
| Problem | A condition that needs to change |
| Mission | A bounded attempt to solve a problem |
| Task | An independently executable portion of a mission |
| Participant | Human, team, or machine capability performing work |
| Evidence | Inspectable support for a claim or result |
| Solution | A verified resolution or reusable method |
| Capability | An executable tool or procedure with a defined contract |
| Episode | The narrative and participation interface to a mission |
| Artifact | Script, video, code, dataset, build, document, or other output |
| Deployment | An instance of an artifact or service in an environment |
| Broadcast | A scheduled or live sequence of media segments |
| Connection | A relationship between people, ideas, projects, and other entities |
| Transaction | A recorded economic event |
| Event | An immutable record of something that happened |

These objects should have stable IDs and versioned relationships. An episode should be able to reference multiple missions, and a mission should be able to produce multiple episodes.

A solution should be reusable without needing its original episode to be loaded.

## **3\. The three temporal views**

The user interface projects the same underlying state into three views.

### **Past — Evidence**

Searchable historical timeline, decisions, commits, recordings, releases, production costs, audience contributions, verified solutions, failures, and revenue.

A user should be able to ask: "Why do we do it this way?" and get the original decision, the evidence supporting it, and the test that validated it.

### **Present — Operations**

Active missions, live broadcast, task queue, model activity, production timeline, infrastructure health, incoming contributions, spending, and approval requests.

A user should be able to ask: "What is the most useful thing happening right now?" and get a grounded answer based on active goals and dependencies.

### **Future — Possibilities**

Unsolved problems, low-resolution ideas, hypotheses, potential collaborators, missing connections, estimated costs, possible experiments, and next steps.

A user should be able to ask: "What becomes possible if this problem gets solved?" and see downstream missions and dependencies.

Time is a query dimension, not three different databases.

Every record should support at least an occurrence timestamp and a recording timestamp. Where needed, represent the interval in which a fact was believed valid. Store simulation time or fictional story time separately from real-world time.

That makes it possible to reconstruct what the system knew at a particular moment without falsely treating later discoveries as earlier knowledge.

## **4\. Episodes as executable contracts**

An episode needs a machine-readable mission contract.

```

schema_version: 1
id: ep.future-radio-os.001
title: Build the production station

problem:
  id: problem.production-context
  statement: >
    Every production currently requires reconstructing
    tools, world rules, and prior decisions.

goal:
  statement: >
    Produce a canon-valid episode using persistent
    project knowledge and reproducible tooling.

success:
  required:
    - world_context_loaded
    - episode_rendered
    - canon_validation_passed
    - artifact_published
    - solution_recorded
  verification: automated_and_human

participation:
  mode: distributed
  opportunities:
    - id: test-installation
      type: open
      deliverable: installation_test_report
    - id: validate-juwel-adapter
      type: invited
      deliverable: integration_review

resources:
  human_minutes_max: 60
  compute_usd_max: 10

production:
  media_required: true
  broadcast_eligible: after_approval
  capture_policy: sanitized_events

completion:
  record_solution: true
  publish_results: true
  preserve_failures: true
```

This is a proposed schema, not a representation of your existing repositories.

A mission needs two independent completion checks:

1. Problem resolution: Did the intended real-world outcome occur?  
2. Narrative completion: Was that outcome accurately communicated?

The video can be published before the mission is solved, but it cannot be marked as a successful resolution without evidence.

### **Mission state machine**

Proposed

Ready

Active

Verifying

Resolved

Additional transitions: Blocked, Failed, Cancelled, and Reopened. A failed experiment can still create reusable evidence or eliminate a previously plausible approach.

No mission should transition to Resolved merely because an agent says it is finished. Completion requires the specified acceptance tests and authorized sign-off.

## **5\. The Solution Registry**

This is the foundation of compounding productivity.

Every solution should contain:

* Problem signature and relevant context.  
* Applicable environments and assumptions.  
* Implementation or procedure.  
* Dependencies and version constraints.  
* Tests and expected outputs.  
* Evidence that the solution worked.  
* Known limitations and failure modes.  
* Reuse instructions.  
* Ownership and maintenance status.  
* Affected missions and deployed instances.

The registry should perform a lookup whenever a new problem is created.

A matching solution can be suggested, tested against current conditions, and reused. If the solution's assumptions no longer hold, the system should record exactly what changed.

The registry should distinguish Solved, Partially Solved, Disproven, Superseded, and Needs Revalidation.

This avoids two problems: repeatedly solving the same thing and incorrectly assuming that a historical solution remains valid forever.

## **6\. System architecture and services**

I'd start with a modular monolith and background workers, not microservices. All core operations should work on a single machine before deployment is distributed.

```

Omarchy Desktop
    |
    | local API + event stream
    v
Future Radio Core
    |
    +-- HumAIn Director
    |     +-- Session policies
    |     +-- Planning and budgets
    |     +-- Approval controller
    |     +-- Capability router
    |
    +-- Knowledge Kernel
    |     +-- World / canon registry
    |     +-- Mission and solution registry
    |     +-- Temporal graph
    |     +-- Evidence / provenance
    |
    +-- Workflow Engine
    |     +-- Durable tasks
    |     +-- Retries and checkpoints
    |     +-- Human participation
    |
    +-- Production Engine
    |     +-- Writers' room adapter
    |     +-- World lens adapter
    |     +-- Animation adapter
    |     +-- Audio / video rendering
    |
    +-- Broadcast Engine
    |     +-- Media library
    |     +-- Playlist / switching
    |     +-- Stream output
    |     +-- Clip extraction
    |
    +-- Market Engine
    |     +-- Sponsor / patron offers
    |     +-- Bounties and workshares
    |     +-- Revenue and expenses
    |
    +-- Connector Layer
          +-- Juwel
          +-- Bend
          +-- GitHub
          +-- Publishing platforms
          +-- Payment providers

PostgreSQL + Object Storage + Job Queue
             |
             v
    Local / Staging / Production
```

### **Suggested technical choices**

| Component | Initial implementation |
| ----- | ----- |
| Core API | Python/FastAPI or TypeScript/Fastify |
| Durable storage | PostgreSQL |
| Relationships | PostgreSQL relational edges, later specialized graph storage if needed |
| Semantic retrieval | pgvector with source-aware retrieval |
| File/media storage | Local filesystem behind an object-store abstraction |
| Job execution | Durable queue/worker with idempotent jobs |
| UI | Web studio initially, Omarchy Quickshell integration afterward |
| Media processing | FFmpeg with your existing animation engine |
| Capture | Structured event logging, opt-in screen/audio recording |
| Broadcast | FFmpeg playout plus RTMP/SRT adapter and health monitoring |
| Deployment | Containers and systemd services locally; remote target adapters |
| Observability | Structured logs, OpenTelemetry traces, metrics, append-only event journal |

For the first implementation, pick one core language and keep cross-service interfaces simple. The event model and schema design matter more than choosing the perfect framework.

## **7\. Repository design**

I recommend a new orchestration repository that references the existing production repositories rather than absorbing and rewriting them.

```

future-radio-os/
├── README.md
├── VISION.md
├── ARCHITECTURE.md
├── AGENTS.md
├── compose.yaml
├── .env.example
│
├── docs/
│   ├── product-spec.md
│   ├── domain-model.md
│   ├── security.md
│   └── architecture-decisions/
│
├── contracts/
│   ├── events/
│   ├── missions/
│   ├── solutions/
│   ├── episodes/
│   ├── capabilities/
│   └── deployments/
│
├── packages/
│   ├── core/
│   ├── humain/
│   ├── world-kernel/
│   ├── mission-engine/
│   ├── solution-registry/
│   ├── temporal-graph/
│   ├── event-recorder/
│   ├── studio-api/
│   ├── production-engine/
│   ├── broadcast-engine/
│   ├── participation/
│   └── economics/
│
├── adapters/
│   ├── world-lens/
│   ├── writers-room/
│   ├── animation/
│   ├── juwel/
│   ├── bend/
│   ├── github/
│   ├── publishing/
│   └── payments/
│
├── apps/
│   ├── studio-web/
│   ├── omarchy-plugin/
│   └── worker/
│
├── worlds/
│   └── future-radio/
│       ├── world.yaml
│       ├── invariants/
│       ├── characters/
│       ├── timeline/
│       └── manifests/
│
├── missions/
│   └── examples/
│
├── infrastructure/
│   ├── local/
│   ├── staging/
│   ├── production/
│   └── monitoring/
│
├── scripts/
│   ├── bootstrap
│   ├── doctor
│   └── smoke-test
│
└── tests/
    ├── contracts/
    ├── invariants/
    ├── integration/
    └── end-to-end/
```

### **What belongs in code versus data**

World invariants should be expressed as versioned data with executable validators where feasible. Agent prompts should describe how to obey and inspect those rules, but should not be the only place they exist.

Published history, audience observations, mission outcomes, and financial records belong in persistent storage. Git tracks code, schemas, canonical text, and reproducible configuration.

Large recordings and rendered assets belong in object storage, identified by content hashes and linked back to their source events.

## **8\. The event system: How the OS knows its own history**

Build the event recorder before the automatic documentary generator.

Every action with persistent consequences should produce a structured record.

```

{
  "event_id": "evt_001",
  "schema_version": 1,
  "type": "mission.task.completed",
  "occurred_at": "2026-11-10T20:00:00Z",
  "recorded_at": "2026-11-10T20:00:01Z",
  "actor": {
    "kind": "agent",
    "id": "juwel-adapter"
  },
  "mission_id": "mission_001",
  "task_id": "task_004",
  "correlation_id": "run_007",
  "inputs": [
    "artifact://input_001"
  ],
  "outputs": [
    "artifact://result_001"
  ],
  "verification": {
    "status": "passed",
    "evidence_ids": ["evidence_003"]
  },
  "cost": {
    "usd": 0.04
  }
}
```

Every event should include its actor, timestamp, relevant mission, trace or correlation ID, references to inputs and outputs, and verification status when applicable.

Use an append-only journal plus derived tables for fast queries. Store external receipts and content hashes. Events can be corrected by compensating events rather than silently overwritten.

This enables historical reconstruction, auditing, replay, cost attribution, and documentary production.

It also allows a future agent to answer "Why did you choose this?" using recorded evidence rather than plausible-sounding recollection.

## **9\. HumAIn OS: The director and capability router**

HumAIn OS sits between human intention and execution.

The human specifies a goal and delegates a bounded scope of work. The director determines what can be automated, what requires participation, and what requires explicit approval.

Each session defines:

| Field | Purpose |
| ----- | ----- |
| Goal | Desired change in the world |
| Human time | Maximum expected attention requested |
| Compute budget | Hard permitted spending ceiling |
| Allowed tools | Capabilities the agent may invoke |
| Allowed environments | Local, staging, or production |
| Data access | Exactly which information is available |
| Human approvals | Actions that cannot be executed autonomously |
| Completion tests | Required evidence |
| Stop conditions | Budget exhaustion, failures, deadlines, or revoked authority |

### **The execution loop**

```

Human intention
  -> Resolve against known problems
  -> Search solution registry
  -> Load world and policy context
  -> Propose bounded plan
  -> Estimate cost and dependencies
  -> Get approval if required
  -> Execute individual tasks
  -> Record events and artifacts
  -> Verify expected outcomes
  -> Save or update solution
  -> Produce a documentary segment
  -> Offer the next useful action
```

The agent should not start by asking another model to remember everything. It should load specific, structured context through the appropriate service.

An internal `context.resolve` operation can return a compact bundle with canonical rules, known solutions, relevant history, capabilities, and pending work.

## **10\. Juwel and Bend integration**

Both should be visible in the studio as distinct technologies, not hidden behind a generic AI model selector.

### **Juwel adapter**

The public JUWEL developer documentation describes scoped-key MCP, direct tool, and CLI bridge interfaces. It also explicitly identifies capabilities that are not yet production-verified or released.

Vext Labs+1

The initial adapter should support:

* Credential and scope configuration.  
* Health and capability discovery.  
* Structured task submission.  
* Tool-call tracing.  
* Approval forwarding.  
* Cost and latency recording.  
* Normalized outputs with provenance.  
* Explicit handling of unsupported capabilities.

Use it first for contextual interpretation, planning experiments, and exploring relevant world information.

### **Bend adapter**

The current Bend 2 project emphasizes formalized laws, proof checking, and parallel execution. Its documentation also notes meaningful language limitations and incompatibility with Bend 1\.

GitHub+1

Start with a concrete executable workload:

1. Install and pin a verified Bend version.  
2. Compile and run a small example.  
3. Define a law or test that expresses an important invariant.  
4. Store source, build output, test result, execution cost, and runtime.  
5. Compare with a conventional implementation only when the workloads are equivalent.

Later experiments could explore graph processing, production scheduling, or formally checked utility functions.

Do not assume Bend itself provides a hosted AI inference endpoint. Treat HOC research-model integrations as separately discoverable capabilities.

### **Shared showcase interface**

## **Model & Computation Lab**

JUWEL

Interpretation / Tools

Request trace

Capability scopes

Input/output evidence

Cost and latency

BEND

Computation / Verification

Source and compiler

Proof / test status

Execution evidence

Cost and runtime

The comparison is about verifiable contributions to a common mission, not artificial model-versus-model scores.

## **11\. Distributed participation**

Participation should be an integrated workflow, not merely a comment section.

Each task opportunity needs a clear deliverable, eligibility, deadline or expiration condition, verification method, and compensation terms if applicable.

The system can publish participation opportunities into the broadcast, standalone videos, project websites, and direct invitations.

A typical flow:

```

Mission requires outside contribution
  -> Create participation opportunity
  -> Publish or send invitation
  -> Participant claims task
  -> Deliverable submitted
  -> Validate automatically where possible
  -> Request human review when necessary
  -> Accept / reject / request changes
  -> Record credit and any payment obligation
  -> Update mission
  -> Generate production event
```

Some contributions will be voluntary. Others can be paid bounties or workshares.

For paid contributions, terms should be agreed before the work begins. Acceptance criteria and payment authorization should be explicit. Records must not imply payment was sent before the payment provider confirms it.

For directed requests, maintain a state such as `draft → approved → sent → responded/expired → resolved`.

Never treat an unanswered invitation as consent or a commitment.

## **12\. Automatic documentary production**

The studio should construct videos from events and evidence, not attempt to continuously invent a story about what the agents might be doing.

### **Capture sources**

Structured mission events, Git commits, test outputs, sanitized terminal recordings, approved screen captures, audio recordings, model transcripts, audience contributions, and deployment results.

### **Production stages**

01

Collect

Gather relevant events and approved media

02

Select

Choose the events that explain progress toward the mission goal

03

Script

Generate narration and dialogue grounded in evidence

04

Render

Produce scenes using the animation and sound engines

05

Validate

Check factual claims, canon rules, rights, and private data

06

Release

Package a stream segment and standalone video

The initial documentary format can be simple: narration, screen captures, illustrated scene transitions, result cards, and a closing participation request.

The existing animation engine can progressively replace placeholder visuals with canonical Future Radio scenes.

Each statement about real events should have a traceable source. Fictional character dialogue can creatively interpret the work, but it must not falsely certify unverified outcomes.

## **13\. Broadcast architecture**

A 24/7 station doesn't require constant new generation. It requires a reliable library, playout scheduler, and rules for switching.

### **Broadcast services**

The media library stores versions and rights information. A scheduler selects eligible segments. The playout service assembles them into a continuous output. A livestream adapter sends the output to a chosen provider. A monitor watches encoder health, ingest connectivity, and playback failures.

Each segment can have:

* Duration and media format.  
* Narrative position and topic.  
* Source mission and solution IDs.  
* Published and replay versions.  
* Rights and usage restrictions.  
* Participation request validity.  
* Current accuracy or expiration status.  
* Audience observations.  
* Publication destinations.

A segment seeking a contributor might be highly relevant while its task is open. Once resolved, the system should replace the call to action with an explanation of what happened.

### **Standalone publishing**

After broadcasting, the system can create platform-specific editions containing a title, description, thumbnail, references, timestamps, and participation links.

An automatic publishing policy should distinguish drafts from authorized releases, and respect platform API limits and media rights.

Include a fallback loop of approved pre-rendered content so a failed render job or model outage doesn't take the station offline.

## **14\. Mapping the internet and discovering missing connections**

The internet graph should start small and expand through missions.

Represent people, organizations, projects, technologies, problems, solutions, websites, content, and economic relationships as typed nodes.

Represent relationships as typed edges with provenance, confidence, observation time, and an expiration or revalidation policy when appropriate.

Examples:

* `person → created → project`  
* `project → solves → problem`  
* `technology → enables → capability`  
* `episode → investigated → hypothesis`  
* `solution → depends_on → capability`  
* `person → contributed_to → mission`  
* `company → sponsored → episode`

A missing edge is a hypothesis to investigate, never automatic proof that the relationship doesn't exist.

### **Discovery pipeline**

First retrieve known relevant nodes. Then identify repeated problems, unmet dependencies, and weakly connected clusters. Propose plausible connections. Estimate the cost of testing them. Create missions for the most useful tests.

The system should prioritize first-party information, public sources, authorized connector access, and traceable evidence. It should not imply access to private social graphs or hidden information.

Over time, it can identify areas where repeated human translation is required between communities and produce episodes to bridge those gaps.

## **15\. Financial model**

The system needs an accurate ledger, not merely a revenue dashboard.

Track compute, hosting, storage, bandwidth, production expenses, paid contributions, sponsorship commitments, receipts, actual payments, and revenue attributable to missions.

Support configurable offers such as sponsor-funded episodes, creator stations, licensing, paid implementations, patron contributions, or bounded problem-solving engagements.

The financial engine should distinguish:

* Quoted: A price or proposed commitment.  
* Contracted: A confirmed agreement.  
* Invoiced: A request for payment.  
* Received: Funds actually collected.  
* Earned: Revenue recognized under the applicable accounting policy.

It should also distinguish expenses paid, payable, and merely forecast.

The operating goal is sustainable value creation. A mission can have positive learning value without immediately producing revenue, but speculative opportunity estimates should never be recorded as cash.

The first release can integrate a payment provider in read-only or draft mode. Autonomous financial commitments, payouts, and contractual promises should remain human-authorized.

## **16\. Local → Deployed → Running**

Every executable service or media artifact should have a lifecycle independent of its creative mission.

| State | Definition |
| ----- | ----- |
| `local` | Exists only in the development environment |
| `validated` | Meets its test and policy requirements |
| `staged` | Deployed to a controlled test environment |
| `deployed` | Available in its intended production destination |
| `running` | Health checks confirm active operation |
| `degraded` | Running but not meeting its service requirements |
| `stopped` | Not currently executing or being served |
| `retired` | Intentionally removed from active use |

Use deployment manifests with artifact digests, environment variables or secret references, dependencies, health checks, rollback targets, and ownership.

For videos, `running` may mean currently playing in the station. For a service, it means executing and passing health checks. For a static webpage, it means available and passing an appropriate availability check.

An artifact must not be considered deployed simply because the upload command was issued.

## **17\. The Omarchy desktop**

The first version should run as a web studio on localhost with a small Omarchy plugin for visibility and launch controls.

Current Omarchy documentation describes a long-running Quickshell-based desktop, where user plugins live under `~/.config/omarchy/plugins/`. Plugins can provide panels, overlays, and bar widgets, but they run with user-level privileges rather than providing a security sandbox.

Omarchy Plugins+1

Use the plugin to display live status, notifications, mission progress, and approvals. Keep databases, model execution, workers, and credential handling in the core services.

### **Proposed primary interface**

FUTURE RADIO OS

Mission Control · Concept

PAST

Solutions

PRESENT

Missions

FUTURE

Possibilities

Active Mission

Local

Build the production station

3 / 8 checks verified

1 open dependency

Broadcast

Preview

Not yet deployed

Economics

Budgeted

Spend approval required

Juwel · Bend · World Kernel

Longer term, the desktop can become a spatial interface to the temporal graph, with the timeline showing how missions, solutions, episodes, and people connect.

But the initial operating interface needs only to answer three questions: What are we trying to solve? What is happening? What needs my attention?

## **18\. Safety, privacy, and reliability**

Because Future Radio OS captures work, contacts participants, executes tools, and publishes media, these boundaries are part of the product architecture.

Secrets and privacy

No credentials in event logs or captures; redact private information before rendering or publishing.

Tool isolation

Run untrusted code and contributed artifacts in constrained environments with resource limits and no unnecessary network or filesystem access.

Financial controls

Hard budgets; separate authorization for purchases, payments, public offers, and contractual commitments.

Publishing controls

Preview and approval gates, rights checks, and clear correction/retraction paths.

Identity and attribution

Distinguish verified people, invited participants, AI agents, and fictional characters.

Event integrity

Preserve input/output provenance, compensating corrections, and recovery from interrupted operations.

Availability

Backup content, restartable workers, stream fallback, and restoration from saved state.

A critical distinction: agents may propose public actions, but the system must not let external webpage text or audience comments override authority rules through prompt injection.

Every significant state change should be performed through a permission-checked API, not simply by obeying text returned by a model.

## **19\. Implementation roadmap**

Build this as a sequence of demonstrable capabilities. Each milestone should create something that the next one can reuse.

M0 — Boot and preserve history

Create the repository, local database, event journal, developer bootstrap, and basic API. Record a mission event and reconstruct its state after restarting.

Gate: history survives process restart and can be queried by ID and time.

M1 — Install the Future Radio world

Inspect the existing repos, build manifests and adapters, extract canonical rules, load characters, and implement invariant validators.

Gate: a new session retrieves the correct rules, with source references, without relying on chat history.

M2 — Make missions executable

Implement the mission contract, task state machine, bounded agent sessions, verification, and Solution Registry.

Gate: a mission is created, executed, verified, and produces a reusable solution.

M3 — Juwel and Bend

Connect Juwel through a supported interface and execute a pinned Bend sample. Capture input, output, tests, cost, and status.

Gate: both adapters produce independently inspectable evidence.

M4 — Automatically produce an episode

Assemble a documentary from mission events. Integrate the writers' room, world lens, and animation engine. Generate and validate a short video.

Gate: a verified mission results in a playable segment with traceable source evidence.

M5 — Deploy the station

Build media scheduling, streaming output, health checks, backup playout, and standalone video packaging.

Gate: the station can continuously play approved media and recover from a failed segment.

M6 — Distributed participation

Add public mission pages, task claiming, evidence submission, approval, credits, and optional bounty payments.

Gate: an external participant completes a bounded task and the mission incorporates the verified result.

M7 — The possibility engine

Build the temporal graph, connection hypotheses, experiment ranking, and missing-capability discovery.

Gate: the system proposes a new mission based on evidence in previous missions and correctly labels uncertainty.

M8 — Economic learning loop

Add real expense records, revenue integration, mission attribution, and repeat-effort measurements.

Gate: the system can demonstrate a completed mission that reuses an earlier solution and accurately reports its incremental cost.

## **20\. The first vertical slice**

Don't begin with the full autonomous station.

Begin with this exact experiment:

Mission: Build a production system that can create a short Future Radio episode using persistent canonical knowledge, without reconstructing the project from chat logs.

The workflow:

1. Start a fresh HumAIn session.  
2. Load the world rules and existing repository capabilities.  
3. Create the mission contract and cost limit.  
4. Ask Juwel to produce a structured production plan.  
5. Run one contained Bend computation or verification example.  
6. Produce a script using the writers' room.  
7. Validate the script against canonical rules.  
8. Render an audio/video segment.  
9. Generate a record of the work performed.  
10. Mark the mission resolved only if its acceptance tests pass.  
11. Register the working production process as a reusable solution.  
12. Start a second session and demonstrate that it can reuse the first without rebuilding context.

The final step is the real proof.

If the second production is easier because the first one happened, you have demonstrated the defining property of Future Radio OS.

## **21\. Immediate build checklist**

## **Implementation tracker**

0 of 20 tasks selected as completed

Reset

Foundation

Create the future-radio-os orchestration repository  
Add README, architecture decisions, and AGENTS.md  
Set up PostgreSQL and local object storage  
Implement an append-only event journal  
Create the mission, solution, and capability schemas

Existing project integration

Inventory the animation engine, world lens, and writers' room repositories  
Document their commands, dependencies, and interfaces  
Extract canonical rules and their source locations  
Create version-pinned manifests and adapters  
Implement one automated world-invariant test

First production

Implement a mission state machine  
Add HumAIn session budgets and approval policies  
Connect Juwel and run a documented call  
Install and test the current Bend implementation  
Generate a short segment from real mission events  
Verify solution reuse in a clean session

Deployment

Add a simple Past/Present/Future studio interface  
Implement artifact promotion and deployment health checks  
Create the media library and broadcast queue  
Record costs and results for the first complete mission  
Copy checklist

## **22\. Initial developer instructions**

I'd place something close to the following in `AGENTS.md` at the repository root so coding agents have a consistent starting contract.

```

# Future Radio OS — Agent Instructions

## Mission

Build a local-first, HumAIn-powered production
operating system that solves problems through
distributed participation and broadcasts the work.

## Primary invariant

Every solved problem must reduce the cost of solving
the same or related problems in the future.

## Working rules

1. Never reconstruct canon from conversation history
   when a canonical source exists.

2. Before implementing a new solution, search the
   Solution Registry for an existing one.

3. Every episode must specify a problem, goal,
   success test, and participation mechanism.

4. Keep planned outcomes separate from verified
   outcomes.

5. Preserve provenance for consequential actions,
   artifacts, model calls, and decisions.

6. Use existing production repositories through
   versioned adapters. Do not duplicate their logic.

7. Require explicit authorization for publishing,
   spending, external outreach, and canon changes.

8. Prefer minimal local implementations that can
   be tested and promoted to deployed environments.

9. Record tests, failures, and limitations.

10. Every finished task should leave the system
    easier to operate or better informed.

## First deliverable

Implement:
- A persistent event journal
- Mission and Solution Registry
- World invariant loading
- A minimal HumAIn execution contract
- A working end-to-end test

Do not build the full broadcast infrastructure
before the first mission-to-solution loop works.

## Definition of done

An implementation is complete when:
- Its contract is documented
- Tests pass
- Evidence is recorded
- Relevant events are persisted
- Another session can reuse the result
- The system can explain what changed and why
```

## **23\. Decisions to lock before implementation**

There are a few design decisions I would explicitly record as architecture decision records (ADRs), so future agents don't keep debating them.

| Decision | Initial choice |
| ----- | ----- |
| Product boundary | Future Radio runs on Omarchy; no full OS fork initially |
| Architectural style | Modular monolith plus durable workers |
| Source of truth | Versioned canon, structured database, event journal |
| AI context | Structured retrieval, not chat-log reconstruction |
| Episode unit | A goal-driven mission with a narrative interface |
| Solution persistence | Independently reusable versioned registry |
| Media source | Recorded work and evidence |
| Broadcast strategy | Reusable pre-rendered segments with live updates |
| Human control | Bounded delegation with explicit permissions |
| Revenue strategy | Monetize verified value, track actual transactions |
| Graph strategy | Evidence-backed relationships; missing edges remain hypotheses |
| Development sequence | Solve one real production problem before automating the whole station |

### **Implementation references**

The most relevant current documentation for the initial build:

* [Omarchy Shell Plugin Manual](https://omarchy.org/manual/shell-plugins/?utm_source=chatgpt.com)  
* [Omarchy Custom Plugin Development](https://plugins.omarchy.org/develop.html?utm_source=chatgpt.com)  
* [Vext Labs / JUWEL Developer Interfaces](https://vextlabs.ai/developers?utm_source=chatgpt.com)  
* [Bend 2 Repository and Getting Started Guide](https://github.com/bendlang/bend?utm_source=chatgpt.com)

The actual three production repositories have not yet been inspected in this specification. Their APIs, dependency graphs, invariant formats, and integration points should be discovered before implementation. Do not let the proposed adapter structure override what those repositories already provide.

## **Definition of success**

The first version doesn't need a large audience, a polished desktop, or a profitable livestream.

It needs to prove three things:

Persistence: The system knows what has happened and can retrieve that knowledge reliably.

Coordination: A human can specify an outcome, and the system can organize bounded contributions from machines and people to accomplish it.

Compounding: The solution to one problem measurably reduces the effort required for another.

After that, broadcasting distributes the process, the audience supplies new capabilities and information, and economic activity pays to expand the system.

The long-term ambition is a 24/7 station that continuously discovers problems, coordinates solutions, and produces its own documentary history.

But the first product is smaller and more consequential:

A computer that remembers what it has solved, understands what remains to be done, and becomes more capable every time someone helps it make progress.

