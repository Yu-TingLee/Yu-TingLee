#!/bin/sh
# Re-render README.md via GitHub's markdown API into /tmp/yt-preview.html
cd "$(dirname "$0")/../.." || exit 1
body=$(jq -n --rawfile t README.md '{text:$t, mode:"gfm", context:"Yu-TingLee/Yu-TingLee"}' | gh api markdown --input -) || exit 1
cat > /tmp/yt-preview.html <<HTML
<!doctype html><html><head><meta charset="utf-8"><base href="file://$PWD/">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.5.1/github-markdown.min.css">
<style>body{background:#fff}@media (prefers-color-scheme:dark){body{background:#0d1117}.markdown-body{border-color:#30363d!important}}.markdown-body{max-width:900px;margin:40px auto;padding:32px;border:1px solid #d0d7de;border-radius:6px}</style></head>
<body><article class="markdown-body">$body</article></body></html>
HTML
echo "updated /tmp/yt-preview.html, press Cmd+R in browser"
