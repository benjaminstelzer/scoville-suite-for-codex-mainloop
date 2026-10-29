## How it works

The current chat owns the Plan, code, required checks and commits. It takes one
original Step at a time through the existing helper; it does not paraphrase the
assignment. Each review is fresh. Explorer reuse requires the same investigation,
an idle agent and unchanged pair/rules; an independent request starts fresh.
Agents choose relevant Skills without gaining additional role rights.

### 1. Main loop

```mermaid
flowchart TD
  A["Activate or resume in the same chat"] --> M{"Own active pair matches main?"}
  M -->|No or unknown| B["Resolve prerequisite; coding stopped"]
  M -->|Yes| N{"New run?"}
  N -->|Yes| G{"Git available and workspace clean?"}
  G -->|No| B
  G -->|Yes| W["Select authorized Work Item; retain start commit"]
  N -->|Resume| R["Reconcile own changes, processes, proof and open reviews"]
  R --> W
  W --> S[["Run ONE original Step; see diagram 2"]]
  S --> D{"All Steps and required reviews complete?"}
  D -->|No| S
  D -->|Yes| C["Helper: all original Steps and full Acceptance"]
  C -->|Success| CR["Fresh closure Reviewer from unchanged returned arguments"]
  C -->|Failure| B
  CR --> V{"Result?"}
  V -->|Defect| nextCorrection{"Supported correction or changed evidence?"}
  nextCorrection -->|Yes| F["Select one affected Step; preserve open findings"]
  nextCorrection -->|No| O["Keep item open; report needed prerequisite"]
  F --> S
  V -->|Missing required proof| P["Recover available proof or finish missing authorized check"]
  P --> C
  V -->|Pass| E["Close and validate records; commit; continue authorized scope"]
```

The new-run Git gate never cleans or commits earlier work. Authorized resumption
reconciles the same started work without prematurely committing it. Missing or
foreign evidence remains an explicit boundary. Stops preserve unfinished work;
compaction continues this same chat from actual Plan, Git, effects and results.

### 2. Step implementation and review

```mermaid
flowchart TD
  S["Save and validate start; helper returns exact Step"] --> I["Main implements; finishes required checks"]
  I --> Q["Establish write, test and restore quiescence"]
  Q --> N{"Files, config or behavior changed, or Step review open?"}
  N -->|No| U["Record completion; no Step review or empty commit"]
  N -->|Yes| R["Helper: original Step, HEAD diff and relevant evidence"]
  R -->|Success| RS["Fresh Reviewer from unchanged returned arguments"]
  R -->|Failure| B["Stop dispatch; resolve helper failure"]
  RS --> V{"Result?"}
  V -->|Defect| nextCorrection{"Supported correction or changed evidence?"}
  nextCorrection -->|Yes| I
  nextCorrection -->|No| O["Keep Step open; report needed prerequisite"]
  V -->|Missing proof| P["Main recovers proof or finishes missing authorized check"]
  P --> Q
  V -->|Pass| C["Commit accepted versionable changes and Plan before next Step"]
```

Keep source and binding inputs unchanged during review. Closure uses the Work
Item start commit, not only the last Step diff. Unexpected HEAD movement must
be reconciled before an empty diff counts as unchanged. Git does not replace
proof of non-file effects. Preserve necessary nonrepeatable evidence through
existing results or artifacts; no mandatory per-Step report or source archive.

### 3. Child selection

```mermaid
flowchart TD
  R{"Role?"} -->|Reviewer| F["Select fresh Reviewer; fixed pair and next number"]
  R -->|Explorer| E{"Same investigation or follow-up; idle; unchanged pair and rules?"}
  E -->|Yes| U["Select followup; same handle, pair and number"]
  E -->|Independent request, no Explorer, or changed pair or rules| N["Select fresh Explorer; fixed pair and next number"]
  E -->|Running or uncertain| W["Wait or resolve native state; no duplicate dispatch"]
  F --> H["Helper builds assignment and native arguments"]
  U --> H
  N --> H
  H --> V{"Exit zero and complete successful output?"}
  V -->|No| B["Stop dispatch; resolve helper failure"]
  V -->|Yes| A["Call native tool with returned arguments unchanged"]
```

Fresh children receive role, writing, shell and result rules once. Explorer
reuse sends its new task and needed context/evidence. Embedded writing and shell
rules satisfy their required reads; unchanged rules stay loaded. Machine-data,
Python discovery and large-output rules load when the operation needs them.
Fresh assignments include accepted Decision text or its valid binding-section
projection; reuse carries current source identities and reads new, changed or
uncertain Decisions. No context measurement or thresholds. Close finished Reviewers
only if native close exists. Interruption proves neither termination nor freed
capacity. Native types are optional; never raise thread limits automatically.

### 4. Questions and planning preparation

```mermaid
flowchart TD
  Q["Question, idea, change request or planning preparation"] --> X["Dispatch read-only Explorer through diagram 3"]
  X --> R["Return relevant facts, proposals and open choices"]
  R --> M["Main answers user; writes authorized Plan changes"]
  M --> W["Continue authorized scope"]
```

Known progress and stop/resume handling need no exploration. A scope-invalidating
change stops dependent implementation first. Explorer writes no Plan or code;
Reviewer runs no project tests. All roles follow the current user's language.
