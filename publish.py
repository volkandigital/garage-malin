"""Publie le carrousel du jour sur Instagram (API Instagram via Facebook Login, page « Le Garage »).
Lancé par GitHub Actions. Variables d'env : IG_TOKEN (jeton de la page, sans expiration), GITHUB_REPOSITORY, COMMIT_SHA.
Usage : python3 publish.py [AAAA-MM-JJ] [--force]
"""
import json, os, sys, time, pathlib, urllib.request, urllib.parse
from datetime import datetime
from zoneinfo import ZoneInfo

API = "https://graph.facebook.com/v25.0"
IG_USER_ID = "17841474308617997"  # @legaragemalin
ROOT = pathlib.Path(__file__).parent


def call(path, params, method="POST"):
    params = {**params, "access_token": os.environ["IG_TOKEN"]}
    data = urllib.parse.urlencode(params)
    url = API + path + ("?" + data if method == "GET" else "")
    req = urllib.request.Request(url, data=None if method == "GET" else data.encode(), method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Erreur API {path}: {e.read().decode()}")


def wait_ready(cid):
    for _ in range(30):
        s = call(f"/{cid}", {"fields": "status_code"}, "GET").get("status_code")
        if s == "FINISHED":
            return
        if s in ("ERROR", "EXPIRED"):
            raise SystemExit(f"Conteneur {cid} : {s}")
        time.sleep(4)
    raise SystemExit(f"Conteneur {cid} : délai dépassé")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    now = datetime.now(ZoneInfo("Europe/Paris"))
    if "--force" not in sys.argv and now.hour != 18:
        print(f"Il est {now:%H:%M} à Paris, publication seulement à 18 h."); return
    day = args[0] if args else now.strftime("%Y-%m-%d")
    todo = [p for p in sorted(ROOT.glob(f"posts/{day}-*.json"))
            if json.loads(p.read_text()).get("status") not in ("published", "blocked")]
    if not todo:
        print(f"Aucun post à publier pour {day}."); return
    post_path = todo[0]
    post = json.loads(post_path.read_text())
    imgs = sorted((ROOT / "out" / post_path.stem).glob("slide-*.jpg"), key=lambda p: int(p.stem.split("-")[1]))
    if not 2 <= len(imgs) <= 20:
        raise SystemExit(f"{len(imgs)} images trouvées, il en faut 2 à 20.")
    base = f"https://raw.githubusercontent.com/{os.environ['GITHUB_REPOSITORY']}/{os.environ['COMMIT_SHA']}"
    children = []
    for p in imgs:
        url = f"{base}/{p.relative_to(ROOT).as_posix()}"
        children.append(call(f"/{IG_USER_ID}/media", {"image_url": url, "is_carousel_item": "true"})["id"])
    for c in children:
        wait_ready(c)
    caption = post["caption"] + "\n\n" + " ".join(post["hashtags"])
    car = call(f"/{IG_USER_ID}/media", {"media_type": "CAROUSEL", "children": ",".join(children), "caption": caption})["id"]
    wait_ready(car)
    pub = call(f"/{IG_USER_ID}/media_publish", {"creation_id": car})
    post.update(status="published", media_id=pub["id"], published_at=now.isoformat())
    post_path.write_text(json.dumps(post, ensure_ascii=False, indent=2))
    print(f"Publié sur @legaragemalin : media {pub['id']}")


if __name__ == "__main__":
    main()
