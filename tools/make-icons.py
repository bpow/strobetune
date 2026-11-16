# Usage: python3 tools/make-icons.py . 192 512  (pure stdlib, no Pillow needed)
import math, struct, sys, zlib

def render(size, ss=4):
    S = size * ss
    px = [[0.0, 0.0, 0.0] for _ in range(S * S)]
    # two LED rings inside the maskable safe zone (inner 80%)
    rings = [  # radius, dot radius, dots, periods, color
        (0.30, 0.034, 24, 4, (40, 255, 70)),
        (0.17, 0.030, 12, 3, (255, 40, 30)),
    ]
    for R, r, n, k, col in rings:
        for i in range(n):
            a = 2 * math.pi * i / n - math.pi / 2
            b = max(0.0, math.cos(2 * math.pi * k * i / n)) ** 2
            b = 0.12 + 0.88 * b
            cx, cy = 0.5 + R * math.cos(a), 0.5 + R * math.sin(a)
            x0, x1 = int((cx - r) * S), int((cx + r) * S) + 1
            y0, y1 = int((cy - r) * S), int((cy + r) * S) + 1
            for y in range(y0, y1):
                for x in range(x0, x1):
                    if ((x + .5) / S - cx) ** 2 + ((y + .5) / S - cy) ** 2 <= r * r:
                        p = px[y * S + x]
                        for c in range(3): p[c] = col[c] * b
    rows = bytearray()
    for y in range(size):
        rows.append(0)
        for x in range(size):
            acc = [0, 0, 0]
            for dy in range(ss):
                for dx in range(ss):
                    p = px[(y * ss + dy) * S + x * ss + dx]
                    for c in range(3): acc[c] += p[c]
            rows += bytes(min(255, round(v / ss / ss)) for v in acc)
    def chunk(t, d): return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d))
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', size, size, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(bytes(rows), 9)) + chunk(b'IEND', b''))

for size in map(int, sys.argv[2:]):
    open(f'{sys.argv[1]}/icon-{size}.png', 'wb').write(render(size))
