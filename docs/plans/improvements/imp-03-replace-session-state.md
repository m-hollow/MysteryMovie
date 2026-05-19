# IMP-03: Replace Session-Based State Passing with Database Transactions

## Current State
Round conclusion stores intermediate results in `request.session`:
- `request.session['point_queue']` — points to be committed
- `request.session['ranked_results']` — ranking data

This is fragile: session expiry, browser close, or server restart loses uncommitted data.

## Proposed Design
Option A: **Atomic database transaction**
- Wrap the entire conclude→commit flow in a single database transaction
- Use a "draft" status on UserRoundDetail that becomes "finalized" on commit

Option B: **Staging table**
- Create `ScoringDraft` model to store intermediate results
- Admin reviews drafts, then commits them to permanent tables
- Drafts auto-expire after 24 hours

## Recommended: Option A
Simpler, uses existing Django infrastructure, no new models needed.

## Steps
1. Add `status` field to UserRoundDetail: `draft` / `finalized`
2. ConcludeRoundView creates/updates UserRoundDetail records with `status='draft'`
3. CommitUserRoundView reviews and confirms individual records
4. CommitGameRoundView sets all to `status='finalized'` in a transaction
5. Remove session-based state passing

## Effort: Medium-High (1-2 days)
