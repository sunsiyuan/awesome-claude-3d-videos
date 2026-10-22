# Contributing

Thanks for adding to the list. One work per issue or pull request.

## What gets in
- Made with Claude, and the creator says so.
- A real 3D space in the picture: objects with volume and light, and a camera that can move through them.
- Not in: flat motion graphics drawn with a 3D library, plain screen recordings of an interface, model-vs-model comparisons with no finished piece.

## Easiest: open an issue
Use the **Add a work** issue form: the link to the original post, a short title, what it was made with, and the prompt if the creator shared one.

## Pull request
Add one object to `data/extra.json`:

```json
{"url": "https://x.com/<creator>/status/<id>", "author": "<creator>", "title": "Short title in sentence case",
 "section": "scene", "tools": ["Blender"], "prompt": null, "likes": null}
```

`section` is one of: `game_interactive`, `scene`, `art_abstract`, `product_ad`, `education_science`, `history_culture`, `story_short`, `music_video`, `humor_meme`, `data_viz`, `ai_self_meta`.
`tools` only lists what the creator said they used. Then run `python3 build.py` and commit the regenerated README.

## Creators
Every work belongs to its creator. If one of yours is here and you want it changed or removed, open an issue and it will be done.
