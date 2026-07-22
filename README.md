# 📚 AI Study Planner

An AI-powered study planning and resource management application built with **FastAPI** and **React**. The goal of this project is to help students organize subjects, plan study sessions intelligently, manage study materials, and leverage both **local** and **cloud LLMs** for personalized learning.

> **Status:** 🚧 Active Development

---

## Features

### Study Planning
- Create and manage subjects
- Organize topics under each subject
- Track exams and deadlines
- Generate personalized study schedules
- Rule-based scheduling with AI-assisted planning

### AI Features
- AI-generated study plans
- Explain difficult topics
- Interactive quiz generation
- AI tutor chat
- Support for both:
  - Local models (Ollama)
  - Cloud models (OpenAI / Anthropic)
- Mock provider for development

### Resource Management
- Upload study notes
- Upload PDFs
- Automatic text extraction
- AI-generated summaries
- Previous year paper analysis
- Topic frequency extraction

### Dashboard
- Upcoming exams
- Today's study sessions
- Progress tracking
- Study statistics

---

## Tech Stack

### Backend
- FastAPI
- SQLAlchemy
- SQLite (Development)
- PostgreSQL (Future)
- Pydantic
- HTTPX

### Frontend
- React
- TypeScript
- Vite
- Axios

### AI
- Ollama
- OpenAI API
- Anthropic API

---

## Architecture

The project follows a layered architecture.

```
React
    │
API Services
    │
FastAPI Routers
    │
Services
    │
Repositories
    │
Database
```

AI features are isolated behind a provider abstraction.

```
Planning Service
        │
AI Orchestrator
        │
LLM Provider
        │
 ┌──────────────┬──────────────┐
 │              │              │
Ollama       OpenAI      Anthropic
```

This allows switching AI providers without modifying business logic.

---

## Project Structure

```
backend/
│
├── app/
│   ├── auth/
│   ├── subjects/
│   ├── topics/
│   ├── exams/
│   ├── schedule/
│   ├── resources/
│   ├── ai/
│   └── shared/
│
└── main.py

frontend/
│
├── src/
│   ├── pages/
│   ├── features/
│   ├── components/
│   ├── services/
│   └── app/
```

---

## Getting Started

### Clone the repository

```bash
git clone https://github.com/<username>/Study_Planner.git
cd Study_Planner
```

---

### Backend Setup

Create a virtual environment

```bash
python -m venv .venv
```

Activate it

Windows

```bash
.venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the backend

```bash
uvicorn main:app --reload
```

---

### Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

---

## Environment Variables

Create a `.env` file.

```env
DATABASE_URL=sqlite:///study_planner.db

SECRET_KEY=your_secret_key

AI_PROVIDER=mock

MODEL=qwen3

OLLAMA_URL=http://localhost:11434

OPENAI_API_KEY=

ANTHROPIC_API_KEY=
```

---

## Current Progress

- [x] Authentication
- [x] Subjects
- [x] Topics
- [x] Exams
- [x] Rule-based Planner
- [ ] AI Study Planner
- [ ] AI Tutor
- [ ] AI Chat
- [ ] Resource Upload
- [ ] PDF Analysis
- [ ] Quiz Generation
- [ ] Previous Paper Analysis
- [ ] Dashboard Analytics
- [ ] RAG over Personal Notes

---

## Future Roadmap

- Semantic search over uploaded notes
- Flashcard generation
- Automatic schedule rebalancing
- AI learning recommendations
- Voice tutor
- Multi-agent workflows
- Cloud deployment
- Mobile support

---

## Why this project?

Most study planners only track tasks.

This project aims to become an intelligent **AI Study Assistant** capable of planning study schedules, understanding learning materials, explaining concepts, generating quizzes, and adapting to each student's progress while supporting both local and cloud language models.

---

## License

This project is licensed under the MIT License.
