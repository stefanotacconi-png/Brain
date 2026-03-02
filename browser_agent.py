"""
Browser agent — Claude navigates the internet via Playwright MCP.

Usage:
    python browser_agent.py "Go to news.ycombinator.com and summarize the top 5 stories"
    python browser_agent.py  # interactive mode
"""

import sys
import anyio
from dotenv import load_dotenv
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage, AssistantMessage, TextBlock

load_dotenv()

PLAYWRIGHT_MCP = {
    "command": "npx",
    "args": ["@playwright/mcp@latest"],
}


async def run(prompt: str) -> None:
    print(f"\nTask: {prompt}\n{'-' * 60}")

    async for message in query(
        prompt=prompt,
        options=ClaudeAgentOptions(
            mcp_servers={"playwright": PLAYWRIGHT_MCP},
            permission_mode="acceptEdits",
        ),
    ):
        if isinstance(message, ResultMessage):
            print(f"\nResult:\n{message.result}")
        elif isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock) and block.text.strip():
                    print(block.text, end="", flush=True)


def main() -> None:
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        print("Browser Agent — Claude can navigate the internet.")
        print("Type your task and press Enter. Ctrl+C to exit.\n")
        try:
            prompt = input("Task: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nBye.")
            return

    if not prompt:
        print("No task provided.")
        return

    anyio.run(run, prompt)


if __name__ == "__main__":
    main()
