# Gmail OAuth Connector

## Status

Planned. This document is the implementation contract for `feature/gmail-oauth-connector`.

## Goal

Allow an authorized WorkTwin organization administrator to connect a Gmail or Google Workspace mailbox, ingest permitted email as provenance-preserving organizational artifacts, and safely make eligible evidence available to existing Twin retrieval.

## Scope

- Google OAuth 2.0 web-server flow for Gmail and Google Workspace.
- The least-privileged Gmail scope required for the first release: `https://www.googleapis.com/auth/gmail.readonly`.
- Secure authorization initiation, callback handling, one-time `state` validation, token refresh, connection status, manual synchronization, and disconnect.
- Selection of one existing Gmail label as the mailbox subset to synchronize for a connection.
- Normalization of Gmail messages and threads into the existing `work_artifacts` ingestion contract.
- Initial and incremental synchronization, checkpointing, deduplication, retry-safe writes, and audit events.
- A frontend connection view for Connect Gmail, connection status, last synchronization, error state, manual sync, and Disconnect.
- Unit, integration, and end-to-end coverage for the acceptance criteria below.

## Non-goals

- Sending, modifying, deleting, labeling, or archiving Gmail messages.
- Gmail push notifications, webhooks, or background scheduling.
- Multiple-label, arbitrary-query, and folder-selection synchronization rules.
- Microsoft 365 / Outlook support.
- Changes to the existing embedding, memory-chunk, derived-profile, or Twin retrieval contracts beyond supplying normalized email artifacts.

## Preconditions and Security Decisions

- A connection must be associated with an authenticated, authorized organization actor. The current application must establish this authorization context before a live connector is enabled.
- OAuth client ID, client secret, redirect URI, and token-encryption material are environment secrets. They must not use `VITE_*` variables, enter source control, API responses, client state, or logs.
- Store access and refresh tokens encrypted at rest; decrypt only in the server-side connector worker. Persist the minimum metadata necessary to refresh and revoke a connection.
- Generate a cryptographically secure OAuth `state`; bind it to the initiating organization and actor; store only a verifiable form; make it one-time-use and short-lived.
- Treat imported Gmail content as `restricted` by default. Promotion to `company_shared` requires a documented, explicit organization policy; Gmail metadata alone is not sufficient to infer that a message is safe to share.
- A v1 connection synchronizes only messages bearing one administrator-selected existing Gmail label. It must never enumerate and persist the rest of the readable mailbox merely because the OAuth scope permits access.
- Disconnecting revokes the Google token where possible, disables future sync, and makes stored connector credentials unusable. Artifact retention follows the organization retention policy and is not silently deleted.

## User Flow

1. An authorized organization administrator selects **Connect Gmail**.
2. WorkTwin creates an expiring OAuth state and redirects to Google's consent screen.
3. Google redirects to WorkTwin's callback. WorkTwin validates state before exchanging the authorization code server-side.
4. WorkTwin records the encrypted credentials and connection metadata, then displays a connected state without exposing credentials.
5. The administrator selects one existing Gmail label to define the synchronized subset.
6. The administrator starts a manual sync. WorkTwin fetches only messages bearing that label, normalizes them, and upserts artifacts idempotently.
7. The administrator can inspect connection and sync status or disconnect the mailbox.

## API Contract

All routes require the authenticated organization context described above. Exact authorization middleware is a prerequisite implementation decision.

| Endpoint | Behavior |
| --- | --- |
| `POST /api/connections/gmail/authorize` | Creates OAuth state and returns the Google authorization URL. |
| `GET /api/connections/gmail/callback` | Validates state, exchanges the code, stores the connection, then redirects to the connection UI with a non-sensitive result. |
| `GET /api/connections/gmail` | Returns sanitized connection and last-sync status; never returns tokens. |
| `PUT /api/connections/gmail/selection` | Validates and records the single Gmail label that defines the synchronized subset. |
| `POST /api/connections/gmail/sync` | Starts one manual, idempotent sync for the current organization connection. |
| `DELETE /api/connections/gmail` | Disconnects the connection and prevents future credential use. |

## Persistence Contract

Add migrations and repository adapters for:

- `oauth_connections`: organization ID, provider (`google_gmail`), provider account ID, encrypted token fields, granted scopes, token expiry, selected Gmail label ID/name, status, timestamps, and sanitized failure metadata.
- `oauth_authorization_states`: organization/actor binding, hashed state, expiry, consumed timestamp, and redirect context.
- `connector_sync_checkpoints`: connection ID, provider cursor/history ID, last completed sync, status, counters, and sanitized failure metadata.
- `connector_audit_events`: actor, organization, connection, event type, timestamp, and non-sensitive context.

Use Gmail message ID as the stable external identity and thread ID as thread provenance. Each normalized artifact must retain source type, author/source identity, timestamp, subject/title, canonical Gmail URI where available, provider IDs, access scope, and original content needed by the existing ingestion contract. Upserts must use a unique provider-message identity so retries cannot create duplicates.

## Synchronization Rules

- The first release is manually triggered; no polling or push notifications run automatically.
- A sync requires a configured selected label and requests only messages with that label ID.
- A sync refreshes an expired access token server-side before making Gmail API calls.
- A completed run advances its checkpoint only after all corresponding artifact writes succeed.
- Repeated delivery of the same Gmail message updates the existing artifact rather than creating another one.
- Failed requests use bounded retry/backoff where safe; user-facing errors are actionable but do not reveal provider credentials or raw provider payloads.
- Imported artifacts continue through the existing embedding and derived-profile refresh workflow only when their access scope permits it.

## Approved Mailbox-selection Policy

The first release imports an explicitly selected subset, not all readable Gmail. Each connection uses one existing Gmail label selected by the authorized administrator; only messages with that label are eligible for synchronization. The Gmail OAuth scope remains `gmail.readonly`, so this product-side filter is mandatory and must be enforced on every initial and incremental sync. All imported content remains `restricted` unless an explicit organization policy promotes it.

## Acceptance Criteria

- Given an authorized organization administrator, when they start Gmail connection, then WorkTwin returns a Google authorization URL with the configured redirect URI, Gmail readonly scope, and a new expiring state.
- Given a valid, unused callback state, when Google returns an authorization code, then WorkTwin stores a sanitized connected state and never exposes an OAuth credential to the browser.
- Given an invalid, expired, cross-organization, or reused state, when the callback runs, then WorkTwin rejects it without exchanging the authorization code.
- Given an expired access token and valid refresh token, when a sync begins, then WorkTwin refreshes credentials server-side and continues safely.
- Given a successful sync, when the same Gmail message is received again, then exactly one corresponding artifact exists with preserved message/thread provenance.
- Given a connected mailbox with a selected label, when a sync runs, then WorkTwin imports only messages bearing that label and does not persist other readable mailbox messages.
- Given imported Gmail evidence, when it has not been explicitly promoted by organization policy, then it is marked `restricted` and excluded from unauthorized Twin retrieval.
- Given a disconnected mailbox, when a subsequent sync is requested, then WorkTwin does not call Gmail or use its stored credentials.
- Given a connection or sync failure, when the user checks status, then they receive a safe actionable error without token values, authorization codes, or raw Gmail content.
