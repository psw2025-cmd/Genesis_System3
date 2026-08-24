/**
 * The positions/holdings batch is optimized aggregate state and may lag the
 * dedicated broker-status endpoint. A successful full response is therefore
 * authoritative for every overlapping field, not only token metadata.
 */
export function mergeAuthoritativeBrokerStatus(batchStatus: any, fullStatus: any) {
  const batch = batchStatus && typeof batchStatus === 'object' ? batchStatus : {}
  if (!fullStatus || typeof fullStatus !== 'object') return batchStatus
  return {
    ...batch,
    ...fullStatus,
    token_proof: fullStatus.token_proof ?? batch.token_proof,
    token_reload: fullStatus.token_reload ?? batch.token_reload,
    canonical_rotation: fullStatus.canonical_rotation ?? batch.canonical_rotation,
  }
}
