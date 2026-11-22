import csv, collections

# ============ célula revisada (circuito A,B,P,N) ============

def cell(a,b,p,n,withnot=False):
    g1=a&b; g2=a|b; g3=1-(a^b)
    t1=g1&(1-p)&n; t2=g2&p&(1-n); t3=g3&p&n; t4=1-(g2|p|n)
    o=t1|t2|t3|t4
    return 1-o if withnot else o
# gate -> (tipo de célula, P, N)
MAP={"AND":("A",0,1),"OR":("A",1,0),"NOR":("A",0,0),"NOT":("A",0,0),"NAND":("B",0,1),"XOR":("B",1,1)}
SPEC={"AND":lambda a,b:a&b,"OR":lambda a,b:a|b,"NOR":lambda a,b:1-(a|b),"NAND":lambda a,b:1-(a&b),"XOR":lambda a,b:a^b,"NOT":lambda a,b:1-a}
for t,(k,p,n) in MAP.items():
    for a in (0,1):
        for b in (0,1):
            bb=a if t=="NOT" else b
            assert cell(a,bb,p,n,k=="B")==SPEC[t](a,bb),t

# ============ netlist do computador ============

G=[];
blk=["?"];
cnt=[0]
def new(): cnt[0]+=1; return "n%d"%cnt[0]
def g(t,a,b=None,out=None):
    o=out or new(); G.append((blk[0],t,a,b if b is not None else a,o)); return o
def NOT(a,out=None): return g("NOT",a,None,out)
def AND(a,b): return g("AND",a,b)
def OR(a,b): return g("OR",a,b)
def XOR(a,b): return g("XOR",a,b)
def NOR(a,b): return g("NOR",a,b)
def NAND(a,b,out=None): return g("NAND",a,b,out)
def ORn(l):
    x=l[0]
    for y in l[1:]: x=OR(x,y)
    return x
def ANDn(l):
    x=l[0]
    for y in l[1:]: x=AND(x,y)
    return x
def mux2(sel,nsel,a0,a1): return OR(AND(a0,nsel),AND(a1,sel))
def latch(d,e):
    nd=NOT(d); s=NAND(d,e); r=NAND(nd,e)
    q=new(); qb=new()
    NAND(s,qb,q); NAND(r,q,qb); return q
def dff(d,clk,nclk):
    return latch(latch(d,nclk),clk)
PROG=[0x15,0x31,0x84,0x71,0xF0,0,0,0]
blk[0]="Clock/reset"; nclk=NOT("CLK")
# ROM
blk[0]="ROM 8x8"
pc=["pc0","pc1","pc2"]
npc=[NOT(x) for x in pc]
sel=[]
for w in range(8):
    lits=[(pc[i] if (w>>i)&1 else npc[i]) for i in range(3)]
    sel.append(ANDn(lits))
I=[]
for k in range(8):
    I.append(ORn([AND(sel[w],"SW%d_%d"%(w,k)) for w in range(8)]))
imm=I[0:4]; op=I[4:8]
blk[0]="Decodificador"
nop=[NOT(x) for x in op]
D={}
for k in (1,2,3,4,5,6,7,8,15):
    D[k]=ANDn([(op[i] if (k>>i)&1 else nop[i]) for i in range(4)])
blk[0]="ALU"
nD1=NOT(D[1])
acc=["a0","a1","a2","a3"]
Aeff=[AND(acc[i],nD1) for i in range(4)]
Beff=[XOR(imm[i],D[3]) for i in range(4)]
carry=D[3]; SUM=[]
for i in range(4):
    x=XOR(Aeff[i],Beff[i]); s=XOR(x,carry); SUM.append(s)
    if i<3: carry=OR(AND(Aeff[i],Beff[i]),AND(x,carry))
AN=[AND(Aeff[i],Beff[i]) for i in range(4)]
ORu=[OR(Aeff[i],Beff[i]) for i in range(4)]
XO=[XOR(Aeff[i],Beff[i]) for i in range(4)]
selADD=NOR(OR(D[4],D[5]),D[6])
R=[ORn([AND(SUM[i],selADD),AND(AN[i],D[4]),AND(ORu[i],D[5]),AND(XO[i],D[6])]) for i in range(4)]
WE=ORn([D[1],D[2],D[3],D[4],D[5],D[6]])
blk[0]="Acumulador (ACC)"
nWE=NOT(WE)
for i in range(4):
    d=AND(mux2(WE,nWE,acc[i],R[i]),"RST_N")
    dff(d,"CLK",nclk) if False else None
    # dff com saída com nome fixo
    m=latch(d,nclk)
    nd=NOT(m); s=NAND(m,"CLK"); r=NAND(nd,"CLK"); qb=new()
    NAND(s,qb,acc[i]); NAND(r,acc[i],qb)
blk[0]="Zero e controle do PC"
Z=NOR(OR(acc[0],acc[1]),OR(acc[2],acc[3]))
LOADs=OR(D[7],AND(D[8],Z)); nLOAD=NOT(LOADs); HLTn=NOT(D[15])
blk[0]="PC (3 bits)"
c0=AND("pc0",HLTn); s0=XOR("pc0",HLTn)
c1=AND("pc1",c0);  s1=XOR("pc1",c0)
s2=XOR("pc2",c1)
for i,sx in enumerate((s0,s1,s2)):
    d=AND(mux2(LOADs,nLOAD,sx,imm[i]),"RST_N")
    m=latch(d,nclk)
    nd=NOT(m); s=NAND(m,"CLK"); r=NAND(nd,"CLK"); qb=new()
    NAND(s,qb,pc[i]); NAND(r,pc[i],qb)

# ============ simulação com TODAS as portas virando células ============

def settle(v):
    for _ in range(400):
        ch=False
        for b,t,a,bb,o in G:
            k,p,n=MAP[t]
            r=cell(v.get(a,0),v.get(bb,0),p,n,k=="B")
            if v.get(o)!=r: v[o]=r; ch=True
        if not ch: return
    raise RuntimeError("não estabilizou")
def run(prog,cycles):
    v={"CLK":0,"RST_N":0}
    for w in range(8):
        for k in range(8): v["SW%d_%d"%(w,k)]=(prog[w]>>k)&1
    settle(v); v["CLK"]=1; settle(v); v["CLK"]=0; settle(v); v["CLK"]=1; settle(v); v["CLK"]=0; settle(v)
    v["RST_N"]=1; settle(v); tr=[]
    for _ in range(cycles):
        # estado antes do pulso = instrução executada neste pulso
        pcv=v["pc0"]+2*v["pc1"]+4*v["pc2"]; acv=sum(v[a]<<i for i,a in enumerate(acc))
        v["CLK"]=1; settle(v); v["CLK"]=0; settle(v)
        tr.append((pcv,PROG_NAMES.get(prog[pcv],hex(prog[pcv])),acv))
    return tr
PROG_NAMES={}
if __name__=="__main__":
    tr=run(PROG,16)
    print([a for _,_,a in tr]); print(tr[-1])
    tr2=run([0x10,0x21,0x71,0,0,0,0,0],10); print("contagem:",[a for _,_,a in tr2])
    cntg=collections.Counter(t for _,t,_,_,_ in G)
    print(len(G),cntg)
    blkc=collections.OrderedDict()
    for b,t,_,_,_ in G: blkc[b]=blkc.get(b,0)+1
    print(blkc)
    with open("/mnt/user-data/outputs/MiniCPU4_netlist_celulas.csv","w",newline="") as f:
        w=csv.writer(f); w.writerow(["id","bloco","funcao_original","celula","P","N","entrada_A","entrada_B","saida"])
        for i,(b,t,a,bb,o) in enumerate(G,1):
            k,p,n=MAP[t]; w.writerow([i,b,t,"CELULA_"+k,p,n,a,bb if t!="NOT" else a,o])
