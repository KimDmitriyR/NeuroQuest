# NeuroQuest

Образовательная квест платформа для детей 

## Stack

- React + TypeScript
- FastAPI
- PostgreSQL
- Docker

## Печатные материалы (QR-коды карточек и миссий)

```bash
cd backend
python -m scripts.generate_qr_codes [base_url]   # default: http://localhost:5173
```

Генерирует QR-коды и заготовки лицевой стороны карточек в
`backend/print_assets/{qr,cards}/` для всех карточек квеста и конвертов с
миссиями, читая актуальный контент прямо из БД. Для прода запусти с
реальным доменом фронтенда, например:
`python -m scripts.generate_qr_codes https://neuroquest.example.com`.