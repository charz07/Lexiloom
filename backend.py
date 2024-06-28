from openai import OpenAI

def prompt_ai(system_prompt:str, prompt:str, temperature = 0.0):
    messages = [{"role": "system", "content": system_prompt},{"role": "user", "content": prompt}]
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=temperature,
        max_tokens=4096
    )
    return response.choices[0].message.content.strip()