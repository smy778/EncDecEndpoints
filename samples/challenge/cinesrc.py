import base64
import hashlib
import struct
import json

K = (
    0x46C6C721, 0x4230C311, 0x18223A1D, 0x56389BA7,
    0xD4A87103, 0x07CB9E2F, 0x73085F9D, 0xD2396A1F,
    0x23AE5ADD, 0x4646C48F, 0x0F4E0903, 0x808F5F31,
    0x953D4E07, 0x7E238FFF, 0x634595DF, 0xCB5E4301,
)

PERMUTATIONS = (
    (3, 5, 1, 0, 2, 4),
    (2, 0, 4, 5, 3, 1),
    (1, 4, 5, 3, 0, 2),
    (2, 0, 1, 5, 4, 3),
    (4, 2, 1, 0, 3, 5),
    (5, 0, 2, 1, 3, 4),
    (4, 5, 1, 0, 3, 2),
    (4, 0, 3, 5, 1, 2),
)

SCHEDULES = (
    (0, 7, 6, 3, 2, 1, 5, 4, 0, 2, 4, 6, 5, 1, 7, 3),
    (5, 2, 1, 3, 0, 4, 6, 7, 4, 1, 0, 7, 3, 6, 5, 2),
    (4, 0, 2, 1, 5, 7, 6, 3, 2, 6, 0, 7, 4, 3, 5, 1),
    (5, 4, 7, 0, 2, 3, 1, 6, 5, 1, 4, 0, 7, 2, 3, 6),
    (4, 7, 0, 2, 1, 6, 5, 3, 6, 1, 3, 2, 0, 7, 4, 5),
    (0, 7, 2, 6, 3, 4, 5, 1, 6, 5, 0, 2, 7, 1, 4, 3),
    (0, 4, 5, 3, 1, 7, 2, 6, 3, 7, 5, 6, 1, 0, 2, 4),
    (7, 6, 0, 4, 2, 5, 1, 3, 7, 5, 3, 4, 2, 6, 0, 1),
)

PROFILES = {
    0: (12, 15),
    1: (16, 17),
}

def u32(x):
    return x & 0xFFFFFFFF

def rotl(x, n):
    x &= 0xFFFFFFFF
    n &= 31
    return x if n == 0 else u32((x << n) | (x >> (32 - n)))

def imul(a, b):
    return u32(a * b)

def b64(s):
    return bytearray(base64.urlsafe_b64decode(s + "=" * (-len(s) % 4)))

def parse(w):
    c = b64(w)

    if len(c) != 32:
        raise ValueError("invalid CSP4 challenge length")

    if c[16:20] != b"}\xbd\xd2C" or c[20] != 4 or c[28:32] != b"CSP4":
        raise ValueError("invalid CSP4 challenge")

    mode, diff, var, rnd, m_b, s_i, p_i = c[21:28]

    if not 1 <= diff <= 30:
        raise ValueError("invalid difficulty")

    if var > 7 or s_i > 7 or p_i > 7:
        raise ValueError("invalid CSP4 selector")

    if PROFILES.get(mode) != (rnd, m_b):
        raise ValueError("invalid CSP4 profile")

    w = struct.unpack_from("<4I", c)
    return c, w, mode, diff, var, rnd, m_b, s_i, p_i

def build(w, var, s_i, m_b):
    size = 1 << m_b
    s = [0] * size

    x = u32(w[var & 3] ^ K[s_i] ^ imul(K[8 + s_i], var + 1))
    y = u32(w[(var + 1) & 3] ^ K[15 - s_i])

    for i in range(size):
        x = u32(w[(i + s_i) & 3] + x + imul(K[(i + var) & 15], i + 1))
        x = u32(x ^ (x << 13))
        x = u32(x ^ (x >> 17))
        x = u32(x ^ (x << 5))

        y = rotl(imul(K[(i + 9) & 15], i + 3) ^ y ^ x, i + var + s_i)

        s[i] = u32(
            imul(K[(i + 5) & 15], i ^ var)
            ^ rotl(w[(i + var) & 3], i + s_i)
            ^ x
            ^ y
        )

    return s

def mix(w, s, var, rnd, m_b, s_i, p_i, n):
    mask = (1 << m_b) - 1
    lo = n & 0xFFFFFFFF
    hi = n >> 32

    a = u32(w[0] ^ K[var] ^ lo)
    b = u32(rotl(lo, var + 7) ^ w[2])
    c = u32(w[1] ^ K[8 + s_i] ^ hi)
    d = u32(rotl(lo ^ hi, s_i + 11) ^ w[3])
    e = u32(K[s_i + var] ^ lo ^ hi)
    f = u32(K[15 - var] ^ w[s_i & 3])

    sch = SCHEDULES[s_i]

    for r in range(rnd):
        i1 = u32(rotl(b, r + 1) ^ imul(K[r & 15], f) ^ e ^ a) & mask
        v1 = s[i1]

        i2 = u32(rotl(e, var + r + 3) ^ imul(K[(r + 7) & 15], d) ^ c ^ v1) & mask
        op = sch[r]

        if op == 0:
            a = rotl(u32(a + d + v1), 5)
            c = u32(imul(c ^ f ^ a, 1187432225) + b)
        elif op == 1:
            b = rotl(c ^ e ^ b ^ v1, 11)
            d = u32(imul(b ^ a, 1110491921) + d)
        elif op == 2:
            c = rotl(u32(c + b + v1), 17)
            a = u32(imul(d ^ f ^ c, 404896285) ^ a)
        elif op == 3:
            d = rotl(a ^ d ^ v1, 23)
            b = u32(imul(c ^ e ^ d, 1446550439) + b)
        elif op == 4:
            a = u32(imul(a ^ e ^ v1, -727158525) + rotl(b, 7))
            d = u32(rotl(u32(c + f + a), 13) ^ d)
        elif op == 5:
            c = u32(imul(u32(c + f + v1), 130784815) ^ rotl(d, 9))
            b = u32(rotl(a ^ e ^ c, 19) + b)
        elif op == 6:
            b = u32(imul(b ^ f ^ v1, 1929928605) + rotl(a, 3))
            c = u32(rotl(u32(d + e + b), 15) ^ c)
        else:
            d = u32(imul(u32(d + e + v1), -767989217) ^ rotl(c, 21))
            a = u32(rotl(b ^ f ^ d, 27) + a)

        v2 = s[i2]

        if ((f ^ r ^ v1) & 1) == 0:
            f = rotl(u32(v2 + f + a), r + 5)
            e = u32(imul(K[8 + op], v2 ^ e ^ f) + d)
        else:
            e = rotl(v2 ^ e ^ b, r + 9)
            f = u32(imul(K[(op + 11) & 15], u32(v2 + f + e)) ^ c)

    v = (a, c, b, d, f, e)
    return tuple(v[i] for i in PERMUTATIONS[p_i])

def diff(h, bits):
    b, r = divmod(bits, 8)

    if any(h[:b]):
        return False

    return r == 0 or h[b] >> (8 - r) == 0

def solve_stage1(data, seed):
    seed = bytes.fromhex(seed)

    c, w, mode, d, var, rnd, m_b, s_i, p_i = parse(data["w"])
    s = build(w, var, s_i, m_b)

    msg = bytearray(88)
    msg[24:40] = c[:16]

    cfg = m_b ^ 0x6B29
    msg[48:56] = bytes((4, mode, var, s_i, p_i, rnd, cfg & 0xFF, cfg >> 8))
    msg[56:88] = seed

    n = 0

    while True:
        m = mix(w, s, var, rnd, m_b, s_i, p_i, n)

        struct.pack_into("<6I", msg, 0, *m)
        struct.pack_into("<Q", msg, 40, n)

        if diff(hashlib.sha256(msg).digest(), d):
            return f"m4.{n:x}"

        n += 1

def solve_stage2(data):
    target = data["pack"][0][::-1]
    salt = data["pack"][3][::-1]
    r = data["pack"][4][::-1]

    decode = lambda s: base64.urlsafe_b64decode(s + "=" * (-len(s) % 4)).decode()

    body = decode(r.split(".")[1])
    payload = decode(body.split(".", 1)[1])
    difficulty = json.loads(payload)["d"]

    width = (difficulty + 3) // 4

    for counter in range(1 << difficulty):
        key = format(counter, "x").zfill(width)
        digest = hashlib.sha256((salt + key).encode()).hexdigest()

        if digest == target:
            return key

    raise RuntimeError("no solution found")