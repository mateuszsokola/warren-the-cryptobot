from typing import List
from rich.console import Console
from rich.prompt import Prompt
from tokens.base_token import BaseToken
from warren.core.token import Token


def choose_token_prompt(token_list: List[BaseToken], console: Console, prompt_message: str = "Choose token0"):
    choices = []
    for idx, token in enumerate(token_list):
        console.print(f"{idx}) {token.name}")
        choices.append(str(idx))

    idx = int(Prompt.ask(prompt_message, choices=choices))
    token = list(token_list)[idx]

    return token
