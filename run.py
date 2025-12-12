import argparse
from pathlib import Path
import json
import subprocess

from PIL import Image, UnidentifiedImageError

IMG_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tif", ".tiff", ".heic", ".heif"}
VIDEO_EXTS = {".mov"}

def iter_image_paths(inputs: list[str], recursive: bool):
    for s in inputs:
        p = Path(s)
        if p.is_file():
            yield p
        elif p.is_dir():
            it = p.rglob("*") if recursive else p.glob("*")
            for fp in it:
                if fp.is_file():
                    yield fp
        else:
            # allow globs like "./imgs/*.png"
            for fp in Path().glob(s):
                if fp.is_file():
                    yield fp

def video_dimensions(path: str | Path) -> tuple[int, int]:
    path = str(path)
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "json",
        path,
    ]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.strip() or "ffprobe failed")

    data = json.loads(p.stdout)
    streams = data.get("streams", [])
    if not streams:
        raise RuntimeError("no video stream found")

    w = streams[0].get("width")
    h = streams[0].get("height")
    if not isinstance(w, int) or not isinstance(h, int):
        raise RuntimeError("could not read width/height from ffprobe output")
    return w, h

def is_probably_image(path: Path) -> bool:
    return path.suffix.lower() in IMG_EXTS

def is_probably_video(path: Path) -> bool:
    return path.suffix.lower() in VIDEO_EXTS

def main():
    ap = argparse.ArgumentParser(description="Print dimensions of images on disk.")
    ap.add_argument("paths", nargs="+", help="Image file(s), directory(ies), or glob(s)")
    ap.add_argument("-r", "--recursive", action="store_true", help="Recurse into directories")
    ap.add_argument("--all", action="store_true", help="Try to open all files, not just common image extensions")
    args = ap.parse_args()

    seen = set()
    for path in iter_image_paths(args.paths, args.recursive):
        path = path.resolve()
        if path in seen:
            continue
        seen.add(path)

        isimg = is_probably_image(path)
        isvid = is_probably_video(path)

        if not args.all and not isimg and not isvid:
            continue

        try:
            if isimg:
                with Image.open(path) as im:
                    w, h = im.size
                    # Some formats may be rotated via EXIF; size is raw pixel dimensions.
                    print(f"{path}\n{w}x{h}")
                    dirname = path.parent.name
                    filename = path.name
                    print(f"""
{{{{< figure 
    thumb="https://coosisv.cc/cdn-cgi/image/width=480,h_480,quality=low,format=auto/https://coosisv.cc/{dirname}/{filename}"
    link="https://coosisv.cc/cdn-cgi/image/quality=high,format=auto/https://coosisv.cc/{dirname}/{filename}"
    size="1316x1347"
    caption="CAPTION HERE"
>}}}}\n""")

            elif isvid:
                dirname = path.parent.name
                filename = path.name
                thumb_name = path.stem + ".jpg"
                w, h = video_dimensions(path)
                print(f"""
{{{{< figure 
    thumb="https://coosisv.cc/cdn-cgi/image/width=480,h_480,quality=low,format=auto/https://coosisv.cc/{dirname}/{thumb_name}"
    link="https://coosisv.cc/{dirname}/{filename}"
    size="{w}x{h}"
    caption="CAPTION HERE"
>}}}}\n""")

            print("-" * 40)
        except (UnidentifiedImageError, OSError) as e:
            # Skip non-images or unreadable files
            print(f"{path}\tERROR: {e}")

if __name__ == "__main__":
    main()
