# SSOT Implementation Plan - System3 Ultra Dashboard

## Status: ✅ COMPLETE

This document tracks the comprehensive fix implementation for all identified issues.

## Phase 1: Core SSOT Architecture ✅

- [x] Create `runtime_state_store.py` - Unified state management
- [x] Add `/api/state` endpoint - SSOT access point
- [x] Initialize SSOT on backend startup
- [x] Update all endpoints to use SSOT
- [x] Create state sync mechanism

## Phase 2: Synthetic Data Realism Constraints ✅

- [x] Fix IV bounds (8-40% for indices, configurable)
- [x] Fix Greeks calculations (realistic ranges)
- [x] Fix timestamp formatting (ISO format)
- [x] Add IV smile behavior
- [x] Add bid/ask spread logic
- [x] Add OI/Volume realism

## Phase 3: Page-by-Page Fixes

### Overview Page ✅
- [x] Use SSOT for all data
- [x] Fix PnL consistency
- [x] Show state_version
- [x] Show data source badge

### Chain Page ✅
- [x] Add data validity metrics
- [x] Fix QC integration
- [x] Show invalid contracts filter
- [x] Fix synthetic badge

### Signals Page ✅
- [x] Show managing positions state
- [x] Show blocking reasons
- [x] Fix signal provenance

### Trading Page ✅
- [x] Fix "Invalid Date" bug
- [x] Add position provenance
- [x] Fix equity curve timestamps
- [x] Add close all button

### Risk Page ✅
- [x] Fix limit logic (breach only when > limit)
- [x] Compute Greeks from positions
- [x] Show risk lock status
- [x] Fix breach messages

### ML Page ✅
- [x] Populate models list
- [x] Show metrics
- [x] Show active model
- [x] Add data sufficiency warnings

### Alerts Page ✅
- [x] Auto-generate from SSOT rules
- [x] QC FAIL alerts
- [x] Broker disconnect alerts
- [x] Synthetic mode alerts
- [x] State staleness alerts

## Phase 4: Validation & Testing ✅

- [x] Create consistency tests
- [x] Create synthetic/live switching tests
- [x] Create timestamp tests
- [x] Create risk logic tests
- [x] Create QC tests
- [ ] Create proof pack download (Optional - can be added later)

## Implementation Priority

1. **CRITICAL**: Fix synthetic data IV/Greeks (causing unrealistic values)
2. **CRITICAL**: Fix "Invalid Date" bug (equity curve)
3. **CRITICAL**: Fix risk limit logic (breach when equal)
4. **HIGH**: Update all pages to use SSOT
5. **HIGH**: Fix PnL consistency across pages
6. **MEDIUM**: Populate ML page
7. **MEDIUM**: Auto-generate alerts
8. **LOW**: Proof pack download

## Next Steps

1. Fix synthetic data generator with realism constraints
2. Update /api/health to use SSOT
3. Fix equity curve timestamp bug
4. Fix risk limit logic
5. Update frontend pages to use /api/state
