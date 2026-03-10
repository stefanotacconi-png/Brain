# Claude — Brain Project

## Memory System
At the start of every session, read these files to load full context:

- `/Users/stefanotacconi/Documents/Vault Brain/Memory/about-me.md` — who Stefano is
- `/Users/stefanotacconi/Documents/Vault Brain/Memory/projects.md` — active projects & status
- `/Users/stefanotacconi/Documents/Vault Brain/Memory/decisions.md` — key decisions log
- `/Users/stefanotacconi/Documents/Vault Brain/Memory/preferences.md` — working style & conventions

At the end of every session, automatically update the relevant memory files — no need to be asked.
Update rules:
- `about-me.md` — if role, tools, or company context changed
- `projects.md` — update status of touched projects, add new ones, remove completed ones
- `decisions.md` — log any significant decision made during the session (date · decision · rationale)
- `preferences.md` — if a new working convention emerged or an existing one was corrected

Only update files that actually changed. Always append the `Last updated` date at the bottom.

## Folder Structure

```
/Users/stefanotacconi/Documents/Brain/       ← Claude Code project
  Skills/                                     ← GTM automation skills & scripts
    CLAUDE.md                                 ← GTM-specific context
    .claude/commands/                         ← slash commands / skills
    output/                                   ← all generated outputs
    ICP/                                      ← scoring & analytics

/Users/stefanotacconi/Documents/Vault Brain/ ← Obsidian vault (memory & notes)
  Memory/                                     ← Claude's persistent memory
  GTM/                                        ← sales knowledge base
  Notes/                                      ← general notes
```

## GTM Context
For outbound GTM work, also read `Skills/CLAUDE.md` — it contains ICP definitions,
campaign knowledge, API keys, and tool conventions.
