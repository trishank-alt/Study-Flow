# AI Implementation Guide

This document explains **how to implement** the AI subsystem for the Study Planner. It assumes the current project already supports authentication, subjects, topics, exams, and the rule-based planner.

---

# Goal

By the end of this implementation the application should support:

- Local AI (Ollama)
- Cloud AI (OpenAI / Anthropic)
- Mock provider
- AI-generated study plans
- Topic explanations
- AI chat
- Quiz generation
- Resource summarization
- Previous paper analysis

The implementation should be incremental. Every phase should leave the project in a working state.

---

# Phase 1 — Provider Abstraction

## Goal

The backend should be capable of communicating with **any** language model without the rest of the application knowing which one is being used.

Current state

```
ScheduleService

↓

RulePlanner
```

Target

```
ScheduleService

↓

AIOrchestrator

↓

LLMProvider

↓

Model
```

---

## Step 1

Create

```
backend/app/ai/providers/provider.py
```

Define an abstract base class.

Responsibilities

- Generate text
- Generate structured JSON
- Handle provider-specific exceptions

Every provider must implement the same interface.

Example

```
generate_text()

generate_json()
```

Nothing else in the application should call OpenAI or Ollama directly.

---

## Step 2

Implement MockProvider.

Purpose

- Development
- Unit testing
- Frontend testing

It should never perform network requests.

Instead it returns deterministic responses.

Example

```
Explain Binary Search

↓

Return fixed explanation
```

Once finished

✓ Frontend can already use AI endpoints.

---

## Step 3

Implement OllamaProvider.

Responsibilities

- Read Ollama URL
- Read model name
- Send HTTP request
- Return response

Communication

```
Application

↓

httpx

↓

localhost:11434

↓

Ollama

↓

Qwen
```

Use

```
POST /api/generate
```

or

```
POST /api/chat
```

depending on the Ollama API being used.

Do NOT expose Ollama details outside this class.

---

## Step 4

Implement OpenAIProvider.

Responsibilities identical.

Only the endpoint changes.

---

## Step 5

Implement AnthropicProvider.

Same interface.

---

## Completion Checklist

- Mock works
- Ollama works
- OpenAI works
- Anthropic works

Nothing else changes.

---

# Phase 2 — AI Orchestrator

Goal

Centralize provider selection.

Current

```
ScheduleService

↓

OpenAI
```

Bad.

Target

```
ScheduleService

↓

AIOrchestrator

↓

Provider
```

Responsibilities

- Read user settings
- Select provider
- Retry
- Handle failures
- Log requests
- Return parsed response

It should NOT contain prompt engineering.

It should NOT know scheduling logic.

---

# Phase 3 — Prompt System

Goal

Move prompts outside business logic.

Create

```
ai/prompts/
```

Example

```
planner.md

tutor.md

quiz.md

summarizer.md

extractor.md
```

Prompt Builder responsibilities

- Load template
- Inject variables
- Return final prompt

Business logic should never concatenate giant strings.

---

# Phase 4 — Parser Layer

Never trust AI output.

Every structured response must be validated.

Example

```
AI

↓

JSON

↓

Parser

↓

Pydantic Validation

↓

Business Logic
```

Invalid JSON

↓

Raise exception

↓

Fallback

---

# Phase 5 — AI Endpoints

Implement

```
POST /ai/explain

POST /ai/chat

POST /ai/quiz
```

Implementation flow

```
Router

↓

Service

↓

AIOrchestrator

↓

Provider

↓

Parser

↓

Response
```

No database writes.

---

# Phase 6 — Planning Engine

Current

```
RulePlanner
```

New

```
PlanningEngine

↓

RulePlanner

or

LLMPlanner
```

PlanningEngine decides which planner to use.

LLMPlanner

↓

Prompt Builder

↓

Provider

↓

Parser

↓

Schedule

If anything fails

↓

RulePlanner

---

# Phase 7 — Resource Module

Implement upload.

Flow

```
Upload

↓

Save File

↓

Save Resource

↓

Extract Text

↓

Update Resource

↓

AI Summary

↓

Update Resource
```

Uploading should never fail because AI failed.

---

# Phase 8 — Previous Paper Analysis

Flow

```
Upload PDF

↓

Extract Text

↓

Prompt Builder

↓

Provider

↓

JSON

↓

Parser

↓

Store Analysis
```

Expected JSON

```
topics[]

difficulty

frequency

confidence
```

---

# Phase 9 — Frontend Integration

Connect

- Explain button
- Quiz button
- Chat
- Upload
- Settings

Every frontend request should follow

```
React

↓

Axios

↓

FastAPI

↓

Router

↓

Service

↓

AI

↓

Response
```

---

# Phase 10 — Testing

Test each provider independently.

Test orchestrator.

Test parser.

Test endpoints.

Test schedule fallback.

Test upload failure.

---

# Final Verification

Mock Provider

✓ Explain

✓ Quiz

✓ Chat

✓ Schedule

Ollama

✓ Explain

✓ Chat

✓ Schedule

Cloud Providers

✓ Explain

✓ Chat

✓ Schedule

Resources

✓ Upload

✓ Summary

✓ Analysis

Planner

✓ Rule-based fallback

✓ AI planning