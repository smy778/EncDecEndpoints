# Semi-optimized proof of concept solver.
# Please reference challenge/byse_optimized.js for js-native pow solver if porting to another language. It's more efficient.

import numpy as np
from numba import njit, prange

BLOCKS = 512
MASK = BLOCKS - 1
ROUNDS = 2
MUL_A = np.uint32(2654435761)
MUL_B = np.uint32(2246822519)

@njit(inline="always")
def _rot(value, shift):
    value = np.uint32(value)
    return np.uint32((value << shift) | (value >> (32 - shift)))

@njit(inline="always")
def _mul(value, factor):
    return np.uint32(np.uint64(value) * np.uint64(factor))

@njit(inline="always")
def _mix(a, b, c, d):
    a = np.uint32(a + b)
    d = _rot(np.uint32(d ^ a), 16)

    c = np.uint32(c + d)
    b = _rot(np.uint32(b ^ c), 12)

    a = np.uint32(a + b)
    d = _rot(np.uint32(d ^ a), 8)

    c = np.uint32(c + d)
    b = _rot(np.uint32(b ^ c), 7)

    return a, b, c, d

@njit
def _prefix_state(prefix):
    a = np.uint32(1779033703)
    b = np.uint32(3144134277)
    c = np.uint32(1013904242)
    d = np.uint32(2773480762)

    for byte in prefix:
        a = np.uint32(a + np.uint32(byte))
        a = _rot(a, 7)
        a, b, c, d = _mix(a, b, c, d)

    return a, b, c, d

@njit(inline="always")
def _process_counter(a, b, c, d, counter):
    if counter == 0:
        a = np.uint32(a + np.uint32(48))
        a = _rot(a, 7)
        return _mix(a, b, c, d)

    divisor = 1
    value = counter

    while value >= 10:
        value //= 10
        divisor *= 10

    while divisor:
        digit = counter // divisor
        counter -= digit * divisor
        divisor //= 10

        a = np.uint32(a + np.uint32(48 + digit))
        a = _rot(a, 7)
        a, b, c, d = _mix(a, b, c, d)

    return a, b, c, d

@njit(inline="always")
def _clz32(value):
    if value == 0:
        return 32

    count = 0
    bit = np.uint32(0x80000000)

    while (value & bit) == 0:
        count += 1
        bit >>= 1

    return count

@njit
def _candidate_valid(counter, difficulty, pa, pb, pc, pd):
    a, b, c, d = _process_counter(pa, pb, pc, pd, counter)

    for _ in range(8):
        a, b, c, d = _mix(a, b, c, d)

    table = np.empty(BLOCKS, dtype=np.uint32)

    for i in range(BLOCKS):
        a, b, c, d = _mix(a, b, c, d)
        table[i] = np.uint32(a ^ c)

    for _ in range(ROUNDS):
        for index in range(BLOCKS):
            table_index = int(table[index] & np.uint32(MASK))

            value = np.uint32(table[index] + table[table_index])
            value = _rot(value, 13)

            next_value = table[(index + 1) & MASK]
            value = np.uint32(value ^ _mul(next_value, MUL_A))

            table[index] = value

            a = np.uint32(a ^ value)
            a, b, c, d = _mix(a, b, c, d)

    remaining = difficulty
    width = BLOCKS // 8

    for i in range(8):
        a, b, c, d = _mix(a, b, c, d)

        value = a
        offset = i * width

        for index in range(width):
            table_value = table[offset + index]

            value = np.uint32(value + table_value)
            value = _rot(value, 5)
            value = np.uint32(value ^ _mul(table_value, MUL_B))

        output = np.uint32(value ^ c)
        zero_bits = _clz32(output)

        if zero_bits >= remaining:
            return True

        if zero_bits < 32:
            return False

        remaining -= 32

    return remaining <= 0

@njit(parallel=True)
def _solve_batch(start, size, difficulty, pa, pb, pc, pd):
    hits = np.zeros(size, dtype=np.uint8)

    for i in prange(size):
        counter = start + i

        if _candidate_valid(counter, difficulty, pa, pb, pc, pd):
            hits[i] = 1

    return hits

def solve_pow(data):
    nonce = data["pow_nonce"]
    difficulty = int(data["pow_difficulty"])

    prefix = np.frombuffer((nonce + ":").encode("latin1"), dtype=np.uint8)
    pa, pb, pc, pd = _prefix_state(prefix)

    batch_size = 1024
    start = 0

    while True:
        hits = _solve_batch(start, batch_size, difficulty, pa, pb, pc, pd)
        indexes = np.flatnonzero(hits)

        if indexes.size:
            counter = start + int(indexes[0])
            return str(counter)

        start += batch_size