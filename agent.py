from dotenv import load_dotenv
load_dotenv()

import os

from anthropic import Anthropic


def read_local_file(filepath: str) -> str:
    """Return the text content of a small local text file."""
    with open(filepath, encoding="utf-8") as file:
        return file.read()


def main() -> None:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    question = input("What would you like Claude to find in a local text file? ")

    response = client.messages.create(
        model=os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5"),
        max_tokens=1024,
        tools=[
            {
                "name": "read_local_file",
                "description": "Read the text content of a small local .txt file.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "filepath": {
                            "type": "string",
                            "description": "The path to the local .txt file to read.",
                        }
                    },
                    "required": ["filepath"],
                },
            }
        ],
        tool_choice={"type": "any"},
        messages=[{"role": "user", "content": question}],
    )

    for block in response.content:
        if block.type == "tool_use":
            filepath = block.input["filepath"]
            print(f"Tool use block: {block}")
            print(f"Tool call made: {block.name}")
            print(f"Arguments used: {block.input}")
            file_text = read_local_file(filepath)
            print(f"Read {len(file_text)} characters from {filepath}")

            final_response = client.messages.create(
                model=os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5"),
                max_tokens=1024,
                tools=[
                    {
                        "name": "read_local_file",
                        "description": "Read the text content of a small local .txt file.",
                        "input_schema": {
                            "type": "object",
                            "properties": {
                                "filepath": {
                                    "type": "string",
                                    "description": "The path to the local .txt file to read.",
                                }
                            },
                            "required": ["filepath"],
                        },
                    }
                ],
                messages=[
                    {"role": "user", "content": question},
                    {"role": "assistant", "content": response.content},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": file_text,
                            }
                        ],
                    },
                ],
            )

            for final_block in final_response.content:
                if final_block.type == "text":
                    print(final_block.text)


if __name__ == "__main__":
    main()