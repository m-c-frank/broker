import http.client
import json
import re


def api(messages, model="granite-code:3b", save=True) -> str:
    conn = http.client.HTTPConnection("localhost", 11434)

    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": messages
    }
    json_data = json.dumps(data)

    conn.request("POST", "/v1/chat/completions",
                 body=json_data, headers=headers)

    response = conn.getresponse()
    response_data = response.read().decode("utf-8")

    formatted_messages = json.dumps(messages, indent=4, ensure_ascii=False)

    response_message = json.loads(response_data)[
        "choices"][0]["message"]["content"]

    lines = [
        "# prompt",
        "## messages",
        formatted_messages,
        "## response",
        response_message
    ]

    final_output = "\n".join(lines)

    return final_output

llm = api

if __name__ == "__main__":
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": "Hello!"
        }
    ]
    model = "granite-code:3b"
    response = api(messages, model)
    print(response)

    import os
    listdir_result = os.listdir()

    messages = prompt_create_index("agent", listdir_result)
    response = api(messages, model)
    print(response)
