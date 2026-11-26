"""Vérifie le jeton sans rien publier : lecture Instagram + test d'écriture invisible sur la page Facebook."""
import os, json
from publish import call, IG_USER_ID, FB_PAGE_ID
print("Instagram :", call(f"/{IG_USER_ID}", {"fields": "username,media_count"}, "GET"))
print("Page :", call(f"/{FB_PAGE_ID}", {"fields": "name"}, "GET"))
url = f"https://raw.githubusercontent.com/{os.environ['GITHUB_REPOSITORY']}/main/out/2026-11-26-clio-4/slide-1.jpg"
pid = call(f"/{FB_PAGE_ID}/photos", {"url": url, "published": "false"})["id"]
print("Écriture page OK (photo non publiée)", pid)
call(f"/{pid}", {}, "DELETE")
print("Photo de test supprimée")
