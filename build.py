"""Build README.md and prompts/ from data/: the seed collections plus data/extra.json (works added by hand, e.g. on a model's launch day).
    python3 build.py
data/extra.json: [{"url": "...", "author": "...", "title": "...", "section": "scene|game_interactive|...", "prompt": "... or null", "likes": 123, "model": "Fable 5.5", "new": true}]   new = goes under Next model watch"""
import csv, json, re, collections, os
H = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(H, 'data')
pid = lambda u: re.search(r'status/(\d+)', u).group(1) if u and 'status/' in u else None
eng = {r['post_id']: int(r['likes']) for r in csv.DictReader(open(f'{D}/case-engagement-observed.csv')) if r['likes'].isdigit()}
titles = json.load(open(f'{D}/titles.json'))
TAG = collections.defaultdict(set)
KW = [('blender', 'Blender'), ('three.js', 'Three.js'), ('threejs', 'Three.js'), ('webgl', 'Shader'), ('shader', 'Shader'), ('unreal', 'Unreal'), ('tripo', 'Tripo'), ('pybevy', 'Bevy'), ('godot', 'Godot')]
def kw(p, text):
    t = (text or '').lower()
    for k, v in KW:
        if k in t: TAG[p].add(v)
for r in csv.DictReader(open(f'{D}/cases.csv')):
    q = pid(r['source_url'])
    if q: kw(q, r['creator_disclosure'])
E = {}
for r in csv.DictReader(open(f'{D}/domain-style.csv')):
    if '3d_render' not in (r['style'], r['style2']) or r['opus_made'] == 'no': continue
    p = pid(r['post_url'])
    if p and p not in E: E[p] = dict(url=r['post_url'], author=r['author'].lstrip('@'), title=r['topic_en'], domain=r['domain'], prompt=None, likes=eng.get(p)); kw(p, r['topic_en'])
for x in json.load(open(f'{D}/videos.json')):
    if not (x['category'] == '3d' or 'threejs' in x.get('tech_tags', [])): continue
    p = pid(x['post_url'])
    if not p: continue
    if p not in E and x['category'] != '3d': continue
    for t in x.get('tech_tags', []):
        if t in ('threejs',): TAG[p].add('Three.js')
        if t in ('shader', 'webgl'): TAG[p].add('Shader')
        if t in ('playable',): TAG[p].add('Playable')
    kw(p, x.get('prompt'))
    e = E.setdefault(p, dict(url=x['post_url'], author=x['author'], title=None, domain='game_interactive' if x['category'] == 'interactive' else 'scene', likes=eng.get(p)))
    if not x.get('prompt_partial') and x.get('prompt'): e['prompt'] = x['prompt']; e['slug'] = x['slug']
    if not e.get('title'): e['title'] = titles.get(x['slug'])
extra = json.load(open(f'{D}/extra.json')) if os.path.exists(f'{D}/extra.json') else []
NEW = []
for x in extra:
    e = dict(url=x['url'], author=x['author'], title=x['title'], domain=x.get('section', 'scene'), prompt=x.get('prompt'), likes=x.get('likes'), model=x.get('model'))
    if e['prompt']: e['slug'] = re.sub(r'\W+', '-', f"{x['author']}-{pid(x['url'])}").lower()
    TAG[pid(x['url'])].update(x.get('tools', [])); kw(pid(x['url']), x['title'])
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
    tg = ''.join(f' `{t}`' for t in sorted(TAG.get(pid(e['url']), ())))
    return f"- [{e['title'].strip()}]({e['url']}) — [@{e['author']}](https://x.com/{e['author']}){tg}{md}{pr}{lk}"
os.makedirs(f'{H}/prompts', exist_ok=True)
for e in E.values():
    if e.get('prompt'):
        open(f"{H}/prompts/{e['slug']}.md", 'w').write(f"# {e['title']}\n\nBy [@{e['author']}](https://x.com/{e['author']}) · [original post]({e['url']})\n\n## Prompt\n\n```\n{e['prompt'].strip()}\n```\n")
anchor = lambda t: t.lower().replace(' & ', '--').replace(' ', '-')
top = sorted([e for e in E.values() if e.get('likes')], key=lambda e: -e['likes'])[:15]
n, npr = len(E), sum(1 for e in E.values() if e.get('prompt'))
md = ["# Awesome Claude 3D Videos [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)", "", "![Awesome Claude 3D Videos](assets/banner.jpg)", "",
      f"3D scenes, worlds, games and films made by Claude — written as code (Three.js, WebGL, shaders, Blender Python) and rendered to video. **{n} works**, each linked to the creator's original post; **{npr} with the prompt** the creator shared.",
      "", "When a new Claude model lands, its first 3D works are added here within a day.", "", "**Make one with your own product, photos or footage → [ultramotion.ai](https://ultramotion.ai/?utm_source=github&utm_medium=readme&utm_campaign=awesome-claude-3d-videos)**", "", "## Contents", "- [Next model watch](#next-model-watch)", "- [Editor's picks](#editors-picks)", "- [Most liked](#most-liked)"]
md += [f"- [{t}](#{anchor(t)}) ({len(by[k])})" for k, t in SEC if by[k]] + ["- [What gets in](#what-gets-in)", "- [Credits](#credits)", "", "Tags show what the creator said they used: `Blender` `Three.js` `Shader` (WebGL/GLSL) `Unreal` `Tripo` `Bevy` `Godot` `Playable` (you can play it in a browser). No tag means the creator didn't say.", "", "## Next model watch", ""]
md += [line(e) for e in NEW] if NEW else ["Claude Fable 5.5 and the next Opus are reported to be close, with early demos in Three.js and Blender. First 3D works from launch day go here."]
def tcell(e):
    p_ = pid(e['url']); tg = ' '.join(f'<code>{t}</code>' for t in sorted(TAG.get(p_, ())))
    pr = f' · <a href="prompts/{e["slug"]}.md">prompt</a>' if e.get('prompt') else ''
    lk = f' · ♥ {e["likes"]:,}' if e.get('likes') else ''
    return (f'<td valign="top" width="25%"><a href="{e["url"]}"><img src="previews/thumbs/{p_}.jpg" width="200" alt=""></a><br>'
            f'<a href="{e["url"]}">{e["title"].strip()}</a><br><sub>@{e["author"]}{lk}{pr}<br>{tg}</sub></td>')
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
    if not by[k]: continue
    items = sorted(by[k], key=lambda e: -(e.get('likes') or 0))
    withimg = [e for e in items if os.path.exists(os.path.join(H, f"previews/thumbs/{pid(e['url'])}.jpg"))]
    md += ["", f"## {t}", "", "<table>"] + ["<tr>" + "".join(tcell(e) for e in withimg[i:i + 4]) + "</tr>" for i in range(0, len(withimg), 4)] + ["</table>", ""]
    md += [line(e) for e in items if e not in withimg]
md += ["", "## What gets in", "",
       "- Made with Claude (the creator says so), with a real 3D space in the picture: objects with volume and light, and a camera that can move through them.",
       "- Out: flat motion graphics drawn with a 3D library (text, logos, cards on a plane facing the camera), plain screen recordings of an interface, and model-vs-model comparisons with no finished piece.",
       "- Editor's picks are chosen by eye for finish and beauty; Most liked is by likes on the original post.", ""]
md += ["", "## Credits", "", "Every video and prompt belongs to its creator, linked from each entry; previews are 3-second excerpts shown only to point to the original post. If you made one of these and want it changed or removed, open an issue.", "",
       "Seed data: [athemeroy/awesome-claude-5-5-videos](https://github.com/athemeroy/awesome-claude-5-5-videos) (CC BY 4.0) and [yihui-dev/awesome-opus5-5-videos](https://github.com/yihui-dev/awesome-opus5-5-videos) (MIT).", "",
       "Know a Claude-made 3D video that belongs here? [Add it](https://github.com/sunsiyuan/awesome-claude-3d-videos/issues/new?template=add-a-work.yml) — see [CONTRIBUTING](CONTRIBUTING.md)."]
open(f'{H}/README.md', 'w').write('\n'.join(md) + '\n')
ZH = [("- [Next model watch](#next-model-watch)", "- [新模型首发](#新模型首发)"), ("- [Editor's picks](#editors-picks)", "- [精选](#精选)"), ("- [Most liked](#most-liked)", "- [最受欢迎](#最受欢迎)"), ("- [What gets in](#what-gets-in)", "- [收录标准](#收录标准)"), ("- [Credits](#credits)", "- [署名](#署名)"),
      ("3D scenes, worlds, games and films made by Claude — written as code (Three.js, WebGL, shaders, Blender Python) and rendered to video.", "Claude 做的 3D 场景、世界、游戏和短片——用代码写出来（Three.js、WebGL、着色器、Blender Python）再渲成视频。"),
      ("works**, each linked to the creator's original post;", "条作品**，每条都链到作者的原帖；"), ("with the prompt** the creator shared.", "条附作者公开的提示词**。"),
      ("When a new Claude model lands, its first 3D works are added here within a day.", "新的 Claude 模型一发布，第一批 3D 作品会在一天内收进来。"),
      ("**Make one with your own product, photos or footage →", "**用你自己的产品、照片或素材做一条 →"),
      ("Tags show what the creator said they used:", "标签是作者自己说用了什么："), ("(WebGL/GLSL)", "（WebGL/GLSL）"), ("(you can play it in a browser). No tag means the creator didn't say.", "（能在浏览器里玩）。没标签表示作者没说。"),
      ("## Contents", "## 目录"), ("## Next model watch", "## 新模型首发"), ("## Editor's picks", "## 精选"), ("The most beautiful and finished ones, picked by eye, not by likes.", "按画面挑的最精美、最完整的作品，不看点赞。"),
      ("## Most liked", "## 最受欢迎"), ("## What gets in", "## 收录标准"),
      ("Claude Fable 5.5 and the next Opus are reported to be close, with early demos in Three.js and Blender. First 3D works from launch day go here.", "据报道 Claude Fable 5.5 和下一代 Opus 都快了，泄露的演示是 Three.js 和 Blender。发布当天的第一批 3D 作品放这里。"),
      ("- Made with Claude (the creator says so), with a real 3D space in the picture: objects with volume and light, and a camera that can move through them.", "- 作者说明是 Claude 做的，画面里是真的 3D 空间：有体积和光影的物体，镜头能在里面移动。"),
      ("- Out: flat motion graphics drawn with a 3D library (text, logos, cards on a plane facing the camera), plain screen recordings of an interface, and model-vs-model comparisons with no finished piece.", "- 不收：用 3D 库画的平面动效（正对镜头的文字、logo、卡片）、单纯的界面录屏、没有成品的模型对比。"),
      ("- Editor's picks are chosen by eye for finish and beauty; Most liked is by likes on the original post.", "- 精选按画面的完成度和美感挑；最受欢迎按原帖点赞数排。"),
      ("## Credits", "## 署名"), ("Every video and prompt belongs to its creator, linked from each entry; previews are 3-second excerpts shown only to point to the original post. If you made one of these and want it changed or removed, open an issue.", "每条视频和提示词都归作者所有，每条都链到原帖；预览是 3 秒片段，只用来指向原帖。作者想修改或下架，提一个 issue 即可。"),
      ("Seed data:", "初始数据："), ("Know a Claude-made 3D video that belongs here?", "知道应该收进来的 Claude 3D 作品？"), ("— see", "——见")]
zh = '\n'.join(md)
for a, b in ZH: zh = zh.replace(a, b)
for k, t in SEC: pass
zh = zh.replace('# Awesome Claude 3D Videos', '# Awesome Claude 3D Videos（中文）', 1)
lang = '[English](README.md) · [中文](README.zh.md)'
open(f'{H}/README.zh.md', 'w').write(zh.replace('![Awesome Claude 3D Videos](assets/banner.jpg)', '![Awesome Claude 3D Videos](assets/banner.jpg)\n\n' + lang, 1) + '\n')
en = open(f'{H}/README.md').read().replace('![Awesome Claude 3D Videos](assets/banner.jpg)', '![Awesome Claude 3D Videos](assets/banner.jpg)\n\n' + lang, 1)
open(f'{H}/README.md', 'w').write(en)
print(n, 'works,', npr, 'prompts')
