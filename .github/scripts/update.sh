#!/bin/sh
# Rebuild both slideshows + browser preview.
#   photos/  -> assets/photos.webp  (jpg/png, sorted by filename)
#   papers/  -> assets/papers.webp  (pdf first page, or png/jpg screenshots)
cd "$(dirname "$0")/../.." || exit 1
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT

photos=$(find photos -maxdepth 1 -type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' \) | sort)
[ -n "$photos" ] && echo "$photos" | tr '\n' '\0' | xargs -0 python3 -I .github/scripts/slideshow.py assets/photos.webp photo

pages=""
for f in $(find papers -maxdepth 1 -type f | sort | tr ' ' '\001'); do
  f=$(echo "$f" | tr '\001' ' ')
  case "$(echo "$f" | tr A-Z a-z)" in
    *.pdf) png="$tmp/$(basename "$f").png"; sips -s format png "$f" --out "$png" -Z 1600 >/dev/null && pages="$pages$png\n" ;;
    *.png|*.jpg|*.jpeg) pages="$pages$f\n" ;;
  esac
done
[ -n "$pages" ] && printf "$pages" | tr '\n' '\0' | xargs -0 python3 -I .github/scripts/slideshow.py assets/papers.webp page

.github/scripts/preview.sh
