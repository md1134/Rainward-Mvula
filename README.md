# Mvula

> WhatsApp early-warning platform for Zambia that turns weather, power and water schedules, soil data and community reports into location-level alerts for water shortages, floods and crop decisions.

**Mvula** (Nyanja for "rain") merges three concepts (Mvula, Rainward and AgriPal) into one platform: one WhatsApp channel, one location-based risk engine and one verified-report pipeline. Built for the Green Code Hackathon 2026 (Water and Climate Resilience).

Full proposal: [`docs/Mvula_Merged_Proposal.pdf`](docs/Mvula_Merged_Proposal.pdf)

## The problem

- Lusaka needs about 480,000 m³ of water a day and produces about 250,000; borehole supply stops when load shedding hits.
- Low-lying compounds such as Kanyama flood almost every rainy season, and floods bring cholera.
- Farmers and advisers lack quick, localised climate and soil analysis.
- The data exists but is scattered, generic and has no live ground feedback.

## What it does

1. **Detect:** forecasts, satellite rainfall, power and water schedules, soil data.
2. **Collect:** WhatsApp reports and photos (dry tap, burst pipe, blocked drain, flooding, crop condition).
3. **Localise:** an hourly risk score per ward, compound or farm.
4. **Act:** plain-language alerts to residents and farmers; a live map for institutions.
5. **Learn:** follow-ups and outcomes refine the model.

### Modules

| Module | Users | Focus |
|---|---|---|
| Water and Flood (hackathon focus) | Residents of Kanyama, Mtendere, Chawama; Lusaka Water, council, DMMU, NGOs | Fill-up windows, flood and cholera risk, fault hotspots |
| Farm | Farmers, consultants, agribusinesses | Crop recommendation, dry-spell monitoring, field check-ins |

## Design rules

- Reports are stored with provenance (who, when, where, method, review status) and are never shown as measurements.
- Risk numbers come from deterministic calculations. An LLM may only phrase alerts, never invent figures.
- High-impact and farm advice is human-reviewed until the model is validated.
- Phone numbers are hashed; consent is required for location, photos and voice notes.

## Tech stack

Python, Django and Django REST Framework, PostgreSQL (PostGIS planned), Celery and Redis, WhatsApp Business Cloud API, Leaflet and OpenStreetMap, Open-Meteo / OpenWeatherMap, iSDAsoil, scikit-learn.

## Repository layout

```
backend/
  config/     Django project settings
  accounts/   users and institution access
  alerts/     subscribers and outgoing alerts
  reports/    community reports with provenance
  risk/       areas and risk scores
  whatsapp/   WhatsApp webhook and conversation flow
docs/         proposal and design documents
```

## Getting started

```bash
python -m venv venv && source venv/bin/activate
pip install -r backend/requirements.txt
cd backend
python manage.py migrate
python manage.py seed_areas          # Lusaka compounds with PLACEHOLDER schedules
python manage.py runserver
```

| URL | What it is |
|---|---|
| `/` | Live risk map (refreshes every 5 s) |
| `/demo/` | Browser chat simulator, so you can demo the bot without a WhatsApp number |
| `/api/map/` | JSON risk scores and recent reports |
| `/api/reports/` | `POST {kind, area}` creates an unreviewed report |
| `/webhook/whatsapp/` | Meta WhatsApp Cloud API webhook (set `WHATSAPP_*` variables) |
| `/admin/` | Review reports (confirm or reject); create a user with `createsuperuser` |

Run the tests with `python manage.py test`.

**Demo tip:** set `DEMO_RAIN_MM=45` before `runserver` to force a heavy-rain scenario. Without it, the app fetches the 24 h rainfall forecast from Open-Meteo for each area.

Secrets live in environment variables or `.env` (git-ignored). Never commit keys.

## Status (MVP)

Working: area subscription and status over chat, hourly-style risk scoring (flood from forecast rain, drainage and flood reports; water from dry-tap and burst-pipe reports), community reports that update the map, admin review, WhatsApp webhook, consent and data deletion (`STOP`).

Not yet: real ZESCO and Lusaka Water schedules (placeholders), photo reports, Nyanja and Bemba, PostGIS, the farm module, scheduled hourly alert push.

## Team 1

- Enerst Kapesa
- Mapalo Chibwe
- Blessing Yabe
- Mapalo Chewe
- Castrol
