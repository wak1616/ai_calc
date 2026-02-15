# Security & HIPAA-Oriented Review (2026-02-15)

## Scope reviewed
- Frontend (Vue/Vuetify/Vite)
- Backend (FastAPI/XGBoost)
- Deployment config in repository (`vercel.json`, `vite.config.js`, docs)

## Key findings

### 1) Backend hosting on Hetzner VPS is technically feasible
- The backend is a standard FastAPI app and can run on any Linux host with Python dependencies and model file available.
- You should front it with a reverse proxy (Nginx/Caddy), TLS, process manager (systemd), and firewall controls.

### 2) HIPAA risk posture depends more on operations/contracts than framework
- Even though direct patient identifiers are not sent in `dataToSend`, clinical parameters are transmitted to the backend.
- If this system is used in a covered workflow, hosting provider BAAs, logging policy, access controls, encryption, and retention policy determine compliance risk.

### 3) Frontend disclosure mismatch
- UI text currently claims all entered data "is not stored or transmitted", but prediction inputs are transmitted to `/predict`.
- Name/ID/DOS are kept client-side in code, but age/eye/corneal_astigmatism/steep_axis/WTW/AL/LASIK are sent to backend.

## Practical recommendations
1. Update UI disclosure language to accurately state what is sent to backend.
2. If HIPAA context applies, ensure hosting providers with appropriate contractual coverage and documented safeguards.
3. Enforce strict server logging policy to avoid accidental capture of request bodies.
4. Add transport/network safeguards: HTTPS-only, WAF/rate limiting, restricted CORS origins.
5. Consider optional local-only inference mode if you want zero patient parameter transmission.

