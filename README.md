# VentureMind AI

VentureMind AI is an explainable AI platform for evaluating startup ideas and producing actionable business plans.

## Workspace layout

```text
venturemind-ai/
├── backend/                 # FastAPI application (clean architecture)
├── frontend/                # React + Vite application
├── infra/                   # Docker and deployment infrastructure
├── docs/                    # Architecture and project documentation
└── .env.example             # Safe environment-variable template
```

### Backend boundaries

- `api/`: HTTP routes, dependencies, and request orchestration.
- `schemas/`: Pydantic request/response contracts.
- `services/`: use-case and business-rule implementations.
- `repositories/`: persistence interfaces and SQLAlchemy implementations.
- `models/`: SQLAlchemy database models.
- `ai/`: deterministic scoring, NLP, explainability, and LLM adapters.
- `core/`: configuration, security, logging, and shared exceptions.
- `db/`: engine, sessions, and Alembic integration.

### Frontend boundaries

- `features/`: domain-oriented UI modules.
- `components/`: reusable presentational components.
- `pages/`: route-level screens.
- `api/`: HTTP client and endpoint modules.
- `routes/`: router and authorization guards.
- `types/`, `validation/`, `hooks/`, `lib/`: shared client concerns.

## Planned module sequence

1. Folder structure and workspace foundations — complete
2. Backend architecture
3. Frontend architecture
4. Database schema
5. Authentication
6. Landing page
7. Dashboard
8. Startup submission form

Each module is implemented and reviewed independently before proceeding.
