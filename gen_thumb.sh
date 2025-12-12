#!/bin/sh
set -eu

usage() {
  cat <<'EOF'
Usage: gen_thumb.sh [--skip-existing|--replace-existing] [--time 1] DIR
Output: /path/to/video.ext -> /path/to/video.jpg  (alongside)
EOF
}

mode="replace"
ts="1"

while [ $# -gt 0 ]; do
  case "$1" in
    --skip-existing) mode="skip"; shift ;;
    --replace-existing) mode="replace"; shift ;;
    --time) ts="${2:?missing value}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    --) shift; break ;;
    -*) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
    *) break ;;
  esac
done

dir="${1:-}"
[ -n "$dir" ] || { usage >&2; exit 2; }
[ -d "$dir" ] || { echo "Not a directory: $dir" >&2; exit 2; }

command -v ffmpeg >/dev/null 2>&1 || { echo "ffmpeg not found in PATH" >&2; exit 127; }

find "$dir" -type f \( \
  -iname '*.mp4' -o -iname '*.mkv' -o -iname '*.mov' -o -iname '*.webm' -o -iname '*.avi' -o \
  -iname '*.m4v' -o -iname '*.mpg' -o -iname '*.mpeg' -o -iname '*.wmv' -o -iname '*.flv' -o \
  -iname '*.3gp' \
\) -print0 |
while IFS= read -r -d '' f; do
  base="${f%.*}"
  out="${base}.jpg"
  dirn=$(dirname -- "$f")
  bn=$(basename -- "$base")
  tmp="${dirn}/.${bn}.jpg.tmp.$$"   # hidden temp in same dir

  if [ "$mode" = "skip" ] && [ -e "$out" ]; then
    printf 'skip: %s\n' "$out"
    continue
  fi

  if ffmpeg -hide_banner -loglevel error \
      -ss "$ts" -i "$f" \
      -frames:v 1 -vf "scale=480:-1" \
      -q:v 2 -f mjpeg -y "$tmp"; then
    mv -f "$tmp" "$out"
    printf 'ok:   %s\n' "$out"
  else
    rm -f "$tmp" 2>/dev/null || true
    printf 'fail: %s\n' "$f" >&2
  fi
done
