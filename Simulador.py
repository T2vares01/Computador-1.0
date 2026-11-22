#!/usr/bin/env python3
"""MiniCPU-4: simulador em Python.

Todas as portas do computador são células do circuito revisado (A, B, P, N).
Entrada: programa (ROM de 8 posições) e clock.  Saída: acumulador (ACC), PC e instrução.
Uso:
    python3 minicpu4_simulador.py                 (modo interativo)
    python3 minicpu4_simulador.py programa.txt    (carrega um programa, uma instrução por linha)
"""
import sys, time

# ---------------- célula revisada ----------------
def cell(a, b, p, n, nt=0):
    g2 = a | b
    o = (a & b & (1 - p) & n) | (g2 & p & (1 - n)) | ((1 - (a ^ b)) & p & n) | (1 - (g2 | p | n))
    return 1 - o if nt else o

# porta -> (P, N, NOT no final)
MAP = {"AND": (0, 1, 0), "OR": (1, 0, 0), "NOR": (0, 0, 0), "NOT": (0, 0, 0),
       "NAND": (0, 1, 1), "XOR": (1, 1, 1)}

# ---------------- netlist do computador ----------------
G, _c = [], [0]
def _new():
    _c[0] += 1
    return "n%d" % _c[0]
def g(t, a, b=None, out=None):
    out = out or _new()
    G.append((t, a, a if b is None else b, out))
    return out
NOT = lambda a, o=None: g("NOT", a, None, o)
AND = lambda a, b: g("AND", a, b)
OR = lambda a, b: g("OR", a, b)
XOR = lambda a, b: g("XOR", a, b)
NOR = lambda a, b: g("NOR", a, b)
NAND = lambda a, b, o=None: g("NAND", a, b, o)
def ORn(l):
    x = l[0]
    for y in l[1:]: x = OR(x, y)
    return x
def ANDn(l):
    x = l[0]
    for y in l[1:]: x = AND(x, y)
    return x
mux = lambda s, ns, a0, a1: OR(AND(a0, ns), AND(a1, s))
def latch(d, e):
    nd = NOT(d); s = NAND(d, e); r = NAND(nd, e)
    q, qb = _new(), _new()
    NAND(s, qb, q); NAND(r, q, qb)
    return q
def ff(d, out):                       # flip-flop mestre-escravo
    m = latch(d, "nclk")
    nd = NOT(m); s = NAND(m, "CLK"); r = NAND(nd, "CLK"); qb = _new()
    NAND(s, qb, out); NAND(r, out, qb)

NOT("CLK", "nclk")
pc = ["pc0", "pc1", "pc2"]; npc = [NOT(x) for x in pc]
sel = [ANDn([pc[i] if (w >> i) & 1 else npc[i] for i in range(3)]) for w in range(8)]
I = [ORn([AND(sel[w], "SW%d_%d" % (w, k)) for w in range(8)]) for k in range(8)]
imm, op = I[:4], I[4:]
nop = [NOT(x) for x in op]
D = {k: ANDn([op[i] if (k >> i) & 1 else nop[i] for i in range(4)]) for k in (1, 2, 3, 4, 5, 6, 7, 8, 15)}
nD1 = NOT(D[1]); acc = ["a0", "a1", "a2", "a3"]
Ae = [AND(a, nD1) for a in acc]
Be = [XOR(x, D[3]) for x in imm]
car = D[3]; SUM = []
for i in range(4):
    x = XOR(Ae[i], Be[i]); SUM.append(XOR(x, car))
    if i < 3: car = OR(AND(Ae[i], Be[i]), AND(x, car))
AN = [AND(Ae[i], Be[i]) for i in range(4)]
OU = [OR(Ae[i], Be[i]) for i in range(4)]
XO = [XOR(Ae[i], Be[i]) for i in range(4)]
sA = NOR(OR(D[4], D[5]), D[6])
R = [ORn([AND(SUM[i], sA), AND(AN[i], D[4]), AND(OU[i], D[5]), AND(XO[i], D[6])]) for i in range(4)]
WE = ORn([D[k] for k in (1, 2, 3, 4, 5, 6)]); nWE = NOT(WE)
for i in range(4): ff(AND(mux(WE, nWE, acc[i], R[i]), "RST_N"), acc[i])
Z = NOR(OR("a0", "a1"), OR("a2", "a3"))
LD = OR(D[7], AND(D[8], Z)); nLD = NOT(LD); HN = NOT(D[15])
c0 = AND("pc0", HN); c1 = AND("pc1", c0)
for i, s in enumerate((XOR("pc0", HN), XOR("pc1", c0), XOR("pc2", c1))):
    ff(AND(mux(LD, nLD, s, imm[i]), "RST_N"), pc[i])

# ---------------- simulação ----------------
class CPU:
    def __init__(self):
        self.rom = [0] * 8
        self.v = {}
        self.ciclos = 0
        self.reset()
    def settle(self):
        v = self.v
        for _ in range(600):
            mudou = False
            for t, a, b, o in G:
                p, n, nt = MAP[t]
                r = cell(v.get(a, 0), v.get(b, 0), p, n, nt)
                if v.get(o) != r: v[o] = r; mudou = True
            if not mudou: return
        raise RuntimeError("circuito não estabilizou")
    def carregar_rom(self):
        for w in range(8):
            for k in range(8): self.v["SW%d_%d" % (w, k)] = (self.rom[w] >> k) & 1
    def reset(self):
        self.v = {"CLK": 0, "RST_N": 0}
        self.carregar_rom(); self.settle()
        for _ in range(2): self.clock()
        self.v["RST_N"] = 1; self.settle(); self.ciclos = 0
    def clock(self):
        self.v["CLK"] = 1; self.settle(); self.v["CLK"] = 0; self.settle()
    def passo(self):
        self.clock(); self.ciclos += 1
    @property
    def pc(self): return sum((self.v.get("pc%d" % i, 0)) << i for i in range(3))
    @property
    def acc(self): return sum((self.v.get("a%d" % i, 0)) << i for i in range(4))
    @property
    def parado(self): return (self.rom[self.pc] >> 4) == 15

# ---------------- montador ----------------
NM = ["NOP", "LDI", "ADD", "SUB", "AND", "OR", "XOR", "JMP", "JZ"] + [None] * 6 + ["HLT"]
def dis(b):
    o, n = b >> 4, b & 15
    if NM[o] is None: return "???"
    return NM[o] if o in (0, 15) else "%s %d" % (NM[o], n)
def montar(txt):
    txt = txt.split(";")[0].strip().upper()
    if not txt: return 0
    if len(txt) == 2 and all(c in "0123456789ABCDEF" for c in txt): return int(txt, 16)
    p = txt.split()
    if p[0] not in NM or len(p) > 2: raise ValueError("instrução inválida: " + txt)
    n = int(p[1]) if len(p) == 2 else 0
    if not 0 <= n <= 15: raise ValueError("operando deve estar entre 0 e 15")
    return (NM.index(p[0]) << 4) | n

EXEMPLOS = {"1": ("Contagem regressiva", ["LDI 5", "SUB 1", "JZ 4", "JMP 1", "HLT"]),
            "2": ("Contador binário", ["LDI 0", "ADD 1", "JMP 1"]),
            "3": ("Inverte os bits", ["LDI 5", "XOR 15", "JMP 1"])}

def mostrar(cpu):
    print("\n  ROM")
    for w in range(8):
        seta = "->" if w == cpu.pc else "  "
        print("  %s %d  %-8s %02X  %s" % (seta, w, dis(cpu.rom[w]), cpu.rom[w], format(cpu.rom[w], "08b")))
    a = cpu.acc
    leds = " ".join(("●" if (a >> i) & 1 else "○") for i in (3, 2, 1, 0))
    print("\n  LEDs (a3 a2 a1 a0): %s   ACC = %s = %d" % (leds, format(a, "04b"), a))
    print("  PC = %d   próxima instrução: %s%s   clocks: %d" % (cpu.pc, dis(cpu.rom[cpu.pc]),
          "  (parado)" if cpu.parado else "", cpu.ciclos))

AJUDA = """comandos:
  p N instrução     escreve na posição N (0 a 7), ex.: p 0 LDI 5   ou   p 1 31
  ex 1|2|3          carrega exemplo (1 contagem regressiva, 2 contador, 3 inverte bits)
  s [N]             executa N clocks (padrão 1)
  r [N] [seg]       executa até parar, ou N clocks, com pausa de seg segundos (padrão 0.3)
  reset             zera PC e ACC
  rom               mostra o estado     ajuda     sair"""

def carregar(cpu, linhas):
    cpu.rom = [0] * 8
    for w, l in enumerate(linhas[:8]): cpu.rom[w] = montar(l)
    cpu.reset()

def main():
    cpu = CPU()
    print("MiniCPU-4: %d portas, todas células do circuito revisado." % len(G))
    if len(sys.argv) > 1:
        carregar(cpu, open(sys.argv[1]).read().splitlines())
    else:
        carregar(cpu, EXEMPLOS["1"][1])
    print(AJUDA); mostrar(cpu)
    while True:
        try: linha = input("\n> ").strip()
        except EOFError: break
        if not linha: continue
        c = linha.split(None, 2)
        try:
            if c[0] in ("sair", "q"): break
            elif c[0] == "ajuda": print(AJUDA); continue
            elif c[0] == "p":
                cpu.rom[int(c[1])] = montar(c[2] if len(c) > 2 else "NOP"); cpu.reset()
            elif c[0] == "ex": carregar(cpu, EXEMPLOS[c[1]][1])
            elif c[0] == "reset": cpu.reset()
            elif c[0] == "s":
                for _ in range(int(c[1]) if len(c) > 1 else 1): cpu.passo()
            elif c[0] == "r":
                args = linha.split()[1:]
                n = int(args[0]) if args else 10**6
                pausa = float(args[1]) if len(args) > 1 else 0.3
                k = 0
                while k < n and not cpu.parado:
                    cpu.passo(); k += 1
                    print("  clock %-4d PC=%d ACC=%s (%d)" % (cpu.ciclos, cpu.pc, format(cpu.acc, "04b"), cpu.acc))
                    time.sleep(pausa)
            elif c[0] != "rom": print("comando desconhecido; digite ajuda"); continue
        except (ValueError, IndexError, KeyError) as e:
            print("erro:", e); continue
        mostrar(cpu)

if __name__ == "__main__":
    main()
