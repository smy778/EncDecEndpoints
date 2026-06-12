import base64
import hashlib

def u32(x):
    return x & 0xffffffff

def rotl(x, n):
    n &= 31
    if n == 0:
        return u32(x)
    return u32((x << n) | (x >> (32 - n)))

def imul(a, b):
    return ((a & 0xffffffff) * (b & 0xffffffff)) & 0xffffffff

def read_le32(b, p):
    return u32(
        b[p]
        | (b[p + 1] << 8)
        | (b[p + 2] << 16)
        | (b[p + 3] << 24)
    )

def write_le32(b, p, x):
    x = u32(x)
    b[p] = x & 0xff
    b[p + 1] = (x >> 8) & 0xff
    b[p + 2] = (x >> 16) & 0xff
    b[p + 3] = (x >> 24) & 0xff

def b64(s):
    s = s.replace("-", "+").replace("_", "/")
    s += "=" * (-len(s) % 4)
    return bytearray(base64.b64decode(s))

def build(w, m):
    s = [0] * 4096

    x = u32(
        w[m & 3]
        ^ u32(imul(m, 0x9e3779b1) - 0x61c8864f)
        ^ 0xa5a5a5a5
    )

    y = 0x85ebca6b

    for i in range(4096):
        x = u32(x + y + w[i & 3])
        x = u32(x ^ (x << 13))
        x = u32(x ^ (x >> 17))
        x = u32(x ^ (x << 5))

        s[i] = u32(
            x
            + imul(i ^ m, 0xc2b2ae35)
            + rotl(w[(i + m) & 3], i + m)
        )

        y = u32(y - 0x7a143595)

    return s

def mix(w, s, m, n):
    lo = n & 0xffffffff
    hi = (n >> 32) & 0xffffffff

    a = u32(w[0] ^ imul(m + 1, 0x27d4eb2d) ^ lo)
    b = u32(w[2] ^ rotl(lo, m + 5))
    c = u32(hi ^ (w[1] ^ 0x165667b1))
    d = u32(w[3] ^ rotl(u32(lo ^ hi), m + 11))

    y = 2667

    for r in range(1, 9):
        v = s[(imul(c, 2481) ^ rotl(b, r) ^ y ^ a) & 4095]
        op = ((r + m - 1) & 7) - 1

        if op == -1:
            a = rotl(u32(a + d + v), 5)
            c = u32(imul(a ^ c, 0x9e3779b1) + b)

        elif op == 0:
            b = rotl(u32(b ^ c ^ v), 11)
            d = u32(imul(b ^ a, 0x85ebca6b) + d)

        elif op == 1:
            c = rotl(u32(b + c + v), 17)
            a = u32(imul(c ^ d, 0xc2b2ae35) ^ a)

        elif op == 2:
            d = rotl(u32(a ^ d ^ v), 23)
            b = u32(imul(d ^ c, 0x27d4eb2d) + b)

        elif op == 3:
            a = u32(imul(a ^ v, 0x165667b1) + rotl(b, 7))
            d = u32(rotl(u32(a + c), 13) ^ d)

        elif op == 4:
            c = u32(imul(u32(v + c), 0xd3a2646c) ^ rotl(d, 9))
            b = u32(rotl(c ^ a, 19) + b)

        elif op == 5:
            b = u32(imul(b ^ v, 0xfd7046c5) + rotl(a, 3))
            c = u32(rotl(u32(b + d), 15) ^ c)

        else:
            d = u32(imul(u32(d + v), 0xb55a4f09) ^ rotl(c, 21))
            a = u32(rotl(d ^ b, 27) + a)

        y += 2667

    return lo, hi, a, c, b, d

def diff(h, d):
    q = d >> 3
    r = d & 7

    for i in range(q):
        if h[i]:
            return False

    return r == 0 or (h[q] >> (8 - r)) == 0

def solve_stage1(data):
    b = b64(data["w"])
    d = b[5]
    m = b[6]

    w = [
        read_le32(b, 8),
        read_le32(b, 12),
        read_le32(b, 16),
        read_le32(b, 20),
    ]

    s = build(w, m)

    msg = bytearray(42)
    msg[0:16] = b[8:24]
    msg[40] = 2
    msg[41] = m

    n = 0

    while True:
        lo, hi, a, c, b2, d2 = mix(w, s, m, n)

        write_le32(msg, 16, lo)
        write_le32(msg, 20, hi)
        write_le32(msg, 24, a)
        write_le32(msg, 28, c)
        write_le32(msg, 32, b2)
        write_le32(msg, 36, d2)

        h = hashlib.sha256(msg).digest()

        if diff(h, d):
            return f"m2.{n:x}"

        n += 1