import os

def load_prompt(prompt_filename: str) -> str:
    """Loads a system prompt from the ai/prompts directory."""
    base_dir = os.path.dirname(__file__)
    prompt_path = os.path.join(base_dir, 'prompts', prompt_filename)
    
    with open(prompt_path, 'r', encoding='utf-8') as file:
        return file.read()
