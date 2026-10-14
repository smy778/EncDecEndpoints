// Native JS solver if you need it.

const BLOCKS = 512;
const MASK = BLOCKS - 1;
const ROUNDS = 2;
const MUL_A = 2654435761;
const MUL_B = 2246822519;

function rot(value, shift) {
    return (value << shift | value >>> (32 - shift)) >>> 0;
}

function mul(value, factor) {
    return Math.imul(value, factor) >>> 0;
}

function mix(state) {
    state[0] = (state[0] + state[1]) >>> 0;
    state[3] = rot(state[3] ^ state[0], 16);

    state[2] = (state[2] + state[3]) >>> 0;
    state[1] = rot(state[1] ^ state[2], 12);

    state[0] = (state[0] + state[1]) >>> 0;
    state[3] = rot(state[3] ^ state[0], 8);

    state[2] = (state[2] + state[3]) >>> 0;
    state[1] = rot(state[1] ^ state[2], 7);
}

function hash(bytes) {
    const state = new Uint32Array([
        1779033703,
        3144134277,
        1013904242,
        2773480762
    ]);

    for (let i = 0; i < bytes.length; i++) {
        state[0] = (state[0] + bytes[i]) >>> 0;
        state[0] = rot(state[0], 7);
        mix(state);
    }

    for (let i = 0; i < 8; i++) {
        mix(state);
    }

    const table = new Uint32Array(BLOCKS);

    for (let i = 0; i < BLOCKS; i++) {
        mix(state);
        table[i] = (state[0] ^ state[2]) >>> 0;
    }

    for (let round = 0; round < ROUNDS; round++) {
        for (let index = 0; index < BLOCKS; index++) {
            const tableIndex = table[index] & MASK;

            let value = (table[index] + table[tableIndex]) >>> 0;
            value = rot(value, 13);
            value = (
                value ^
                mul(table[(index + 1) & MASK], MUL_A)
            ) >>> 0;

            table[index] = value;

            state[0] = (state[0] ^ value) >>> 0;
            mix(state);
        }
    }

    const out = new Uint32Array(8);
    const width = BLOCKS / 8;

    for (let i = 0; i < 8; i++) {
        mix(state);

        let value = state[0];
        const offset = i * width;

        for (let index = 0; index < width; index++) {
            const tableValue = table[offset + index];

            value = (value + tableValue) >>> 0;
            value = rot(value, 5);
            value = (
                value ^
                mul(tableValue, MUL_B)
            ) >>> 0;
        }

        out[i] = (value ^ state[2]) >>> 0;
    }

    return out;
}

function latin1Bytes(value) {
    const out = new Uint8Array(value.length);

    for (let i = 0; i < value.length; i++) {
        out[i] = value.charCodeAt(i) & 255;
    }

    return out;
}

function leadingZeros(value) {
    let total = 0;

    for (let i = 0; i < value.length; i++) {
        const item = value[i];

        if (item === 0) {
            total += 32;
            continue;
        }

        return total + Math.clz32(item);
    }

    return total;
}

export function solve_pow(data) {
    const nonce = data.pow_nonce;
    const difficulty = data.pow_difficulty;
    const prefix = `${nonce}:`;

    for (let counter = 0; ; counter++) {
        const bytes = latin1Bytes(prefix + counter);

        if (leadingZeros(hash(bytes)) >= difficulty) {
            return String(counter);
        }
    }
}