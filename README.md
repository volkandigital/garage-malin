# Le Garage Malin

Carrousels Instagram de [@legaragemalin](https://www.instagram.com/legaragemalin/) : conseils auto & moto pour jeunes conducteurs.

- `posts/AAAA-MM-JJ-sujet.json` : contenu d'un post (écrit chaque jour par Claude)
- `render.py` : génère les slides 1080x1350 (`out/<post>/slide-N.jpg`)
- `publish.py` + `.github/workflows/publish.yml` : publication automatique à 18 h (heure de Paris) via l'API Instagram

Bloquer un post : mettre `"status": "blocked"` dans son JSON.
Secret requis : `IG_TOKEN` (jeton de la page Facebook « Le Garage », sans expiration).
