# Audit Logging

The app uses an append-only educational audit log backed by local SQLite.

Events capture:

- timestamp;
- user role;
- module;
- object type;
- object ID;
- action;
- previous value;
- new value;
- reason;
- approval status.

Typical events include control execution, issue creation, owner changes, status changes, evidence submission, 2LOD challenge, closure acceptance, closure rejection and audit observations.

This is a learning implementation. It is not an enterprise audit-management system.
