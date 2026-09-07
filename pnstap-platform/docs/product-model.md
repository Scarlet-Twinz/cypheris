# Cypheris Product Model

## Product

Cypheris is the security platform. PNSTAP is the technical security engine underneath it, while Cypheris Sentinel is the command-center experience and LYROMI is the intelligence layer.

The product is organization-first: a company creates one workspace, becomes the owner of its security environment, and can invite people and connect infrastructure into that workspace.

## Company onboarding

1. A company creates an account.
2. Signup creates the company workspace and the first user as **Company Admin**.
3. The workspace immediately starts a **7-day full-access trial**.
4. The company can connect environments, enroll sensors, review telemetry, use security surfaces, and evaluate the platform during the trial.
5. When the trial ends, continued platform access requires an active paid subscription.

## Subscription model

| Plan | Annual price | Included users | Retention | AI tier | Branding |
| --- | ---: | ---: | ---: | --- | --- |
| Free | $0 | 1 | 7 days | Core | Cypheris standard |
| Pro | $1,000/year | 5 | 30 days | Basic | Cypheris standard |
| Business | $5,000/year | 50 | 90 days | Advanced | Logo + colors |
| Enterprise | $15,000+/year | Unlimited | 1 year | Custom | Full white-label |

Users above the plan allowance are billed at **$10/user/month**.

Paid subscriptions are yearly in the current product model. Stripe and PayPal are the planned payment rails; Enterprise also supports bank transfer. Payment credentials, webhook secrets, and provider identifiers belong in deployment secrets, never in source control.

The repository currently contains the subscription/trial data model and plan API. Real payment activation requires provider credentials and webhook verification in the deployment environment.

## Company identity

The workspace can carry organization-level identity. The data model supports a company logo URL plus primary and secondary brand colors. Business is the planned entry point for logo/color customization; Enterprise extends this to full white-label behavior.

The UI should keep Cypheris's security structure while allowing the organization's identity to appear inside its workspace.

## Access model

The first account is Company Admin. The platform is organization-scoped: authenticated requests derive `company_id` from the access token instead of trusting a company ID supplied by the browser.

The intended access model is:

- Company Admin — organization, billing, branding, team and security administration.
- Security/Analyst roles — security operations and investigation surfaces.
- Member roles — controlled workspace visibility based on assigned permissions.
- Sensor/agent credentials — device-level enrollment credentials, separate from human user authentication.

## Workspace surfaces

The application is intentionally larger than a single dashboard. The current navigation foundation contains:

1. Overview — command-center posture and live metrics.
2. Security — posture and security controls.
3. Alerts — detections and investigation queue.
4. Network — traffic and communication intelligence.
5. Assets — organization infrastructure inventory.
6. Sensors — sensor enrollment and fleet health.
7. Intelligence — threat intelligence and contextual findings.
8. LYROMI — AI security analysis.
9. Incidents — investigation and response workspace.
10. Reports — executive and operational reporting.
11. Integrations — cloud, SIEM, EDR and custom security sources.
12. Notifications — organization and security notifications.
13. Team — members and access management.
14. Billing — trial, plans and subscription state.
15. Settings — organization identity and workspace configuration.
16. Audit — security-sensitive organization activity.
17. API — controlled developer/integration surface.

Public product pages, authentication, onboarding, sensor setup and the existing dashboard remain separate entry points.

## Security architecture direction

- PostgreSQL is the system of record.
- FastAPI provides authenticated API surfaces.
- JWT claims identify the authenticated user, company and role.
- Passwords are stored as bcrypt hashes.
- Security integrations and sensors use separate enrollment credentials.
- Company-scoped queries prevent cross-tenant access through caller-supplied company IDs.
- Audit logging is part of the data model.
- Production deployment should use versioned migrations rather than reset-oriented initialization SQL.
- Production authentication should consider secure HttpOnly cookie sessions/refresh-token rotation, rate limiting, secret management, monitoring and verified payment webhooks.

## Product direction

The long-term Cypheris experience is a security command center rather than a collection of disconnected screens. The main flow is:

**Connect → Observe → Understand → Investigate → Respond → Report → Improve**

The platform should continue to grow around that loop while keeping the organization, subscription, security data, integrations and AI context connected through one consistent tenant model.
