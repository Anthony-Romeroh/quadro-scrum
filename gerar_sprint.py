#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sprint Board Generator
Uso: python gerar_sprint.py
Salva JSON em dados/ e atualiza board.html automaticamente.
"""

import json, os, time, glob, re
from datetime import datetime

TAGS = ["bundle", "git", "infra", "motor", "docs"]
COLS = ["todo", "doing", "done", "debug"]
COL_LABELS = {"todo": "a fazer", "doing": "fazendo", "done": "feito", "debug": "debug/erro"}
DADOS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados")
BOARD_HTML = os.path.join(os.path.dirname(os.path.abspath(__file__)), "board.html")

CARDS_PADRAO = {
    "todo": [
        {"title": "Corrigir nome da branch para padrao anthonyhernandez_Bemol/feat-bundle-roteirizacao", "tag": "tag-git"},
        {"title": "Recriar branch a partir da dev sincronizada com a main", "tag": "tag-git"},
        {"title": "Adicionar roteirizacao = true no pyproject.toml", "tag": "tag-bundle"},
        {"title": "Abrir PR para dev com reviewer chefa", "tag": "tag-git"},
        {"title": "Linkar epico 266515 no PR", "tag": "tag-git"},
        {"title": "Validar catalogo inteligencia_negocios no Unity Catalog", "tag": "tag-infra"},
        {"title": "Validar schema roterizacao no Unity Catalog", "tag": "tag-infra"},
        {"title": "Aguardar aprovacao e deploy automatico via esteira CI/CD", "tag": "tag-bundle"},
        {"title": "Validar pipelines publicadas no Databricks apos deploy", "tag": "tag-bundle"},
        {"title": "Coordenar deploy com a PSW", "tag": "tag-infra"},
        {"title": "Configurar schedule 10 min pausado apos deploy em prod", "tag": "tag-bundle"},
        {"title": "Aguardar e incorporar codigo definitivo do motor lat_log.py e motor.py", "tag": "tag-motor"},
        {"title": "Alinhar com Sabrina sobre status do software do motor", "tag": "tag-motor"},
        {"title": "Criar README.md do bundle roteirizacao", "tag": "tag-docs"},
        {"title": "Configurar git user.name e user.email", "tag": "tag-git"},
        {"title": "Verificar infraestrutura minima - catalogo, schemas, volumes (guia item 3.1)", "tag": "tag-infra"},
        {"title": "Testar execucao das pipelines gold apos deploy (guia item 6.4)", "tag": "tag-bundle"},
        {"title": "Avaliar necessidade de tags no bundle (guia item 4.5)", "tag": "tag-docs"},
    ],
    "doing": [
        {"title": "Alinhar fluxo correto de deploy via CI/CD com chefa e consultoria", "tag": "tag-bundle"},
    ],
    "done": [
        {"title": "Instalar Databricks CLI v1.2.0 via extensao VS Code", "tag": "tag-infra"},
        {"title": "Gerar token PAT com escopo all-apis e configurar autenticacao", "tag": "tag-infra"},
        {"title": "Clonar repositorio Databricks-Mawe do Azure DevOps", "tag": "tag-git"},
        {"title": "Criar estrutura do bundle roteirizacao no repositorio", "tag": "tag-bundle"},
        {"title": "Criar databricks.yml com targets dev e prod", "tag": "tag-bundle"},
        {"title": "Criar roteirizacao_ship_from_store.yml", "tag": "tag-bundle"},
        {"title": "Criar roteirizacao_ship_from_store_pendentes.yml", "tag": "tag-bundle"},
        {"title": "Criar roteirizacao_motor.yml placeholder serverless", "tag": "tag-motor"},
        {"title": "Incorporar notebooks gold ship_from_store.py e pendentes", "tag": "tag-bundle"},
        {"title": "bundle validate passou - Validation OK!", "tag": "tag-bundle"},
        {"title": "Mapear 9 tabelas fonte com pipeline de origem e frequencia", "tag": "tag-docs"},
        {"title": "Branch feat/bundle-roteirizacao criada e enviada para Azure DevOps", "tag": "tag-git"},
        {"title": "Deploy manual testado com sucesso - Deployment complete!", "tag": "tag-bundle"},
        {"title": "Deploy manual removido com bundle destroy", "tag": "tag-bundle"},
        {"title": "Validar arquitetura com chefa - bundle so gold confirmado", "tag": "tag-bundle"},
        {"title": "Definir computacao serverless com chefa - sem cluster policy", "tag": "tag-infra"},
    ],
    "debug": [
        {"title": "Token PAT sem escopo all-apis bloqueava upload - resolvido com novo token", "tag": "tag-infra"},
        {"title": "Deploy feito direto do CLI local - nao segue padrao CI/CD do repositorio", "tag": "tag-bundle"},
        {"title": "Branch criada a partir da main em vez da dev", "tag": "tag-git"},
        {"title": "Nome da branch fora do padrao githubusername/tipo-descricao", "tag": "tag-git"},
    ]
}

def cor(t, c): return f"\033[{c}m{t}\033[0m"
def verde(t): return cor(t, "92")
def amarelo(t): return cor(t, "93")
def vermelho(t): return cor(t, "91")
def azul(t): return cor(t, "94")
def cinza(t): return cor(t, "90")
def negrito(t): return cor(t, "1")
def limpar(): os.system("cls" if os.name == "nt" else "clear")
def sep(): print(cinza("─" * 52))

def cabecalho():
    print(negrito(azul("╔════════════════════════════════════════════════╗")))
    print(negrito(azul("║         SPRINT BOARD GENERATOR                 ║")))
    print(negrito(azul("╚════════════════════════════════════════════════╝")))
    print()

def listar_sprints():
    os.makedirs(DADOS_DIR, exist_ok=True)
    arquivos = sorted(glob.glob(os.path.join(DADOS_DIR, "*.json")))
    if not arquivos:
        return []
    sprints = []
    for a in arquivos:
        try:
            with open(a, encoding="utf-8") as f:
                d = json.load(f)
            sprints.append({"arquivo": a, "nome": d.get("sprint", os.path.basename(a)), "data": d.get("createdAt", "")})
        except:
            pass
    return sprints

def mostrar_sprints(sprints):
    if not sprints:
        print(cinza("  Nenhuma sprint salva ainda."))
    else:
        print(negrito("Sprints existentes:"))
        for i, s in enumerate(sprints, 1):
            data = s["data"][:10] if s["data"] else "?"
            print(f"  {cinza(str(i)+'.')} {s['nome']} {cinza('('+data+')')}")
    print()

def menu_principal(sprints):
    print(negrito("O que deseja fazer?"))
    print(f"  {cinza('1.')} nova sprint com dados do relatorio (Bundle Roteirizacao)")
    print(f"  {cinza('2.')} nova sprint do zero")
    if sprints:
        print(f"  {cinza('3.')} editar sprint existente")
    print()
    opcoes = ["1", "2", "3"] if sprints else ["1", "2"]
    while True:
        v = input(cinza("  opcao: ")).strip()
        if v in opcoes:
            return v
        print(vermelho("  opcao invalida"))

def coletar_massa(col, existentes=None):
    tasks = list(existentes or [])
    print()
    print(negrito(f"  Coluna: {COL_LABELS[col].upper()}"))
    if tasks:
        print(cinza(f"  {len(tasks)} tasks ja existem. Adicionando mais:"))
    print(cinza("  Formato: task | tag  (ex: Corrigir branch | git)"))
    print(cinza("  Tags: bundle git infra motor docs"))
    print(cinza("  Enter vazio para terminar."))
    sep()
    while True:
        try:
            linha = input("  > ").strip()
        except EOFError:
            break
        if not linha:
            break
        if "|" in linha:
            partes = linha.split("|", 1)
            titulo = partes[0].strip()
            tag = partes[1].strip().lower()
            if tag not in TAGS:
                tag = "bundle"
        else:
            titulo = linha
            tag = "bundle"
        if titulo:
            tasks.append({"title": titulo, "tag": f"tag-{tag}"})
            print(verde(f"  + {titulo} [{tag}]"))
    return tasks

def slug(nome):
    s = nome.lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = s.strip("_")
    return s[:40]

def salvar_sprint(sprint_name, cards):
    os.makedirs(DADOS_DIR, exist_ok=True)
    id_seq = 1
    cards_js = {}
    for col in COLS:
        cards_js[col] = []
        for c in cards.get(col, []):
            cards_js[col].append({
                "id": id_seq,
                "title": c["title"],
                "tag": c["tag"],
                "timeLog": {},
                "createdAt": int(time.time() * 1000)
            })
            id_seq += 1
    state = {"sprint": sprint_name, "cards": cards_js, "createdAt": datetime.now().isoformat()}
    nome_arquivo = slug(sprint_name) + ".json"
    caminho = os.path.join(DADOS_DIR, nome_arquivo)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    return caminho

def carregar_todos():
    os.makedirs(DADOS_DIR, exist_ok=True)
    arquivos = sorted(glob.glob(os.path.join(DADOS_DIR, "*.json")))
    sprints = []
    for a in arquivos:
        try:
            with open(a, encoding="utf-8") as f:
                sprints.append(json.load(f))
        except:
            pass
    return sprints

def gerar_board(sprints):
    sprints_json = json.dumps(sprints, ensure_ascii=False)
    base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sprint-board-base.html")
    if os.path.exists(base_path):
        with open(base_path, encoding="utf-8") as f:
            base = f.read()
        inject = _inject_script(sprints_json)
        html = base.replace("</body>", inject + "</body>")
    else:
        html = _html_template(sprints_json)
    with open(BOARD_HTML, "w", encoding="utf-8") as f:
        f.write(html)

def main():
    limpar()
    cabecalho()
    sprints = listar_sprints()
    mostrar_sprints(sprints)
    opcao = menu_principal(sprints)

    if opcao == "1":
        sprint_name = input(cinza("Nome da sprint (Enter = 'Bundle Roteirizacao - Sprint 1'): ")).strip() or "Bundle Roteirizacao - Sprint 1"
        cards = {col: list(CARDS_PADRAO[col]) for col in COLS}
        print()
        print(negrito("Quer adicionar tasks extras?"))
        for col in COLS:
            sep()
            print(f"  {COL_LABELS[col].upper()} — {verde(str(len(cards[col])))} tasks pre-carregadas")
            add = input(cinza("  adicionar mais? (s/n, default=n): ")).strip().lower()
            if add == "s":
                cards[col] = coletar_massa(col, cards[col])

    elif opcao == "2":
        sprint_name = input(cinza("Nome da sprint: ")).strip() or "Sprint 1"
        cards = {}
        for col in COLS:
            sep()
            cards[col] = coletar_massa(col)

    else:
        print()
        for i, s in enumerate(sprints, 1):
            print(f"  {cinza(str(i)+'.')} {s['nome']}")
        while True:
            v = input(cinza("  qual sprint editar (numero): ")).strip()
            if v.isdigit() and 1 <= int(v) <= len(sprints):
                break
            print(vermelho("  invalido"))
        sp = sprints[int(v)-1]
        sprint_name = sp["nome"]
        arq = sp["arquivo"]
        with open(arq, encoding="utf-8") as f:
            data = json.load(f)
        cards = {}
        for col in COLS:
            cards[col] = [{"title": c["title"], "tag": c["tag"]} for c in data["cards"].get(col, [])]
        print()
        print(negrito("Editar coluna:"))
        for col in COLS:
            sep()
            print(f"  {COL_LABELS[col].upper()} — {verde(str(len(cards[col])))} tasks")
            add = input(cinza("  adicionar mais tasks? (s/n, default=n): ")).strip().lower()
            if add == "s":
                cards[col] = coletar_massa(col, cards[col])

    sep()
    print()
    print(negrito("Resumo:"))
    total = 0
    for col in COLS:
        n = len(cards.get(col, []))
        total += n
        cor_n = verde(str(n)) if col == "done" else vermelho(str(n)) if col == "debug" else (amarelo(str(n)) if n > 0 else cinza("0"))
        print(f"  {COL_LABELS[col]:15} {cor_n} tasks")
    print(f"  {'total':15} {negrito(str(total))} tasks")

    print()
    caminho = salvar_sprint(sprint_name, cards)
    print(verde(f"  Sprint salva: {os.path.basename(caminho)}"))

    todas = carregar_todos()
    gerar_board(todas)
    print(verde(f"  Board atualizado: board.html ({len(todas)} sprint(s))"))
    print()

def _inject_script(sprints_json):
    return f"""<script>
const COLS=['todo','doing','done','debug'];
const COL_LABELS={{todo:'a fazer',doing:'fazendo',done:'feito',debug:'debug/erro'}};
const ALL_SPRINTS={sprints_json};
let currentSprint=null;
let dragCardId=null,dragSrcCol=null;

function now(){{return Date.now();}}
function ms2str(ms){{if(!ms||ms<=0)return'—';const h=Math.floor(ms/3600000),m=Math.floor((ms%3600000)/60000);return h>0?h+'h '+m+'m':m+'m';}}
function totalTime(card){{let t=0;const log=card.timeLog||{{}};COLS.forEach(c=>{{t+=(log[c]||0);}});return t;}}

function renderTabs(){{
  const sel=document.getElementById('sprint-selector');
  sel.innerHTML='';
  const all=document.createElement('button');
  all.className='sprint-tab all'+(currentSprint===null?' active':'');
  all.textContent='todas ('+ALL_SPRINTS.length+')';
  all.onclick=()=>selectSprint(null);
  sel.appendChild(all);
  ALL_SPRINTS.forEach((s,i)=>{{
    const btn=document.createElement('button');
    btn.className='sprint-tab'+(currentSprint===i?' active':'');
    const d=s.createdAt?s.createdAt.slice(0,10):'';
    btn.textContent=s.sprint+(d?' ('+d+')':'');
    btn.onclick=()=>selectSprint(i);
    sel.appendChild(btn);
  }});
  document.getElementById('sprint-count').textContent=ALL_SPRINTS.length+' sprint(s)';
}}

function selectSprint(idx){{
  currentSprint=idx;
  renderTabs();
  render();
}}

function getCards(col){{
  if(currentSprint===null){{
    return ALL_SPRINTS.flatMap(s=>
      (s.cards[col]||[]).map(c=>{{
        const tc=totalTime(c);
        return{{...c,_sprint:s.sprint,_tc:tc}};
      }})
    );
  }}
  return (ALL_SPRINTS[currentSprint].cards[col]||[]).map(c=>{{
    const tc=totalTime(c);
    return{{...c,_sprint:ALL_SPRINTS[currentSprint].sprint,_tc:tc}};
  }});
}}

function render(){{
  const formCols=document.querySelectorAll('[id^="form-"]');
  formCols.forEach(f=>f.style.display=currentSprint!==null?'block':'none');
  COLS.forEach(col=>{{
    const container=document.getElementById('cards-'+col);
    container.innerHTML='';
    const list=getCards(col);
    if(list.length===0){{container.innerHTML='<div class="empty">vazio</div>';}}
    else{{
      list.forEach(card=>{{
        const el=document.createElement('div');
        el.className='card';
        el.draggable=currentSprint!==null;
        el.dataset.id=card.id;
        const t=card._tc;
        const showSprint=currentSprint===null;
        el.innerHTML=`<div class="card-title">${{card.title}}</div>
          <div class="card-footer">
            <div style="display:flex;gap:4px;flex-wrap:wrap;align-items:center">
              <span class="tag ${{card.tag}}">${{card.tag.replace('tag-','')}}</span>
              ${{showSprint?`<span class="card-sprint">${{card._sprint}}</span>`:''}}
            </div>
            <div style="display:flex;align-items:center;gap:6px">
              <span class="card-time">&#9201; ${{ms2str(t)}}</span>
              ${{currentSprint!==null?`<button class="card-btn" onclick="deleteCard(${{card.id}},'${{col}}')" title="remover">&#215;</button>`:''}}
            </div>
          </div>`;
        if(currentSprint!==null){{
          el.addEventListener('dragstart',e=>{{dragCardId=card.id;dragSrcCol=col;el.classList.add('dragging');}});
          el.addEventListener('dragend',()=>el.classList.remove('dragging'));
        }}
        container.appendChild(el);
      }});
    }}
    document.getElementById('badge-'+col).textContent=list.length;
  }});
  updateStats();
}}

function updateStats(){{
  const cols=COLS.map(c=>getCards(c));
  const total=cols.reduce((s,l)=>s+l.length,0);
  const done=getCards('done').length;
  const pct=total>0?Math.round(done/total*100):0;
  const allTime=cols.flat().reduce((s,c)=>s+c._tc,0);
  document.getElementById('stats').innerHTML=`
    <div class="stat">total <b>${{total}}</b></div>
    <div class="stat">feito <b>${{done}}</b></div>
    <div class="stat">progresso <b>${{pct}}%</b></div>
    <div class="stat">tempo total <b>${{ms2str(allTime)}}</b></div>
    <div class="stat">debug <b>${{getCards('debug').length}}</b></div>`;
}}

function addCard(col){{
  if(currentSprint===null)return;
  const inp=document.getElementById('inp-'+col);
  const tag=document.getElementById('tag-'+col).value;
  const title=inp.value.trim();
  if(!title)return;
  const id=Date.now();
  ALL_SPRINTS[currentSprint].cards[col].push({{id,title,tag,timeLog:{{}},createdAt:now()}});
  inp.value='';hideForm(col);render();
}}

function deleteCard(id,col){{
  if(currentSprint===null)return;
  if(!confirm('Remover?'))return;
  ALL_SPRINTS[currentSprint].cards[col]=ALL_SPRINTS[currentSprint].cards[col].filter(c=>c.id!==id);
  render();
}}

function showForm(col){{document.getElementById('addform-'+col).classList.add('open');document.querySelector('#form-'+col+' .add-btn').style.display='none';document.getElementById('inp-'+col).focus();}}
function hideForm(col){{document.getElementById('addform-'+col).classList.remove('open');document.querySelector('#form-'+col+' .add-btn').style.display='block';}}
function dragOver(e){{e.preventDefault();e.currentTarget.classList.add('drag-over');}}
function dragLeave(e){{e.currentTarget.classList.remove('drag-over');}}
function drop(e,targetCol){{
  e.preventDefault();e.currentTarget.classList.remove('drag-over');
  if(!dragCardId||dragSrcCol===targetCol||currentSprint===null){{dragCardId=null;dragSrcCol=null;return;}}
  const idx=ALL_SPRINTS[currentSprint].cards[dragSrcCol].findIndex(c=>c.id===dragCardId);
  if(idx===-1)return;
  const card=ALL_SPRINTS[currentSprint].cards[dragSrcCol].splice(idx,1)[0];
  const t=now();
  if(!card.timeLog)card.timeLog={{}};
  if(dragSrcCol==='doing'&&card.doingStart){{card.timeLog.doing=(card.timeLog.doing||0)+(t-card.doingStart);delete card.doingStart;}}
  if(targetCol==='doing')card.doingStart=t;
  ALL_SPRINTS[currentSprint].cards[targetCol].push(card);
  dragCardId=null;dragSrcCol=null;render();
}}

function openReport(){{
  const allCards=COLS.flatMap(col=>getCards(col).map(c=>{{return{{...c,col}}}}));
  if(!allCards.length){{alert('Nenhuma task.');return;}}
  const maxTime=Math.max(...allCards.map(c=>c._tc),1);

  const overviewHTML=ALL_SPRINTS.map(s=>{{
    const total=COLS.reduce((x,c)=>x+(s.cards[c]||[]).length,0);
    const done=(s.cards.done||[]).length;
    const pct=total>0?Math.round(done/total*100):0;
    return`<div class="overview-card"><h3>${{s.sprint}}</h3>
      <div style="font-size:11px;color:var(--text2)">${{done}}/${{total}} concluidas — ${{pct}}%</div>
      <div class="overview-bar"><div class="overview-bar-inner" style="width:${{pct}}%"></div></div></div>`;
  }}).join('');

  const rows=allCards.sort((a,b)=>b._tc-a._tc).map(card=>{{
    const pct=Math.round(card._tc/maxTime*100);
    const barClass=card.col==='done'?'done':card.col==='debug'?'debug':'';
    return`<tr><td>${{card.title}}</td><td><span class="tag ${{card.tag}}">${{card.tag.replace('tag-','')}}</span></td>
      <td style="font-size:10px;color:var(--text2)">${{card._sprint}}</td>
      <td>${{COL_LABELS[card.col]}}</td><td>${{ms2str(card._tc)}}</td>
      <td style="min-width:80px"><div class="bar-wrap"><div class="bar ${{barClass}}" style="width:${{pct}}%"></div></div></td></tr>`;
  }}).join('');

  const totalTime2=allCards.reduce((s,c)=>s+c._tc,0);
  const totalDone=getCards('done').length;
  const totalAll=allCards.length;

  document.getElementById('report-content').innerHTML=`
    <div class="stats" style="margin-bottom:1rem">
      <div class="stat">tasks <b>${{totalAll}}</b></div>
      <div class="stat">concluidas <b>${{totalDone}}</b></div>
      <div class="stat">tempo total <b>${{ms2str(totalTime2)}}</b></div>
      <div class="stat">sprints <b>${{ALL_SPRINTS.length}}</b></div>
    </div>
    <div style="font-size:12px;font-weight:500;margin-bottom:8px;color:var(--text2)">resumo por sprint</div>
    <div class="overview-grid" style="margin-bottom:1.5rem">${{overviewHTML}}</div>
    <div style="font-size:12px;font-weight:500;margin-bottom:8px;color:var(--text2)">todas as tasks</div>
    <table><thead><tr><th>task</th><th>tag</th><th>sprint</th><th>coluna</th><th>tempo</th><th>proporcao</th></tr></thead>
    <tbody>${{rows}}</tbody></table>`;
  document.getElementById('report-modal').classList.add('open');
}}

function closeReport(){{document.getElementById('report-modal').classList.remove('open');}}

function exportSprint(){{
  const data=currentSprint!==null?ALL_SPRINTS[currentSprint]:{{all:ALL_SPRINTS}};
  const blob=new Blob([JSON.stringify(data,null,2)],{{type:'application/json'}});
  const a=document.createElement('a');
  a.href=URL.createObjectURL(blob);
  a.download='sprint-export-'+new Date().toISOString().slice(0,10)+'.json';
  a.click();
}}

document.addEventListener('keydown',e=>{{
  if(e.key==='Escape')closeReport();
  if(e.key==='Enter'&&!e.shiftKey){{
    COLS.forEach(col=>{{
      const inp=document.getElementById('inp-'+col);
      if(document.activeElement===inp){{e.preventDefault();addCard(col);}}
    }});
  }}
}});

renderTabs();
selectSprint(ALL_SPRINTS.length>0?ALL_SPRINTS.length-1:null);
</script>"""

def _html_template(sprints_json):
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sprint Board</title>
<style>
  *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
  :root{{--bg:#f8f8f6;--bg2:#ffffff;--bg3:#f1efe8;--text:#1a1a18;--text2:#5f5e5a;--text3:#9a9994;--border:rgba(0,0,0,0.12);--border2:rgba(0,0,0,0.22);--radius:8px;--radius-lg:12px;--blue:#185fa5;--blue-bg:#e6f1fb;--blue-text:#0c447c;--green:#0f6e56;--green-bg:#e1f5ee;--green-text:#085041;--red:#a32d2d;--red-bg:#fcebeb;--red-text:#791f1f;--amber:#854f0b;--amber-bg:#faeeda;--amber-text:#633806;--purple:#534ab7;--purple-bg:#eeedfe;--purple-text:#3c3489}}
  @media(prefers-color-scheme:dark){{:root{{--bg:#1a1a18;--bg2:#222220;--bg3:#2a2a28;--text:#e8e6dc;--text2:#9a9994;--text3:#6a6965;--border:rgba(255,255,255,0.1);--border2:rgba(255,255,255,0.2);--blue-bg:#0c447c;--blue-text:#b5d4f4;--green-bg:#085041;--green-text:#9fe1cb;--red-bg:#791f1f;--red-text:#f7c1c1;--amber-bg:#633806;--amber-text:#fac775;--purple-bg:#3c3489;--purple-text:#cecbf6}}}}
  body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:var(--bg);color:var(--text);min-height:100vh}}
  .app{{max-width:1280px;margin:0 auto;padding:1.5rem 1rem}}
  .top{{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;margin-bottom:1.25rem}}
  .top-left h1{{font-size:18px;font-weight:500}}
  .top-right{{display:flex;gap:8px;flex-wrap:wrap;align-items:center}}
  .btn{{font-size:12px;padding:6px 14px;border:0.5px solid var(--border2);border-radius:var(--radius);background:var(--bg2);color:var(--text2);cursor:pointer}}
  .btn:hover{{background:var(--bg3)}}
  .btn-primary{{background:var(--blue);color:#fff;border-color:var(--blue)}}
  .sprint-selector{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:1rem;padding-bottom:1rem;border-bottom:0.5px solid var(--border)}}
  .sprint-tab{{font-size:12px;padding:5px 12px;border:0.5px solid var(--border);border-radius:99px;background:var(--bg2);color:var(--text2);cursor:pointer;white-space:nowrap}}
  .sprint-tab:hover{{border-color:var(--border2)}}
  .sprint-tab.active{{background:var(--blue);color:#fff;border-color:var(--blue)}}
  .sprint-tab.all{{background:var(--bg3)}}
  .stats{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:1.25rem}}
  .stat{{background:var(--bg2);border:0.5px solid var(--border);border-radius:var(--radius);padding:6px 12px;font-size:12px;color:var(--text2)}}
  .stat b{{color:var(--text);font-weight:500}}
  .columns{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}}
  @media(max-width:768px){{.columns{{grid-template-columns:1fr 1fr}}}}
  @media(max-width:480px){{.columns{{grid-template-columns:1fr}}}}
  .col{{background:var(--bg3);border-radius:var(--radius-lg);padding:10px;min-height:200px}}
  .col.drag-over{{border:1.5px dashed var(--border2)}}
  .col-head{{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;padding-bottom:8px;border-bottom:0.5px solid var(--border)}}
  .col-title{{font-size:11px;font-weight:500;text-transform:uppercase;letter-spacing:.06em}}
  .col-todo .col-title{{color:var(--text2)}}.col-doing .col-title{{color:var(--blue)}}.col-done .col-title{{color:var(--green)}}.col-debug .col-title{{color:var(--red)}}
  .col-badge{{font-size:11px;background:var(--bg2);border:0.5px solid var(--border);border-radius:99px;padding:1px 7px;color:var(--text2)}}
  .cards{{display:flex;flex-direction:column;gap:6px;min-height:40px}}
  .card{{background:var(--bg2);border:0.5px solid var(--border);border-radius:var(--radius);padding:8px 10px;cursor:grab}}
  .card:hover{{border-color:var(--border2)}}.card.dragging{{opacity:.35}}
  .col-debug .card{{border-left:2.5px solid var(--red);border-radius:0 var(--radius) var(--radius) 0}}
  .col-done .card{{border-left:2.5px solid var(--green);border-radius:0 var(--radius) var(--radius) 0}}
  .card-title{{font-size:12px;font-weight:500;line-height:1.4;margin-bottom:6px;color:var(--text)}}
  .card-footer{{display:flex;align-items:center;justify-content:space-between;gap:6px;flex-wrap:wrap}}
  .card-sprint{{font-size:10px;color:var(--text3);font-style:italic}}
  .tag{{font-size:10px;padding:1px 6px;border-radius:99px;font-weight:500}}
  .tag-bundle{{background:var(--purple-bg);color:var(--purple-text)}}.tag-git{{background:var(--amber-bg);color:var(--amber-text)}}.tag-infra{{background:var(--red-bg);color:var(--red-text)}}.tag-motor{{background:var(--green-bg);color:var(--green-text)}}.tag-docs{{background:var(--blue-bg);color:var(--blue-text)}}
  .card-time{{font-size:10px;color:var(--text3)}}.card-time.active{{color:var(--blue)}}
  .card-actions{{display:flex;gap:4px}}
  .card-btn{{background:none;border:none;cursor:pointer;color:var(--text3);font-size:13px;padding:1px 3px;border-radius:4px}}
  .card-btn:hover{{color:var(--text);background:var(--bg3)}}
  .time-log{{margin-top:6px;border-top:0.5px solid var(--border);padding-top:6px;display:none}}
  .time-log.open{{display:block}}
  .time-row{{display:flex;justify-content:space-between;font-size:10px;color:var(--text2);padding:1px 0}}
  .add-btn{{width:100%;margin-top:8px;font-size:11px;padding:5px;border:0.5px dashed var(--border);border-radius:var(--radius);background:none;color:var(--text3);cursor:pointer;text-align:center}}
  .add-btn:hover{{color:var(--text2);border-color:var(--border2)}}
  .add-form{{margin-top:8px;display:none}}.add-form.open{{display:block}}
  .add-textarea{{width:100%;font-size:12px;padding:6px 8px;border:0.5px solid var(--border);border-radius:var(--radius);background:var(--bg2);color:var(--text);resize:none;font-family:inherit}}
  .add-textarea:focus{{outline:none;border-color:var(--blue)}}
  .add-row{{display:flex;gap:6px;margin-top:6px}}
  .add-select{{font-size:11px;padding:4px 6px;border:0.5px solid var(--border);border-radius:var(--radius);background:var(--bg2);color:var(--text2)}}
  .add-confirm{{font-size:11px;padding:4px 10px;border:0.5px solid var(--border2);border-radius:var(--radius);background:var(--bg2);color:var(--text);cursor:pointer}}
  .add-cancel{{font-size:11px;padding:4px 8px;border:none;background:none;color:var(--text3);cursor:pointer}}
  .empty{{font-size:11px;color:var(--text3);text-align:center;padding:20px 0}}
  .modal-wrap{{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.4);z-index:100;align-items:center;justify-content:center}}
  .modal-wrap.open{{display:flex}}
  .modal{{background:var(--bg2);border:0.5px solid var(--border2);border-radius:var(--radius-lg);padding:1.5rem;width:90%;max-width:720px;max-height:85vh;overflow-y:auto}}
  .modal h2{{font-size:16px;font-weight:500;margin-bottom:1rem}}
  .modal-close{{float:right;background:none;border:none;font-size:18px;cursor:pointer;color:var(--text2)}}
  table{{width:100%;border-collapse:collapse;font-size:12px}}
  th{{text-align:left;padding:6px 8px;font-weight:500;color:var(--text2);border-bottom:0.5px solid var(--border);font-size:11px;text-transform:uppercase;letter-spacing:.04em}}
  td{{padding:6px 8px;border-bottom:0.5px solid var(--border);color:var(--text)}}
  tr:last-child td{{border-bottom:none}}
  .bar-wrap{{background:var(--bg3);border-radius:99px;height:6px;width:100%}}
  .bar{{height:6px;border-radius:99px;background:var(--blue)}}.bar.done{{background:var(--green)}}.bar.debug{{background:var(--red)}}
  .chart-row{{display:flex;align-items:center;gap:8px;margin-bottom:6px}}
  .chart-label{{font-size:11px;color:var(--text2);width:200px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;flex-shrink:0}}
  .chart-bar-wrap{{flex:1;background:var(--bg3);border-radius:99px;height:14px}}
  .chart-bar{{height:14px;border-radius:99px;background:var(--blue);min-width:2px}}
  .chart-val{{font-size:11px;color:var(--text2);width:50px;text-align:right;flex-shrink:0}}
  .overview-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px;margin-bottom:1.5rem}}
  .overview-card{{background:var(--bg3);border-radius:var(--radius-lg);padding:12px;border:0.5px solid var(--border)}}
  .overview-card h3{{font-size:13px;font-weight:500;margin-bottom:8px;color:var(--text)}}
  .overview-bar{{height:6px;border-radius:99px;background:var(--bg2);margin-top:6px}}
  .overview-bar-inner{{height:6px;border-radius:99px;background:var(--green)}}
</style>
</head>
<body>
<div class="app">
  <div class="top">
    <div class="top-left"><h1>Sprint Board</h1></div>
    <div class="top-right">
      <span id="sprint-count" style="font-size:12px;color:var(--text2)"></span>
      <button class="btn" onclick="openReport()">&#9776; relatorio</button>
      <button class="btn" onclick="exportSprint()">&#8595; exportar sprint</button>
    </div>
  </div>

  <div class="sprint-selector" id="sprint-selector"></div>
  <div class="stats" id="stats"></div>

  <div class="columns">
    <div class="col col-todo" id="col-todo" ondragover="dragOver(event)" ondrop="drop(event,'todo')" ondragleave="dragLeave(event)">
      <div class="col-head"><span class="col-title">a fazer</span><span class="col-badge" id="badge-todo">0</span></div>
      <div class="cards" id="cards-todo"></div>
      <div id="form-todo"><button class="add-btn" onclick="showForm('todo')">+ nova task</button>
        <div class="add-form" id="addform-todo"><textarea class="add-textarea" id="inp-todo" rows="2" placeholder="Descreve a task..."></textarea>
          <div class="add-row"><select class="add-select" id="tag-todo"><option value="tag-bundle">bundle</option><option value="tag-git">git</option><option value="tag-infra">infra</option><option value="tag-motor">motor</option><option value="tag-docs">docs</option></select>
          <button class="add-confirm" onclick="addCard('todo')">adicionar</button><button class="add-cancel" onclick="hideForm('todo')">cancelar</button></div></div></div>
    </div>
    <div class="col col-doing" id="col-doing" ondragover="dragOver(event)" ondrop="drop(event,'doing')" ondragleave="dragLeave(event)">
      <div class="col-head"><span class="col-title">fazendo</span><span class="col-badge" id="badge-doing">0</span></div>
      <div class="cards" id="cards-doing"></div>
      <div id="form-doing"><button class="add-btn" onclick="showForm('doing')">+ nova task</button>
        <div class="add-form" id="addform-doing"><textarea class="add-textarea" id="inp-doing" rows="2" placeholder="Descreve a task..."></textarea>
          <div class="add-row"><select class="add-select" id="tag-doing"><option value="tag-bundle">bundle</option><option value="tag-git">git</option><option value="tag-infra">infra</option><option value="tag-motor">motor</option><option value="tag-docs">docs</option></select>
          <button class="add-confirm" onclick="addCard('doing')">adicionar</button><button class="add-cancel" onclick="hideForm('doing')">cancelar</button></div></div></div>
    </div>
    <div class="col col-done" id="col-done" ondragover="dragOver(event)" ondrop="drop(event,'done')" ondragleave="dragLeave(event)">
      <div class="col-head"><span class="col-title">feito</span><span class="col-badge" id="badge-done">0</span></div>
      <div class="cards" id="cards-done"></div>
      <div id="form-done"><button class="add-btn" onclick="showForm('done')">+ nova task</button>
        <div class="add-form" id="addform-done"><textarea class="add-textarea" id="inp-done" rows="2" placeholder="Descreve a task..."></textarea>
          <div class="add-row"><select class="add-select" id="tag-done"><option value="tag-bundle">bundle</option><option value="tag-git">git</option><option value="tag-infra">infra</option><option value="tag-motor">motor</option><option value="tag-docs">docs</option></select>
          <button class="add-confirm" onclick="addCard('done')">adicionar</button><button class="add-cancel" onclick="hideForm('done')">cancelar</button></div></div></div>
    </div>
    <div class="col col-debug" id="col-debug" ondragover="dragOver(event)" ondrop="drop(event,'debug')" ondragleave="dragLeave(event)">
      <div class="col-head"><span class="col-title">debug / erro</span><span class="col-badge" id="badge-debug">0</span></div>
      <div class="cards" id="cards-debug"></div>
      <div id="form-debug"><button class="add-btn" onclick="showForm('debug')">+ novo erro</button>
        <div class="add-form" id="addform-debug"><textarea class="add-textarea" id="inp-debug" rows="2" placeholder="Descreve o erro..."></textarea>
          <div class="add-row"><select class="add-select" id="tag-debug"><option value="tag-infra">infra</option><option value="tag-bundle">bundle</option><option value="tag-git">git</option><option value="tag-motor">motor</option><option value="tag-docs">docs</option></select>
          <button class="add-confirm" onclick="addCard('debug')">adicionar</button><button class="add-cancel" onclick="hideForm('debug')">cancelar</button></div></div></div>
    </div>
  </div>
</div>

<div class="modal-wrap" id="report-modal" onclick="if(event.target===this)closeReport()">
  <div class="modal"><button class="modal-close" onclick="closeReport()">&#215;</button><h2>Relatorio</h2><div id="report-content"></div></div>
</div>

{_inject_script(sprints_json)}
</body>
</html>"""

if __name__ == "__main__":
    main()
