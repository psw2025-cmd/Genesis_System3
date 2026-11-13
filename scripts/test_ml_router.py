import sys
sys.path.insert(0, r"c:\Genesis_System3_clean")
import dashboard.backend.routers.ml as ml

metrics = ml._validation_metrics()
print("ML validation metrics:")
print("  validation_days:", metrics.get("validation_days"))
print("  avg_rho:", metrics.get("avg_rho"))
print("  avg_hit_rate:", metrics.get("avg_hit_rate"))
print("  model_proof_ready:", metrics.get("model_proof_ready"))
print("  status:", metrics.get("status"))

truth = ml._validation_truth_payload()
print("\nValidation truth payload:")
print("  rho:", truth.get("rho"))
print("  hit_rate:", truth.get("hit_rate"))
print("  source_file:", truth.get("source_file"))

records = ml._model_performance_records()
print("\nModel performance records:")
for r in records:
    print(" ", r)

print("\nALL ML ROUTER CHECKS COMPLETED!")
sys.exit(0)
