# Claude Agent: Feature Brainstorming Guide

This document outlines a structured process for exploring features and improvements through collaborative dialogue before implementation planning.

## Core Process

The workflow spans four phases:

**Phase 0** assesses whether brainstorming is actually needed. If requirements are already detailed with acceptance criteria and defined scope, the agent suggests jumping directly to planning.

**Phase 1** builds understanding through lightweight repository research and one-at-a-time questioning. The agent asks broad questions first (purpose, users), then narrows focus to constraints and success criteria.

**Phase 2** presents 2-3 concrete approaches with pros/cons for each, leading with a recommendation. The agent applies YAGNI principles—favoring simpler solutions.

**Phase 3** captures decisions in a brainstorm document at `docs/brainstorms/YYYY-MM-DD-<topic>-brainstorm.md`. Critically, any open questions must be resolved with the user before proceeding.

**Phase 4** offers multiple next steps: refine the document, proceed to planning, share to Proof for collaboration, ask deeper questions, or defer.

## Key Principles

The process intentionally separates **WHAT to build** (brainstorming) from **HOW to build it** (planning). Questions should be posed individually to avoid overwhelming users. The agent never writes code during brainstorming—only explores and documents decisions.

This structure ensures collaborative exploration precedes detailed implementation planning.
