# ☁️ GOOGLE CLOUD ACCESS DOCUMENTATION

## Cloud Run Application
- URL: https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/
- Service: genesis-system3-web
- Project: system3-openalgo-safe
- Region: asia-south1
- Automation SA: genesis-system3-automation@system3-openalgo-safe.iam.gserviceaccount.com
- Token rotate job: genesis-system3-dhan-token-rotate

## Cloud Console Access
- Main: https://console.cloud.google.com/
- Cloud Run: https://console.cloud.google.com/run/
- Cloud Storage: https://console.cloud.google.com/storage/
- Monitoring: https://console.cloud.google.com/monitoring/
- Logs: https://console.cloud.google.com/logs/

## Full Investigation Access

### View Deployments
```bash
gcloud run services describe genesis-system3-web
gcloud run revisions list --service genesis-system3-web
```

### View Logs
```bash
gcloud run logs read --limit 50
gcloud run logs read --service genesis-system3-web --limit 100
```

### View Metrics
```bash
gcloud monitoring dashboards list
gcloud monitoring metrics-descriptors list
```

### Edit Configuration
```bash
gcloud run services update genesis-system3-web --set-env-vars KEY=VALUE
```

### Deploy Updates
```bash
# From repo
gcloud run deploy genesis-system3-web --source . --region asia-south1
```

## Proof Sources

- Deployment History: https://console.cloud.google.com/run/detail/...
- Logs View: https://console.cloud.google.com/logs/...
- Monitoring: https://console.cloud.google.com/monitoring/...

## Investigation Capabilities

✅ Full access to:
- Deployment history
- All logs
- Monitoring metrics
- Configuration management
- Version control
- Performance metrics
- Error tracking

✅ Edit access to:
- Environment variables
- Configuration files
- Deployment settings
- Scaling parameters

---
All commands require gcloud CLI authentication.
Future Claude will have access to all of these automatically.
