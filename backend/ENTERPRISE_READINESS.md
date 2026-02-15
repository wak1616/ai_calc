# Backend Enterprise / Licensing Readiness Checklist

This checklist is intended to help prepare the backend service for larger-company due diligence.

## 1) Security configuration (must-have)
- Set strict `ALLOWED_ORIGINS` to only approved frontend domains.
- Keep `ALLOW_ORIGIN_REGEX` narrow, or disable broad preview-domain regex in production.
- Keep `MAX_REQUEST_SIZE_BYTES` small (default 8 KB is appropriate for this API payload).
- Keep HTTPS termination enabled at the edge/reverse proxy.
- Keep `SET_HSTS_HEADER=true` when serving over HTTPS.

## 2) Runtime and infrastructure controls
- Run API behind a managed TLS edge (Render or reverse proxy).
- Restrict inbound traffic at firewall/security-group level.
- Use least-privilege service accounts and scoped secrets.
- Rotate all secrets and tokens on a documented schedule.
- Enable vulnerability scanning and patch cadence for dependencies/base images.

## 3) Data handling expectations
- API is designed to accept only de-identified clinical inputs for inference.
- Do not log request bodies.
- Configure retention limits for application logs and monitoring traces.
- Document data flow and retention in a customer-facing security appendix.

## 4) Healthcare / HIPAA program items (organizational)
- Confirm legal applicability with counsel/compliance.
- Execute required BAAs/DPAs with vendors if applicable.
- Maintain written policies: access control, incident response, breach notification, and retention/deletion.
- Maintain auditable access logs and periodic access reviews.

## 5) Recommended evidence package for enterprise licensing
- Architecture/data-flow diagram.
- API schema and payload examples.
- Security control matrix (technical + organizational controls).
- Pen-test or security assessment summary.
- Change management and release process summary.

## 6) Environment variables used by backend
- `ALLOWED_ORIGINS`
- `ALLOW_ORIGIN_REGEX`
- `MAX_REQUEST_SIZE_BYTES`
- `SET_HSTS_HEADER`
- `ENABLE_API_DOCS`
