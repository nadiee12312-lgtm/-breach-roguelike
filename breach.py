#!/usr/bin/env python3
"""
BREACH — a Game Boy-style hacking roguelike.
Pick a runner & difficulty, then DESCEND through layered systems. After each node
you CHOOSE your next path (risk vs reward). Beat the layer guardians, build combos,
outrun the TRACE, spend score in shops that appear between runs. On ZERO DAY your
tools jam and break. Hit the leaderboard. Go deep.

Controls:  type answer + ENTER · F1 hint · F2 skip · F3 decode · F4 scanner · ESC pause
"""
import pygame, base64, random, codecs, json, os

DARK=(15,56,15); MID=(48,98,48); LITE=(139,172,15); BG=(155,188,15)
W,H=480,432
SAVE=os.path.expanduser("~/.breach_save.json")

pygame.init()
try:
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512); AUDIO=True
except Exception: AUDIO=False
SCALE=2
win=pygame.display.set_mode((W*SCALE,H*SCALE)); screen=pygame.Surface((W,H))
pygame.display.set_caption("BREACH"); clock=pygame.time.Clock()
fS=pygame.font.SysFont("monospace",13,bold=True)
fM=pygame.font.SysFont("monospace",17,bold=True)
fL=pygame.font.SysFont("monospace",30,bold=True)

def _wave(freq,ms,vol):
    import numpy as np
    n=int(22050*ms/1000); t=np.arange(n)
    w=(np.sign(np.sin(2*np.pi*freq*t/22050))*vol*32767).astype(np.int16)
    return np.column_stack([w,w])
def tone(freq,ms,vol=0.25):
    if not AUDIO: return None
    try: return pygame.mixer.Sound(buffer=_wave(freq,ms,vol).tobytes())
    except Exception: return None
SFX={"type":tone(440,18,.08),"ok":tone(880,90,.20),"bad":tone(110,180,.28),
     "buy":tone(660,70,.18),"boss":tone(220,220,.24),"combo":tone(1320,70,.18),
     "route":tone(520,40,.14)}
def play(k):
    s=SFX.get(k)
    if s:
        try: s.play()
        except Exception: pass

MUSIC=None
def build_music():
    global MUSIC
    if not AUDIO: return
    try:
        import numpy as np
        notes=[131,165,196,165, 147,196,220,196, 131,165,196,247, 110,147,196,165]
        arr=np.concatenate([_wave(f,200,0.06) for f in notes])
        MUSIC=pygame.mixer.Sound(buffer=arr.tobytes())
    except Exception: MUSIC=None
build_music()
def music_on():
    if MUSIC:
        try: pygame.mixer.Channel(5).play(MUSIC, loops=-1)
        except Exception: pass
def music_off():
    try: pygame.mixer.Channel(5).stop()
    except Exception: pass

def text(s,x,y,f=fS,col=DARK): screen.blit(f.render(s,False,col),(x,y))
def ctext(s,y,f=fM,col=DARK):
    surf=f.render(s,False,col); screen.blit(surf,(W//2-surf.get_width()//2,y))
def ctext_x(s,cx,y,f=fS,col=DARK):
    surf=f.render(s,False,col); screen.blit(surf,(cx-surf.get_width()//2,y))
def box(x,y,w,h,fill=LITE,border=DARK,bw=3):
    pygame.draw.rect(screen,fill,(x,y,w,h)); pygame.draw.rect(screen,border,(x,y,w,h),bw)
def wrap(s,n):
    out,line=[],""
    for w in s.split(" "):
        if len(line)+len(w)+1<=n: line+=(" " if line else "")+w
        else: out.append(line); line=w
    if line: out.append(line)
    return out

WORDS=['root','shell','admin','crypt','proxy','ghost','cipher','breach','kernel','daemon',
       'access','bypass','exploit','payload','rootkit','zeroday','backdoor','firewall','socket','trojan']
MORSE={'a':'.-','b':'-...','c':'-.-.','d':'-..','e':'.','f':'..-.','g':'--.','h':'....','i':'..',
       'j':'.---','k':'-.-','l':'.-..','m':'--','n':'-.','o':'---','p':'.--.','q':'--.-','r':'.-.',
       's':'...','t':'-','u':'..-','v':'...-','w':'.--','x':'-..-','y':'-.--','z':'--..'}
LEET={'4':'a','3':'e','1':'i','0':'o','7':'t','5':'s','9':'g'}
def p_base64():  w=random.choice(WORDS); return (base64.b64encode(w.encode()).decode(),"Base64 -> text",w,"BASE64")
def p_rot13():   w=random.choice(WORDS); return (codecs.encode(w,'rot_13'),"ROT13",w,"ROT13")
def p_hex():     w=random.choice(WORDS); return (w.encode().hex(),"Hex -> ASCII",w,"HEX")
def p_binary():  w=random.choice([x for x in WORDS if len(x)<=6]); return (' '.join(format(ord(c),'08b') for c in w),"Binary -> text",w,"BINARY")
def p_caesar():  w=random.choice(WORDS); sh=random.randint(2,8); return (''.join(chr((ord(c)-97+sh)%26+97) for c in w),f"Caesar shift {sh}",w,"CAESAR")
def p_reverse(): w=random.choice(WORDS); return (w[::-1],"Reversed",w,"REVERSE")
def p_xor():     w=random.choice([x for x in WORDS if len(x)<=7]); k=random.randint(1,9); return (' '.join(str(ord(c)^k) for c in w),f"XOR with {k} -> ASCII",w,"XOR")
def p_firewall():a,b=random.randint(10,40),random.randint(10,40); seq=[a,b,a+b,a+2*b,2*a+3*b]; return (', '.join(map(str,seq))+", ?","Sum of previous two",str(3*a+5*b),"SEQUENCE")
def p_morse():   w=random.choice([x for x in WORDS if len(x)<=6]); return (' '.join(MORSE[c] for c in w),"Morse -> text",w,"MORSE")
def p_atbash():  w=random.choice(WORDS); return (''.join(chr(122-(ord(c)-97)) for c in w),"Atbash (a<->z)",w,"ATBASH")
def p_leet():    w=random.choice(WORDS); rev={v:k for k,v in LEET.items()}; return (''.join(rev.get(c,c) for c in w),"Leetspeak -> text",w,"LEET")
def p_ascii():   w=random.choice([x for x in WORDS if len(x)<=6]); return (' '.join(str(ord(c)) for c in w),"Decimal ASCII -> text",w,"ASCII")
def p_url():     w=random.choice([x for x in WORDS if len(x)<=6]); return (''.join('%%%02x'%ord(c) for c in w),"URL-encoded (%XX) -> text",w,"URLENC")
def p_vigenere():
    w=random.choice([x for x in WORDS if len(x)<=7]); key=random.choice(['key','hex','sys'])
    enc=''.join(chr((ord(w[i])-97+ord(key[i%len(key)])-97)%26+97) for i in range(len(w)))
    return (f"{enc}  (key: {key})","Vigenere, subtract key",w,"VIGENERE")
SEC_Q=[("Port for SSH?","22"),("Port for HTTPS?","443"),("Port for HTTP?","80"),
       ("Tool to scan ports?","nmap"),("Broken hash algo?","md5"),("Encoding, not encryption?","base64"),
       ("Port for DNS?","53"),("Famous wordlist?","rockyou"),("Port for RDP?","3389"),
       ("Tool to crack hashes (GPU)?","hashcat"),("Web proxy for pentesting?","burp"),("Port for FTP?","21")]
def p_security(): q,a=random.choice(SEC_Q); return (q,"security trivia",a,"INTEL")
PUZZLES=[p_base64,p_rot13,p_hex,p_binary,p_caesar,p_reverse,p_xor,p_firewall,
         p_morse,p_atbash,p_leet,p_ascii,p_url,p_vigenere,p_security]
def p_boss(): w=random.choice(WORDS); return (base64.b64encode(w[::-1].encode()).decode(),"GUARDIAN: Base64 then REVERSE",w,"GUARDIAN")

LAYERS=["OUTER NET","DMZ","INTRANET","THE VAULT","DATA CORE","BLACK ICE","DEEP NODE"]
GUARDIANS=["SENTINEL","WARDEN","BLACK ICE","CERBERUS","THE ARCHITECT","NULL","OVERSEER"]
CHARS=[
    {"name":"NEON","hp":6,"mult":1.0,"skips":0,"perk":"none","desc":"6 integrity"},
    {"name":"R00T","hp":5,"mult":1.5,"skips":0,"perk":"none","desc":"+50% score"},
    {"name":"GHOST","hp":5,"mult":1.0,"skips":2,"perk":"none","desc":"2 free skips"},
    {"name":"ORACLE","hp":5,"mult":1.0,"skips":0,"perk":"type","desc":"sees cipher type"},
    {"name":"VIPER","hp":5,"mult":1.0,"skips":0,"perk":"shop","desc":"30% off shop"},
    {"name":"ECHO","hp":5,"mult":1.0,"skips":0,"perk":"trace","desc":"slow trace"},
]
DIFFS=[
    {"name":"SCRIPT KIDDIE","smult":1.0,"trace":0.06,"shop_n":6,"break":False,"hpmod":0,"desc":"chill. learn it."},
    {"name":"OPERATOR","smult":1.6,"trace":0.12,"shop_n":6,"break":False,"hpmod":0,"desc":"the real deal."},
    {"name":"GHOST PROTOCOL","smult":2.4,"trace":0.22,"shop_n":4,"break":False,"hpmod":0,"desc":"fast trace, lean shop."},
    {"name":"ZERO DAY","smult":3.5,"trace":0.34,"shop_n":3,"break":True,"hpmod":-1,"desc":"tools JAM & break. legends only."},
]
TOOLS=[
    {"name":"HINT [F1]","cost":30,"k":"hint","desc":"extra hint"},
    {"name":"SHIELD","cost":55,"k":"shield","desc":"blocks next fail"},
    {"name":"SKIP [F2]","cost":75,"k":"skip","desc":"skip a node"},
    {"name":"DECODE [F3]","cost":130,"k":"decode","desc":"auto-solve a node"},
    {"name":"SCANNER [F4]","cost":45,"k":"scanner","desc":"reveal cipher type"},
    {"name":"OVERCLOCK","cost":90,"k":"oc","desc":"2x next correct"},
]
EVENTS=[("HIDDEN CACHE","Loose credits. +40 score.","score",40),
        ("EXPLOIT KIT","Free DECODE added.","tool","decode"),
        ("ALLY RUNNER","A friend slips you a SKIP.","tool","skip"),
        ("SYSTEM PATCH","Logs cleared. Trace reset.","trace",0),
        ("HONEYPOT","A trap drained 30 score.","score",-30),
        ("DEAD NODE","Nothing here... keep moving.","none",0)]
ROUTES={"std":("STD NODE","standard cipher"),"secure":("SECURE NODE","guarded, 2x score, +trace"),
        "cache":("DATA CACHE","easy node, bonus score"),"shop":("MARKET","tools, then a node"),
        "event":("DARK NODE","unknown event, then a node")}
ACH={"first":("FIRST BLOOD","breach a node"),"boss":("GUARDIAN DOWN","beat a guardian"),
     "combo5":("ON FIRE","hit x3 combo"),"deep10":("DEEP DIVE","reach node 10"),
     "rich":("LOADED","hold 300+ score"),"zd":("ZERO COOL","clear a node on ZERO DAY"),
     "layer3":("INTRUDER","reach THE VAULT")}

def load_save():
    try: return json.load(open(SAVE))
    except Exception: return {"best":0,"board":[],"ach":[]}
def write_save(d): json.dump(d,open(SAVE,"w"))

class State:
    def __init__(s):
        s.scene="menu"; s.sel=0; s.dsel=1; s.save=load_save(); s.initials=""
        s.glitch=0; s.flash=0; s.scan=0

    def start(s,ch,diff):
        s.ch=ch; s.diff=diff; s.perk=ch["perk"]
        s.maxhp=max(1,ch["hp"]+diff["hpmod"]); s.hp=s.maxhp; s.mult=ch["mult"]
        s.score=0; s.depth=0; s.combo=0; s.trace=0.0; s.wear=0; s.bought=False
        s.inv={"hint":0,"skip":ch["skips"],"decode":0,"scanner":0}
        s.shield=False; s.oc=False; s.msg=""; s.glitch=0; s.flash=0; s.scan=0
        s.event=None; s.queued=None; s.bonus=False; s.routes=[]; s.rsel=0
        s.stock=list(range(len(TOOLS))); s.gen_node("std"); s.scene="play"; music_on()

    def layer(s): return LAYERS[min((s.depth-1)//5, len(LAYERS)-1)]
    def unlock(s,key):
        if key not in s.save["ach"]:
            s.save["ach"].append(key); write_save(s.save); s.msg="ACHIEVEMENT: "+ACH[key][0]

    def gen_node(s,kind):
        s.depth+=1; s.boss=(kind=="boss"); s.secure=(kind=="secure"); s.bonus=(kind=="cache"); s.trace=0.0; s.scan=8
        gen=p_boss if (s.boss or s.secure) else random.choice(PUZZLES)
        s.disp,s.hint,s.ans,s.ptype=gen()
        s.show_hint=(s.perk=="type"); s.scanned=(s.perk=="type"); s.inp=""
        if s.secure: s.trace=25.0      # head start on the trace = real pressure
        if s.boss: play("boss")

    def open_shop(s):
        s.stock=sorted(random.sample(range(len(TOOLS)),min(s.diff["shop_n"],len(TOOLS))))
        s.scene="shop"

    def advance(s):
        if (s.depth+1)%5==0:
            s.gen_node("boss"); s.scene="play"
        else:
            s.routes=random.sample(["std","secure","cache","shop","event"],3); s.rsel=0
            s.scene="route"; play("route")

    def take_route(s,t):
        if t=="shop": s.open_shop(); s.queued="std"
        elif t=="event": s.event=random.choice(EVENTS); s.scene="event"; s.queued="std"
        else: s.gen_node(t); s.scene="play"

    def apply_event(s):
        _,_,kind,val=s.event
        if kind=="score": s.score=max(0,s.score+val)
        elif kind=="tool": s.inv[val]+=1
        elif kind=="trace": s.trace=0.0
        s.event=None
        if s.queued: s.gen_node(s.queued); s.queued=None
        s.scene="play"

    def leave_shop(s):
        if s.queued: s.gen_node(s.queued); s.queued=None
        s.scene="play"

    def use_tool(s,key):
        if s.diff["break"]:
            prob=min(0.12+s.wear*0.12,0.85); s.wear+=1
            if random.random()<prob:
                s.inv[key]=max(0,s.inv[key]-1); s.msg="TOOL JAMMED! it broke."; play("bad"); return False
        s.inv[key]=max(0,s.inv[key]-1); return True

    def submit(s):
        if s.inp.strip().lower()==s.ans.lower():
            s.combo+=1; cmult=1.0+0.25*min(s.combo-1,6)
            base=s.depth*10*s.mult*s.diff["smult"]*cmult
            gain=int(base)*(2 if (s.boss or s.secure) else 1)*(2 if s.oc else 1)+(25 if s.bonus else 0)
            s.score+=gain; s.oc=False
            s.msg=f"GRANTED +{gain}"+(f"  COMBO x{s.combo}" if s.combo>1 else "")
            s.flash=6; play("combo" if s.combo>1 else "ok")
            s.unlock("first")
            if s.boss: s.unlock("boss")
            if s.combo>=3: s.unlock("combo5")
            if s.depth>=10: s.unlock("deep10")
            if s.score>=300: s.unlock("rich")
            if s.depth>=11: s.unlock("layer3")
            if s.diff["name"]=="ZERO DAY": s.unlock("zd")
            s.advance()
        else:
            s.combo=0; s.glitch=10; play("bad")
            if s.shield: s.shield=False; s.msg=f"SHIELD ABSORBED (was '{s.ans}')"; s.advance()
            else:
                s.hp-=1; s.msg=f"DENIED (was '{s.ans}')"
                if s.hp<=0: s.game_over()
                else: s.advance()
        s.inp=""

    def trace_hit(s):
        s.hp-=1; s.combo=0; s.glitch=12; play("bad"); s.trace=0.0; s.msg="TRACED! -1"
        if s.hp<=0: s.game_over()
        else: s.advance()

    def game_over(s):
        music_off()
        s.best=max(s.score,s.save["best"]); s.save["best"]=s.best; write_save(s.save)
        lows=[b[1] for b in s.save["board"]] or [0]
        s.qual=(len(s.save["board"])<5 or s.score>min(lows))
        s.scene="name" if (s.qual and s.score>0) else "over"; s.initials=""

    def save_initials(s):
        s.save["board"].append([s.initials or "AAA",s.score])
        s.save["board"]=sorted(s.save["board"],key=lambda b:-b[1])[:5]; write_save(s.save); s.scene="over"

st=State()

def draw_menu():
    screen.fill(BG); ctext("B R E A C H",36,fL); ctext("a hacking roguelike",80,fS,MID)
    ctext("1. select runner:",110,fS)
    for i,c in enumerate(CHARS):
        x=18+(i%3)*155; y=134+(i//3)*104; sel=(i==st.sel)
        box(x,y,140,88,LITE if sel else BG,DARK,4 if sel else 2)
        ctext_x(c["name"],x+70,y+10,fM)
        for j,ln in enumerate(wrap(c["desc"],16)): ctext_x(ln,x+70,y+38+j*15,fS)
    ctext("< >  choose    ENTER  next",368,fS,MID)
    ctext(f"high: {st.save['best']}   [H] how to play   [L] board",400,fS,MID)

def draw_help():
    screen.fill(BG); ctext("HOW TO PLAY",40,fL)
    lines=["You descend a system, node by node.","Each node is a hacking puzzle:",
           "read the intercepted data, type the answer.","",
           "After each node you CHOOSE your path:","STD / SECURE(2x) / CACHE / MARKET / DARK.","",
           "COMBO: chain correct answers for bonus.","TRACE: the bar rises - solve fast or lose HP.","Every 5 nodes: a LAYER GUARDIAN (boss).",
           "Tools: F1 hint F2 skip F3 decode F4 scanner.","ZERO DAY: tools can jam & break."]
    for i,l in enumerate(lines): ctext(l,90+i*24,fS)
    ctext("[B] back",404,fS,MID)

def draw_diff():
    screen.fill(BG); ctext("2. select difficulty:",46,fM)
    for i,d in enumerate(DIFFS):
        y=90+i*78; sel=(i==st.dsel)
        box(30,y,W-60,68,LITE if sel else BG,DARK,4 if sel else 2)
        text(d["name"],44,y+8,fM); text(f"score x{d['smult']}",W-150,y+8,fS,MID)
        text(d["desc"],44,y+34,fS,MID)
    ctext("< >  choose    ENTER  hack in",406,fS,MID)

def draw_route():
    screen.fill(BG); ctext("CHOOSE YOUR PATH",40,fM); ctext(f"-- {st.layer()} --",70,fS,MID)
    for i,t in enumerate(st.routes):
        lbl,desc=ROUTES[t]; y=104+i*86; sel=(i==st.rsel)
        box(40,y,W-80,74,LITE if sel else BG,DARK,4 if sel else 2)
        ctext_x(f"{i+1}. {lbl}",W//2,y+12,fM)
        ctext_x(desc,W//2,y+42,fS,MID)
    ctext("< >  or  1-3     ENTER  go",404,fS,MID)

def draw_event():
    screen.fill(BG); name,desc,kind,val=st.event
    ctext("// EVENT //",70,fM); box(40,120,W-80,150,LITE,DARK,3); ctext(name,150,fM)
    for j,ln in enumerate(wrap(desc,30)): ctext(ln,185+j*20,fS)
    ctext("press ENTER to continue",320,fS,MID)

def draw_play():
    screen.fill(BG); gx=random.randint(-st.glitch,st.glitch) if st.glitch>0 else 0
    if st.flash>0: screen.fill(LITE)
    box(0,0,W,40,LITE,DARK,3); text(st.ch["name"],8,12,fM)
    hearts="".join("#" if i<st.hp else "." for i in range(st.maxhp))
    text(f"INT {hearts}",110,6,fS); text(f"SCORE {st.score}",110,22,fS)
    text(f"COMBO x{st.combo}" if st.combo>1 else "COMBO -",300,6,fS)
    text("TRACE",300,22,fS); box(355,23,110,10,BG,DARK,1)
    tw=int(108*min(st.trace,100)/100); pygame.draw.rect(screen,DARK if st.trace<70 else MID,(356,24,tw,8))
    g=GUARDIANS[min((st.depth-1)//5,len(GUARDIANS)-1)]
    if st.boss: title="== GUARDIAN: "+g+" =="
    elif st.secure: title="-- SECURE NODE "+f"{st.depth:02d}"+" --"
    elif st.bonus: title="-- DATA CACHE "+f"{st.depth:02d}"+" --"
    else: title="-- NODE "+f"{st.depth:02d}"+" --"
    ctext(title,50,fM); text(st.layer(),W-150,46,fS,MID)
    box(25+gx,84,W-50,104,LITE,DARK,3); ctext("intercepted:",94,fS,MID)
    ctext(st.disp[:44],118,fM)
    if len(st.disp)>44: ctext(st.disp[44:88],140,fM)
    if st.scan>0:
        sy=84+int((8-st.scan)/8*104); pygame.draw.line(screen,DARK,(28,sy),(W-28,sy),2)
    if st.scanned or st.show_hint:
        line=f"[{st.ptype}] {st.hint}" if (st.scanned and st.show_hint) else (f"type: {st.ptype}" if st.scanned else f"hint: {st.hint}")
        ctext(line,166,fS,MID)
    else: ctext("[F1] hint(30)   [F4] scan(45)",166,fS,MID)
    box(25,204,W-50,42,BG,DARK,3); text("decode> "+st.inp+"_",36,215,fM)
    wstr=f"  wear:{st.wear}" if st.diff["break"] else ""
    text(f"skip:{st.inv['skip']} shield:{'ON' if st.shield else 0} dec:{st.inv['decode']} OC:{'ON' if st.oc else 0}{wstr}",25,260,fS,MID)
    text("[F2] skip   [F3] decode   [ESC] pause",25,280,fS,MID)
    if st.msg: box(25,310,W-50,34,LITE,DARK,3); ctext(st.msg,316,fS)

def draw_pause():
    draw_play(); ov=pygame.Surface((W,H)); ov.set_alpha(150); ov.fill(BG); screen.blit(ov,(0,0))
    box(90,150,W-180,130,LITE,DARK,4); ctext("-- PAUSED --",185,fM)
    ctext("[ESC] resume",225,fS); ctext("[Q] quit to menu",250,fS,MID)

def draw_shop():
    screen.fill(BG); ctext("// BLACK MARKET //",20,fM)
    disc=0.7 if st.perk=="shop" else 1.0
    extra="  (VIPER -30%)" if disc<1 else ("  (ZERO DAY: limited stock)" if st.diff["break"] else "")
    ctext(f"score: {st.score}"+extra,52,fS,MID)
    for slot,idx in enumerate(st.stock):
        t=TOOLS[idx]; y=82+slot*54; cost=int(t["cost"]*disc)
        box(25,y,W-50,46,LITE,DARK,3); text(f"{slot+1}. {t['name']}",36,y+6,fS)
        text(f"{cost}",W-80,y+6,fS,MID); text(t["desc"],36,y+26,fS,MID)
    ctext("number to buy   ENTER leave",410,fS,MID)

def draw_name():
    screen.fill(BG); ctext("NEW HIGH SCORE!",90,fM); ctext(f"score {st.score}",130,fM)
    ctext("enter initials:",180,fS); ctext((st.initials or "_")[:3],215,fL)
    ctext("type 3 letters + ENTER",300,fS,MID)

def draw_over():
    screen.fill(BG); ctext("CONNECTION",60,fL); ctext("TERMINATED",100,fL)
    ctext(f"node {st.depth}   score {st.score}   best {st.save['best']}",165,fS)
    ctext("-- LEADERBOARD --",195,fS,MID)
    for i,b in enumerate(st.save["board"][:5]): ctext_x(f"{i+1}. {b[0]}  {b[1]}",W//2,218+i*19,fS)
    ctext(f"achievements: {len(st.save['ach'])}/{len(ACH)}",345,fS,MID)
    ctext("[R] jack back in",388,fS,MID)

def draw_board():
    screen.fill(BG); ctext("LEADERBOARD",48,fL)
    if not st.save["board"]: ctext("no runs yet",126,fM,MID)
    for i,b in enumerate(st.save["board"][:5]): ctext(f"{i+1}.  {b[0]}   {b[1]}",116+i*26,fM)
    ctext("-- ACHIEVEMENTS --",272,fS,MID); y=294
    for k,(nm,ds) in ACH.items():
        got=k in st.save["ach"]; ctext_x(("[x] " if got else "[ ] ")+nm,W//2,y,fS,DARK if got else MID); y+=17
    ctext("[B] back",416,fS,MID)

SCENES={"menu":draw_menu,"help":draw_help,"diff":draw_diff,"route":draw_route,"event":draw_event,
        "play":draw_play,"pause":draw_pause,"shop":draw_shop,"name":draw_name,"over":draw_over,"board":draw_board}

def main():
    run=True
    while run:
        for e in pygame.event.get():
            if e.type==pygame.QUIT: run=False
            elif e.type==pygame.KEYDOWN:
                sc=st.scene
                if sc=="menu":
                    if e.key==pygame.K_LEFT: st.sel=(st.sel-1)%len(CHARS)
                    elif e.key==pygame.K_RIGHT: st.sel=(st.sel+1)%len(CHARS)
                    elif e.key==pygame.K_h: st.scene="help"
                    elif e.key==pygame.K_l: st.scene="board"
                    elif e.key==pygame.K_RETURN: st.scene="diff"
                elif sc in ("help","board"):
                    if e.key==pygame.K_b: st.scene="menu"
                elif sc=="diff":
                    if e.key==pygame.K_LEFT: st.dsel=(st.dsel-1)%len(DIFFS)
                    elif e.key==pygame.K_RIGHT: st.dsel=(st.dsel+1)%len(DIFFS)
                    elif e.key==pygame.K_RETURN: st.start(CHARS[st.sel],DIFFS[st.dsel])
                elif sc=="route":
                    if e.key==pygame.K_LEFT: st.rsel=(st.rsel-1)%len(st.routes)
                    elif e.key==pygame.K_RIGHT: st.rsel=(st.rsel+1)%len(st.routes)
                    elif pygame.K_1<=e.key<=pygame.K_3 and e.key-pygame.K_1<len(st.routes):
                        st.rsel=e.key-pygame.K_1; st.take_route(st.routes[st.rsel])
                    elif e.key==pygame.K_RETURN: st.take_route(st.routes[st.rsel])
                elif sc=="event":
                    if e.key==pygame.K_RETURN: st.apply_event()
                elif sc=="play":
                    if e.key==pygame.K_ESCAPE: st.scene="pause"
                    elif e.key==pygame.K_RETURN and st.inp: st.submit()
                    elif e.key==pygame.K_BACKSPACE: st.inp=st.inp[:-1]
                    elif e.key==pygame.K_F1:
                        if not st.show_hint and st.score>=30: st.score-=30; st.show_hint=True; play("buy")
                    elif e.key==pygame.K_F4:
                        if not st.scanned and st.score>=45: st.score-=45; st.scanned=True; play("buy")
                    elif e.key==pygame.K_F2 and st.inv["skip"]>0:
                        if st.use_tool("skip"): st.msg="node skipped"; play("buy"); st.advance()
                    elif e.key==pygame.K_F3 and st.inv["decode"]>0:
                        if st.use_tool("decode"): st.inp=st.ans; st.submit()
                    elif e.unicode and e.unicode.isprintable():
                        if len(st.inp)<40: st.inp+=e.unicode; play("type")
                elif sc=="pause":
                    if e.key==pygame.K_ESCAPE: st.scene="play"
                    elif e.key==pygame.K_q: music_off(); st.__init__()
                elif sc=="shop":
                    if e.key==pygame.K_RETURN: st.leave_shop()
                    elif pygame.K_1<=e.key<=pygame.K_9:
                        slot=e.key-pygame.K_1
                        if slot<len(st.stock):
                            t=TOOLS[st.stock[slot]]; disc=0.7 if st.perk=="shop" else 1.0; cost=int(t["cost"]*disc)
                            if st.score>=cost:
                                st.score-=cost; st.bought=True; play("buy")
                                if t["k"]=="shield": st.shield=True
                                elif t["k"]=="oc": st.oc=True
                                else: st.inv[t["k"]]+=1
                elif sc=="name":
                    if e.key==pygame.K_RETURN: st.save_initials()
                    elif e.key==pygame.K_BACKSPACE: st.initials=st.initials[:-1]
                    elif e.unicode.isalpha() and len(st.initials)<3: st.initials+=e.unicode.upper()
                elif sc=="over":
                    if e.key==pygame.K_r: music_off(); st.__init__()

        if st.scene=="play":
            st.trace += st.diff["trace"]*(0.45 if st.perk=="trace" else 1.0)
            if st.trace>=100: st.trace_hit()
            if st.scan>0: st.scan-=1
        if st.glitch>0: st.glitch-=1
        if st.flash>0: st.flash-=1
        SCENES[st.scene]()
        pygame.transform.scale(screen,(W*SCALE,H*SCALE),win); pygame.display.flip(); clock.tick(30)
    pygame.quit()

if __name__=="__main__": main()
