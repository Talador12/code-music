# code-music web player

Open `index.html` in a browser after running `make songs-wav` and `make scales`.

The player reads from `../../dist/` (relative to this file).

To serve locally:
```bash
cd docs/web
python3 -m http.server 8000
# open http://localhost:8000
```

GitHub Pages: enable Pages on the `main` branch, set source to `/docs`.
The player will be at https://talador12.github.io/code-music/web/
