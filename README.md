# AstroStream 🤖

Prototype de télé-opération robotique assistée en temps réel.

Un robot physique est remplacé par une simulation **Pygame** (côté edge) dont le flux vidéo est transmis à un **dashboard web via WebRTC**. L'opérateur pilote le robot à distance, pendant qu'une IA embarquée analyse les obstacles et calcule le risque de collision.

---

## Structure:
AstroStream/
├── dashboard/          # Interface web (HTML, JS, CSS)
├── edge/
│   ├── ai/             # Détection obstacles + calcul TTC
│   ├── rtc/            # WebRTC, DataChannel, signaling
│   └── simulation/     # Moteur Pygame, robot, environnement
└── requirements.txt
---

## Installation

```bash
pip install -r edge/requirements.txt
```

---

## Lancement

```bash
# 1. Serveur de signalisation
python -m edge.rtc.signaling_server

# 2. Simulation edge
python -m edge.rtc.edge_main

# 3. Dashboard
python -m http.server 8080 --directory dashboard
# → ouvrir http://localhost:8080
```

---

## Contrôles

| Touche | Action |
|---|---|
| `↑ ↓ ← →` | Piloter le robot |
| `Espace` | Frein |
| `S` (Pygame) | Safe Mode — arrêt d'urgence |
| `R` (Pygame) | Reprendre la téléopération |

---

## Fonctionnement

- **Vidéo** : la scène Pygame est streamée en temps réel via WebRTC (~30 fps)
- **Commandes** : envoyées depuis le dashboard vers le robot via DataChannel
- **IA / TTC** : obstacles détectés côté edge, Time-To-Collision affiché en overlay (cadres rouges)
- **Sécurité** : arrêt automatique en cas de perte de connexion ou Safe Mode activé
