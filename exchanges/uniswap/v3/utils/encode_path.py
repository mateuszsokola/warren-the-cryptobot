from typing import List


FEE_SIZE = 3


def encode_path(path: List[str], fees: List[int]) -> str:
    assert len(path) == len(fees) + 1

    encoded = "0x"

    for i in range(0, len(fees), 1):
        # 20 byte encoding of the address
        encoded += path[i][2:]
        # 3 byte encoding of the fee
        encoded += str(hex(fees[i])[2:]).zfill(2 * FEE_SIZE)

    # encode the final token
    encoded += path[len(path) - 1][2:]

    return encoded.lower()
