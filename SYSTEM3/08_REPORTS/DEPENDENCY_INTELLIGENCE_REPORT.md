# Phase 4 dependency intelligence
Upstream: owner bounded authority -> exact merged SHA -> CI -> approved build -> immutable digest -> Cloud Run & job/scheduler -> Dhan session and exchange data. Downstream: worker -> Firestore artifacts/lease -> read-only API -> 22-tab UI -> independent evidence.
Failure cascade: missing verifier -> main workflow exits 2 before HTTP; missing approval -> no candidate build; absent worker -> stale/absent broker & paper records; mismatched SHA -> no production proof; stale lease/duplicate owner -> quarantine.
Blast radius: CI-only negative tests cannot mutate cloud. LIVE/order route remains separately denied; no broker-side zero-order evidence.
