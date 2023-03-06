from typing import List


NULL_ADDRESS = "0x0000000000000000000000000000000000000000"


def fill_array_with_null_addresses(array: List[str] = [], len: int = 9) -> List[str]:
    result = [*array]

    for _ in range(len(array), len, 1):
        result.append(NULL_ADDRESS)

    return result
