# Database Schema

VentureMind uses MySQL with UUID primary keys, UTC timestamps, foreign keys, and indexes for the main ownership and lifecycle queries.

```text
users ──< projects ──< startup_ideas ──< evaluations ──< evaluation_scores
  │          │              │                 │
  │          ├──< reports ──┘                 └──< reports
  ├──< security_tokens
  ├──< feedback
  ├──< notifications
  └──< chat_conversations ──< chat_messages
```

## Design decisions

- Startup submissions are versioned per project. Evaluations reference the precise version they analyze.
- Metric-level scores are normalized in `evaluation_scores`; explainability data stays adjacent to each metric.
- Larger, variable AI outputs are JSON documents within `evaluations`, preventing premature tables for unbounded LLM content while retaining one stable evaluation record.
- All authentication tokens are hashed, revocable, typed, and expiry-indexed. Raw refresh or verification tokens are never stored.
- Reports store metadata and object-storage keys—not PDF binary data—in MySQL.
- `ON DELETE CASCADE` removes user-owned project data safely; report references to an evaluation become null when appropriate.

The baseline schema is captured in Alembic revision `20260712_0001`.
