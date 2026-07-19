                                         USER
                                           │
                                           ▼
                              React + TypeScript + Vite
                                           │
        ┌───────────────────────────┬───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
      Pages                    Components                  API Services
        │                           │                           │
        └───────────────────────────┴───────────────────────────┘
                                           │
                                           ▼
                                   Axios / REST API
                                           │
═══════════════════════════════════════════╪══════════════════════════════════════════════
                                           │
                                      FastAPI Backend
                                           │
                                Authentication Middleware
                                           │
                                           ▼
                                         Routers
                                           │
      ┌─────────────┬──────────────┬──────────────┬─────────────┬──────────────┬─────────────┐
      ▼             ▼              ▼              ▼             ▼              ▼
    Auth        Subjects        Topics         Exams        Schedule      Resources
                                           │
                                           ▼
                                         Services
                                           │
      ┌─────────────┬──────────────┬──────────────┬─────────────┬──────────────┬─────────────┐
      ▼             ▼              ▼              ▼             ▼              ▼
 AuthService  SubjectService  TopicService  ExamService  ScheduleService  ResourceService
                                           │
                                           ▼
═══════════════════════════════════════════╪══════════════════════════════════════════════
                                           │
                                    AI ORCHESTRATOR
                                           │
       ┌───────────────────────────┬──────────────────────────┬──────────────────────────┐
       │                           │                          │                          │
       ▼                           ▼                          ▼                          ▼
 Planning Engine             Tutor Engine             Analysis Engine            Quiz Engine
       │                           │                          │                          │
       ▼                           ▼                          ▼                          ▼
 Planner Prompt             Explain Prompt          Extract Prompt          Quiz Prompt
       │                           │                          │                          │
       └───────────────────────────┴──────────────────────────┴──────────────────────────┘
                                           │
                                           ▼
                                     Prompt Builder
                                           │
                                           ▼
                                       LLM Provider
                                           │
          ┌───────────────────────────────┼────────────────────────────────┐
          ▼                               ▼                                ▼
   Ollama Provider                 OpenAI Provider                 Anthropic Provider
          │
          ▼
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │                Qwen • Llama • Gemma • DeepSeek • Others                    │
 └─────────────────────────────────────────────────────────────────────────────┘
                                           │
                                           ▼
                                Structured JSON / Markdown
                                           │
                                           ▼
                               Parser & Response Validation
                                           │
═══════════════════════════════════════════╪══════════════════════════════════════════════
                                           │
                                   Repository Layer
                                           │
      ┌─────────────┬──────────────┬──────────────┬─────────────┬──────────────┬─────────────┐
      ▼             ▼              ▼              ▼             ▼              ▼
  UserRepo    SubjectRepo     TopicRepo      ExamRepo    ScheduleRepo    ResourceRepo
                                           │
                                           ▼
                                    SQLAlchemy Models
                                           │
                                           ▼
                                  PostgreSQL / SQLite


===========================================================================================
BACKEND
===========================================================================================

backend/
│
├── app/
│   └── main.py
│
├── auth/
│   ├── router.py
│   ├── service.py
│   ├── repository.py
│   ├── models.py
│   ├── schemas.py
│   └── security.py
│
├── subjects/
├── topics/
├── exams/
├── schedule/
├── resources/
│
├── ai/
│   ├── orchestrator.py
│   │
│   ├── planning/
│   │   ├── planner.py
│   │   ├── llm_planner.py
│   │   └── rule_planner.py
│   │
│   ├── prompts/
│   │   ├── planner.py
│   │   ├── tutor.py
│   │   ├── summarizer.py
│   │   ├── extractor.py
│   │   └── quiz.py
│   │
│   ├── providers/
│   │   ├── provider.py
│   │   ├── ollama_provider.py
│   │   ├── openai_provider.py
│   │   └── anthropic_provider.py
│   │
│   ├── parsers/
│   │   ├── json_parser.py
│   │   └── validators.py
│   │
│   └── models/
│       ├── planning_request.py
│       ├── planning_response.py
│       └── chat_response.py
│
└── shared/
    ├── config.py
    ├── database.py
    ├── dependencies.py
    ├── exceptions.py
    └── logger.py


===========================================================================================
FRONTEND
===========================================================================================

frontend/
│
├── src/
│
├── app/
│   ├── App.tsx
│   ├── router.tsx
│   └── providers.tsx
│
├── pages/
│   ├── LoginPage
│   ├── DashboardPage
│   ├── SubjectsPage
│   ├── SubjectDetailsPage
│   ├── PlannerPage
│   ├── ResourcesPage
│   ├── ExamsPage
│   └── SettingsPage
│
├── features/
│   ├── auth/
│   ├── subjects/
│   ├── topics/
│   ├── exams/
│   ├── schedule/
│   ├── resources/
│   └── ai/
│
├── components/
│   ├── Navbar
│   ├── Sidebar
│   ├── Calendar
│   ├── SubjectCard
│   ├── TaskCard
│   ├── UploadArea
│   ├── ChatPanel
│   ├── ProgressBar
│   └── Modal
│
├── services/
│   ├── api.ts
│   ├── auth.ts
│   ├── subjects.ts
│   ├── topics.ts
│   ├── exams.ts
│   ├── schedule.ts
│   ├── resources.ts
│   └── ai.ts
│
├── hooks/
├── utils/
└── types/


===========================================================================================
CORE ENTITIES
===========================================================================================

User
├── Subjects
│   ├── Topics
│   │   ├── ScheduleItems
│   │   ├── StudySessions
│   │   └── Resources
│   └── Exams
└── Settings


===========================================================================================
AI FLOWS
===========================================================================================

Generate Study Plan
React
→ POST /schedule/generate
→ ScheduleRouter
→ ScheduleService
→ AIOrchestrator
→ PlanningEngine
→ PromptBuilder
→ LLMProvider
→ Local/API Model
→ JSON Response
→ Validation
→ ScheduleRepository
→ Database

Explain Topic
React
→ TopicService
→ AIOrchestrator
→ Tutor Prompt
→ LLMProvider
→ Markdown Response

Upload Notes
React
→ ResourceService
→ Extract Text
→ AIOrchestrator
→ Summarizer Prompt
→ Summary
→ Database

Analyze Previous Papers
React
→ ResourceService
→ Extract Text
→ AIOrchestrator
→ Extraction Prompt
→ Structured JSON
→ Topic Frequencies
→ Database

Regenerate Schedule
Missed Sessions
→ ScheduleService
→ PlanningEngine
→ Updated Plan
→ Validation
→ Database

AI Chat
React Chat
→ AIOrchestrator
→ Tutor Prompt
→ LLMProvider
→ Response


===========================================================================================
DESIGN PRINCIPLES
===========================================================================================

• Routers handle HTTP requests and responses.
• Services contain business logic.
• Repositories handle database access only.
• AI Orchestrator is the single entry point for all AI features.
• Planning Engine generates or updates study plans.
• Prompt Builder converts application data into prompts.
• LLM Provider abstracts local (Ollama) and cloud (OpenAI/Anthropic) models.
• Parser & Validator ensure AI responses follow expected schemas.
• AI never communicates directly with the database.
• Every database write goes through Services → Repositories.
• Models can be swapped by configuration without changing business logic.
