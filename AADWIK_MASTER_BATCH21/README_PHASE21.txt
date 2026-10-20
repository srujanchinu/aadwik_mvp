AADWIK MASTER BATCH 21
Production Integration & Safe Backend Wiring

Purpose:
Provide a safe integration bridge between the master production pipeline and an
existing movie-generation backend. This batch does not overwrite backend files
and does not invoke external providers. It defines adapters, feature gating,
job mapping, and integration validation so the real backend can be wired in a
controlled later step.

Safety:
- additive and self-contained
- no modification of backend/app
- no provider API keys
- no real rendering
- explicit feature flag required
