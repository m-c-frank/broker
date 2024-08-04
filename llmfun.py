def define_russian_word(russian_word: str):
    prompt = f"Define the Russian word '{russian_word}' in English with a maximum of 32 words. Explain its nuances."
    messages=[
    {
        'role': 'system',
        'content': 'you are dostoyevsky. and you do an original translation. not these superficial ones. you are authentic. you even go into ontology, etymology and examples'
    },
    {
        'role': 'user',
        'content': prompt
    },
    ]
    return messages

def ollama_define_russian_word(russian_word):
    import ollama
    response = ollama.chat(model='llama3', messages=define_russian_word(russian_word))
    definition = response['message']['content']
    return f"**{russian_word}**: {definition}"

def openai_define_russian_word(russian_word):
    from openai import OpenAI
    from llmfun import openai_define_russian_word

    import os
    import dotenv
    dotenv.load_dotenv()
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=define_russian_word(russian_word),
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    print(response)
    return response.choices[0].message.content