from typing import List
from rich.console import Console
from rich.prompt import Prompt
from warren.core.token import Token


def choose_token_prompt(token_list: List[str], token_service: Token, console: Console, prompt_message: str = "Choose token0"):
    choices = []
    for idx, token in enumerate(token_list):
        console.print(f"{idx}) {token}")
        choices.append(str(idx))

    idx = int(Prompt.ask(prompt_message, choices=choices))
    token_name = list(token_list)[idx]

    return token_service.get_token_by_name(token_name)
