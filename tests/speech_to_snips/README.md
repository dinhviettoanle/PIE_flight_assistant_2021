# Test SpeechRecogntion to Snips-NLU

## Lancement
1. (Si besoin) Être dans le bon environnement conda / venv
2. Lancer dans un terminal `python3 app.py`
3. Sur un navigateur, aller sur [http://localhost:5000/](http://localhost:5000/)
4. Cliquer sur le bouton et parler. Le texte devrait théoriquement s'afficher en direct sur le canvas
5. Re-cliquer sur le bouton. Normalement, le terminal devrait afficher le texte reconnu

## Snips-NLU
Il reste juste à coder la fonction `process_transcript()` (ligne 21 du .py).

À partir d'une phrase brute (par exemple `what is the nearest airport`, modulo toutes les variantes `what's the nearest airport`, `which airport is the nearest`, `what is the closest airport`...), il faut qu'elle renvoie une forme "normalisée" de la requête (par exemple `NearestAirport`), en considérant toutes les requêtes qu'on voudra prendre en compte.

Ça permettra de rejoindre le `handle_query()` dans `src/web_app/views.py`.

## Fonctionnement en gros
- En lançant `python3 app.py`, on lance un serveur Python. Il attend qu'un client se connecte.
- En ouvrant localhost sur un navigateur, on vient de créer un client. Le serveur voit donc qu'un client se connecte et renvoie une page html à ce client (fonction `index`, ligne 46 du `app.py`).
- Tout ce qui est SpeechRecognition se passe au niveau client (en gros, Python ne sait pas ce qu'il se passe sur le navigateur). Tout ce qui s'y passe est dans `static/speech_recognition.js`:
  - Dès que la page s'ouvre, on exécute `init_speech_recognizer()`
  - Quand on appuie sur le bouton, on exécute la fonction `trigger_button()` (ligne 34 du .html qui renvoie à la ligne 71 du .js)
  - Cette fonction lance donc `recognition.start();` (ligne 80 du .js) qui lance la reconnaissance vocale
  - Quand on ré-appuie sur la bouton, on ré-exécute `trigger_button()` mais ça lance cette fois `recognition.stop();` (ligne 75 du .js)
  - Ce `.stop()` indique au recognizer de s'arrêter, ce qui exécute alors le `recognition.onend` (ligne 33 du .js)
  - Dedans, il y a, en particulier `send_transcript()` qui envoie au serveur le transcript final sur l'adresse `/_transcript` (ligne 102 du .js)
- On repasse sur le code python (côté serveur) : le serveur regarde constamment l'adresse `/_transcript` (ligne 53 du .py). Quand il voit que quelque chose arrive dessus, il exécute `get_speech_transcript()` (ligne 54 du .py) et renvoie au client qu'il a bien reçu son message (ligne 59 du .py).


En gros pour résumer :

1. [ Serveur ] &#8594; `index.html` &#8594; [ Client ]
2. [ Client ] fait son truc avec le SpeechRecognition
3. [ Client ] &#8594; `{transcript: "what's the nearest airport"}` &#8594; [ Serveur ]
4. [ Serveur ] fait du NLP avec ce transcript
5. [ Serveur ] &#8594; `{success: True}` [ Client ]
