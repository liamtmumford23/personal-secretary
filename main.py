import json
import anthropic
from dotenv import load_dotenv

load_dotenv()

from prompts import SYSTEM_PROMPT
from tools import TOOLS, run_tool

MODEL = "claude-sonnet-4-6"

client = anthropic.Anthropic()


def run_agent(messages: list) -> str:
    """Run the agentic loop until stop_reason is 'end_turn'. Returns final text."""
    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            tools=TOOLS,
            messages=messages,
        )

        # Append assistant turn
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            # Return the final text block
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return ""

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue

                # Show the tool call to the user
                print(f"[calling {block.name}({json.dumps(block.input, ensure_ascii=False)})]")

                result = run_tool(block.name, block.input)
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    }
                )

            messages.append({"role": "user", "content": tool_results})

        else:
            # Unexpected stop reason — return whatever text we have
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return f"(stopped: {response.stop_reason})"


def main():
    print("Personal Secretary — type 'quit' to exit\n")
    messages = []

    while True:
        try:
            user_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            break

        messages.append({"role": "user", "content": user_input})
        reply = run_agent(messages)
        print(f"\n{reply}\n")


if __name__ == "__main__":
    main()
