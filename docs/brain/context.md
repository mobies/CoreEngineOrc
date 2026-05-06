# Antigravity Persistent Context - Core Engine Orchestrator

This file serves as the "memory" for the AI assistant (Antigravity) across different machines and sessions. **DO NOT DELETE.**

## Project Overview
- **Goal:** Build a multi-agent orchestrator for project automation.
- **Key Features:** Flexible API integration, Manager-Worker-Judge pattern, Portability.

## Current Status (2026-05-07)
- **Phase:** Fase 1 (Setup Awal)
- **Completed:** 
    - Git Initialization.
    - Initial Roadmap.
    - Security templates (.gitignore, .env.example).
- **Next Task:** Setup Python Environment & Base Dependencies.

## Architecture Decisions
- Use a "Memory-in-Files" strategy for cross-machine consistency.
- Standardize API calls through an Adapter pattern (Fase 2).

## Notes for Antigravity
When resuming this project on any machine:
1. Read `ROADMAP.md` for overall progress.
2. Read `docs/brain/context.md` (this file) for current state and logic.
3. Check `.env` for active API keys.
