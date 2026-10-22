"""Build README.md and prompts/ from data/: the seed collections plus data/extra.json (works added by hand, e.g. on a model's launch day).
    python3 build.py
data/extra.json: [{"url": "...", "author": "...", "title": "...", "section": "scene|game_interactive|...", "prompt": "... or null", "likes": 123, "model": "Fable 5.5", "new": true}]   new = goes under Next model watch"""
import csv, json, re, collections, os
H = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(H, 'data')
pid = lambda u: re.search(r'status/(\d+)', u).group(1) if u and 'status/' in u else None
eng = {r['post_id']: int(r['likes']) for r in csv.DictReader(open(f'{D}/case-engagement-observed.csv')) if r['likes'].isdigit()}
titles = json.load(open(f'{D}/titles.json'))
E = {}
for r in csv.DictReader(open(f'{D}/domain-style.csv')):
    if '3d_render' not in (r['style'], r['style2']) or r['opus_made'] == 'no': continue
    p = pid(r['post_url'])
    if p and p not in E: E[p] = dict(url=r['post_url'], author=r['author'].lstrip('@'), title=r['topic_en'], domain=r['domain'], prompt=None, likes=eng.get(p))
for x in json.load(open(f'{D}/videos.json')):
    if not (x['category'] == '3d' or 'threejs' in x.get('tech_tags', [])): continue
    p = pid(x['post_url'])
    if not p: continue
    if p not in E and x['category'] != '3d': continue
    e = E.setdefault(p, dict(url=x['post_url'], author=x['author'], title=None, domain='game_interactive' if x['category'] == 'interactive' else 'scene', likes=eng.get(p)))
    if not x.get('prompt_partial') and x.get('prompt'): e['prompt'] = x['prompt']; e['slug'] = x['slug']
    if not e.get('title'): e['title'] = titles.get(x['slug'])
extra = json.load(open(f'{D}/extra.json')) if os.path.exists(f'{D}/extra.json') else []
NEW = []
for x in extra:
    e = dict(url=x['url'], author=x['author'], title=x['title'], domain=x.get('section', 'scene'), prompt=x.get('prompt'), likes=x.get('likes'), model=x.get('model'))
    if e['prompt']: e['slug'] = re.sub(r'\W+', '-', f"{x['author']}-{pid(x['url'])}").lower()
    old = E.get(pid(x['url']))
    if old and not e['prompt'] and old.get('prompt'): e['prompt'], e['slug'] = old['prompt'], old['slug']
    if old and not e.get('likes'): e['likes'] = old.get('likes')
    E[pid(x['url'])] = e
    if x.get('new'): NEW.append(e)
cur = json.load(open(f'{D}/curation.json')) if os.path.exists(f'{D}/curation.json') else {'picks': [], 'drop': []}
E = {p: e for p, e in E.items() if e.get('title') and p not in cur['drop']}
SEC = [('game_interactive', 'Games & interactive worlds'), ('scene', 'Scenes & worlds'), ('art_abstract', 'Art & generative'), ('product_ad', 'Products & launches'),
       ('education_science', 'Science & explainers'), ('history_culture', 'History & culture'), ('story_short', 'Short stories'), ('music_video', 'Music videos'),
       ('humor_meme', 'Humor'), ('data_viz', 'Data'), ('ai_self_meta', 'AI about itself'), ('other', 'Other')]
by = collections.defaultdict(list)
for e in E.values(): by[e['domain'] if e['domain'] in dict(SEC) else 'other'].append(e)
def line(e):
    pr = f" · [prompt](prompts/{e['slug']}.md)" if e.get('prompt') else ''
    lk = f" · ♥ {e['likes']:,}" if e.get('likes') else ''
    md = f" · {e['model']}" if e.get('model') else ''
    return f"- [{e['title'].strip()}]({e['url']}) — [@{e['author']}](https://x.com/{e['author']}){md}{pr}{lk}"
os.makedirs(f'{H}/prompts', exist_ok=True)
for e in E.values():
    if e.get('prompt'):
        open(f"{H}/prompts/{e['slug']}.md", 'w').write(f"# {e['title']}\n\nBy [@{e['author']}](https://x.com/{e['author']}) · [original post]({e['url']})\n\n## Prompt\n\n```\n{e['prompt'].strip()}\n```\n")
anchor = lambda t: t.lower().replace(' & ', '--').replace(' ', '-')
top = sorted([e for e in E.values() if e.get('likes')], key=lambda e: -e['likes'])[:15]
n, npr = len(E), sum(1 for e in E.values() if e.get('prompt'))
md = ["# Awesome Claude 3D Videos", "",
      f"3D scenes, worlds, games and films made by Claude — written as code (Three.js, WebGL, shaders, Blender Python) and rendered to video. **{n} works**, each linked to the creator's original post; **{npr} with the prompt** the creator shared.",
      "", "When a new Claude model lands, its first 3D works are added here within a day.", "", "**Make one with your own product, photos or footage → [ultramotion.ai](https://ultramotion.ai/?utm_source=github&utm_medium=readme&utm_campaign=awesome-claude-3d-videos)**", "", "## Contents", "- [Next model watch](#next-model-watch)", "- [Editor's picks](#editors-picks)", "- [Most liked](#most-liked)"]
md += [f"- [{t}](#{anchor(t)}) ({len(by[k])})" for k, t in SEC if by[k]] + ["- [Credits](#credits)", "", "## Next model watch", ""]
md += [line(e) for e in NEW] if NEW else ["Claude Fable 5.5 and the next Opus are reported to be close, with early demos in Three.js and Blender. First 3D works from launch day go here."]
def cell(e):
    g = f"previews/{pid(e['url'])}.gif"
    img = f'<a href="{e["url"]}"><img src="{g}" width="260" alt="{e["title"]}"></a><br>' if os.path.exists(os.path.join(H, g)) else ''
    return f'<td valign="top" width="33%">{img}<a href="{e["url"]}">{e["title"]}</a><br><sub>@{e["author"]}{" · ♥ " + format(e["likes"], ",") if e.get("likes") else ""}</sub></td>'
top = sorted([e for e in E.values() if e.get('likes')], key=lambda e: -e['likes'])[:30]
grid = [e for e in top if os.path.exists(os.path.join(H, f"previews/{pid(e['url'])}.gif"))][:24]
picks = [E[p] for p in cur['picks'] if p in E]
md += ["", "## Editor's picks", "", "The most beautiful and finished ones, picked by eye, not by likes.", "", "<table>"] + ["<tr>" + "".join(cell(e) for e in picks[i:i + 3]) + "</tr>" for i in range(0, len(picks), 3)] + ["</table>"]
md += ["", "## Most liked", "", "<table>"] + ["<tr>" + "".join(cell(e) for e in grid[i:i + 3]) + "</tr>" for i in range(0, len(grid), 3)] + ["</table>", ""] + [line(e) for e in top if e not in grid]
for k, t in SEC:
    if by[k]: md += ["", f"## {t}", ""] + [line(e) for e in sorted(by[k], key=lambda e: -(e.get('likes') or 0))]
md += ["", "## Credits", "", "Every video and prompt belongs to its creator, linked from each entry; previews are 3-second excerpts shown only to point to the original post. If you made one of these and want it changed or removed, open an issue.", "",
       "Seed data: [athemeroy/awesome-claude-5-5-videos](https://github.com/athemeroy/awesome-claude-5-5-videos) (CC BY 4.0) and [yihui-dev/awesome-opus5-5-videos](https://github.com/yihui-dev/awesome-opus5-5-videos) (MIT).", "",
       "Know a Claude-made 3D video that belongs here? Open a pull request with the link."]
open(f'{H}/README.md', 'w').write('\n'.join(md) + '\n'); print(n, 'works,', npr, 'prompts')
