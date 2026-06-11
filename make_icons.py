#!/usr/bin/env python3
# Генератор иконок без внешних зависимостей: рисует ключ 木 на красном фоне.
import struct, zlib, math

# Штрихи иероглифа 木 в координатах [0..1] (x вправо, y вниз): (x1,y1,x2,y2)
CX, CY = 0.5, 0.40
STROKES = [
    (0.5, 0.10, 0.5, 0.92),   # вертикаль
    (0.16, 0.40, 0.84, 0.40),  # горизонталь
    (0.5, 0.44, 0.18, 0.88),   # левая ветвь
    (0.5, 0.44, 0.82, 0.88),   # правая ветвь
]
HALF = 0.052      # половина толщины штриха (доля размера)
INK = (255, 255, 255)
TOP = (0xEC, 0x5C, 0x46)   # верх градиента
BOT = (0xCE, 0x39, 0x28)   # низ градиента

def dist_seg(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    L2 = dx*dx + dy*dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px-x1)*dx + (py-y1)*dy)/L2))
    qx, qy = x1 + t*dx, y1 + t*dy
    return math.hypot(px-qx, py-qy)

def render(size):
    half = HALF
    aa = 1.4 / size            # ширина сглаживания в долях
    rows = bytearray()
    for j in range(size):
        rows.append(0)         # filter byte
        v = j/(size-1)
        br = int(TOP[0]+(BOT[0]-TOP[0])*v)
        bg = int(TOP[1]+(BOT[1]-TOP[1])*v)
        bb = int(TOP[2]+(BOT[2]-TOP[2])*v)
        py = (j+0.5)/size
        for i in range(size):
            px = (i+0.5)/size
            d = min(dist_seg(px, py, *s) for s in STROKES)
            cov = (half - d)/aa + 0.5
            cov = 0.0 if cov < 0 else (1.0 if cov > 1 else cov)
            r = int(br + (INK[0]-br)*cov)
            g = int(bg + (INK[1]-bg)*cov)
            b = int(bb + (INK[2]-bb)*cov)
            rows += bytes((r, g, b))
    raw = bytes(rows)
    def chunk(typ, data):
        c = typ + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xffffffff)
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)  # 8-bit RGB
    idat = zlib.compress(raw, 9)
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")

for name, size in [("icon-512.png",512), ("icon-192.png",192), ("apple-touch-icon.png",180), ("favicon-32.png",32)]:
    open(name, "wb").write(render(size))
    print("сгенерирован", name, size)
