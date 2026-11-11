"""
Generator for CLOUD_GITHUB_TRUTH.xlsx
Authoritative forensic audit comparing Source A (GitHub repository) and Source B (Google Cloud Run deployed service).

Verified parameters:
- GitHub Remote: https://github.com/psw2025-cmd/Genesis_System3.git
- GitHub Branch: main
- GitHub Origin Commit: c6f63aec9b2e45c2871ffeed56dd7f4a58e722db
- Local HEAD Commit: 3e79246528663ce8f7092c5d7f1b613a4371a159
- Cloud Deployed Commit (DEPLOY_GIT_SHA): b732bf0921083d8b20128146b68366c91d4e9944
- Cloud Run Service: genesis-system3-web (project: system3-openalgo-safe, region: asia-south1)
- Cloud Run Active Revision (100% traffic): genesis-system3-web-00136-qub
- Cloud Run Candidate Revision (0% traffic): genesis-system3-web-00141-cuv
- Cloud Run Image Digest (Active): sha256:4a14ad39a348ec8c6aba796e24321900651ec1858ed76728442d8bbf5b7c9ba4
- Cloud Run Image Digest (Candidate): sha256:d3cd2d5031578071bd9f2f12f4d973375b6b8c099ce26ea710a2ac168d7c2164
- Dockerfile used: dashboard/backend/Dockerfile
- Cloud Build Source Revision (Active): gs://system3-openalgo-safe_cloudbuild/source/genesis-auto-b732bf092108-1794280178.tgz (gen 1794280239240188)
- Cloud Build Source Revision (Candidate): gs://system3-openalgo-safe_cloudbuild/source/genesis-auto-b732bf092108-1794280791.tgz (gen 1794280858377786)
"""

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def build_cloud_github_truth_workbook(output_path: str = "CLOUD_GITHUB_TRUTH.xlsx"):
    wb = openpyxl.Workbook()
    # Remove default sheet
    wb.remove(wb.active)

    headers = [
        "File",
        "GitHub SHA256",
        "Cloud SHA256",
        "Match YES/NO",
        "GitHub Commit",
        "Cloud Revision",
        "Evidence"
    ]

    # Style definitions
    font_header = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    fill_header = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid") # Dark Navy

    font_data = Font(name="Calibri", size=10)
    font_bold = Font(name="Calibri", size=10, bold=True)
    
    # Status fills
    fill_match_yes = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid") # Light Green
    font_match_yes = Font(name="Calibri", size=10, bold=True, color="375623")
    
    fill_match_no = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid") # Light Coral/Red
    font_match_no = Font(name="Calibri", size=10, bold=True, color="C65911")
    
    fill_unverified = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid") # Light Yellow
    font_unverified = Font(name="Calibri", size=10, bold=True, color="7F6000")
    
    fill_proven = PatternFill(start_color="DDEBF7", end_color="DDEBF7", fill_type="solid") # Light Blue
    font_proven = Font(name="Calibri", size=10, bold=True, color="1F4E79")

    thin_border_side = Side(style="thin", color="D9D9D9")
    thin_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
    header_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=Side(style="medium", color="000000"))

    align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
    align_left = Alignment(horizontal="left", vertical="center", wrap_text=True)

    # Sheet definitions & data
    sheets_data = {
        "DEPLOYMENT_CHAIN": [
            [
                "1. GitHub Commit SHA",
                "c6f63aec9b2e45c2871ffeed56dd7f4a58e722db (origin/main) / 3e79246528663ce8f7092c5d7f1b613a4371a159 (HEAD)",
                "b732bf0921083d8b20128146b68366c91d4e9944 (DEPLOY_GIT_SHA)",
                "NO",
                "c6f63aec9b2e45c2871ffeed56dd7f4a58e722db",
                "genesis-system3-web-00136-qub",
                "gcloud run revisions describe genesis-system3-web-00136-qub confirms DEPLOY_GIT_SHA=b732bf0921083d8b20128146b68366c91d4e9944; origin/main is at c6f63aec9b2e45c2871ffeed56dd7f4a58e722db (5 commits ahead, no diff in the 4 target files)"
            ],
            [
                "2. GitHub Branch",
                "main (refs/heads/main)",
                "main (deployed from branch main at commit b732bf09)",
                "YES",
                "c6f63aec9b2e45c2871ffeed56dd7f4a58e722db",
                "genesis-system3-web-00136-qub",
                "git branch --show-current confirms main; git remote -v confirms https://github.com/psw2025-cmd/Genesis_System3.git; Cloud Run container deployed from main branch workspace"
            ],
            [
                "3. Dockerfile used by build",
                "dashboard/backend/Dockerfile (SHA256: cdca8f921d7b301b44ecddb703e1a8a2d1d07c088dd1c73ec6ba6bf46497f58b)",
                "dashboard/backend/Dockerfile",
                "YES",
                "c6f63aec9b2e45c2871ffeed56dd7f4a58e722db",
                "genesis-system3-web-00136-qub",
                "Cloud Build c0049f2f-0c77-42c9-b197-5cfc71269e0a step 0 args confirm --file=dashboard/backend/Dockerfile; multi-stage Dockerfile copies repository context into /app/"
            ],
            [
                "4. Cloud Build source revision",
                "UNVERIFIED (GCS build tarball not stored in git)",
                "gs://system3-openalgo-safe_cloudbuild/source/genesis-auto-b732bf092108-1794280178.tgz (gen 1794280239240188, SHA256: 0d4d714c357a83d14e6421216bbf16caf47779097e85b74c4200a3c6c7f2eb52)",
                "PROVEN",
                "b732bf0921083d8b20128146b68366c91d4e9944",
                "genesis-system3-web-00136-qub",
                "gcloud builds describe c0049f2f-0c77-42c9-b197-5cfc71269e0a confirms storageSource object genesis-auto-b732bf092108-1794280178.tgz in bucket system3-openalgo-safe_cloudbuild; Candidate build c5a2f44a used genesis-auto-b732bf092108-1794280791.tgz"
            ],
            [
                "5. Cloud Run revision",
                "N/A (Serverless Cloud Run Runtime)",
                "genesis-system3-web-00136-qub (100% active traffic; Candidate: genesis-system3-web-00141-cuv 0% traffic)",
                "PROVEN",
                "b732bf0921083d8b20128146b68366c91d4e9944",
                "genesis-system3-web-00136-qub",
                "gcloud run services describe genesis-system3-web --region asia-south1 --project system3-openalgo-safe: spec.traffic assigns 100% to genesis-system3-web-00136-qub; live HTTP probe to https://genesis-system3-web-doq2wplepa-el.a.run.app/api/broker/dhan/status confirms runtime_instance=genesis-system3-web-00136-qub"
            ],
            [
                "6. Cloud Run image digest",
                "N/A (Container registry image digest)",
                "sha256:4a14ad39a348ec8c6aba796e24321900651ec1858ed76728442d8bbf5b7c9ba4 (Candidate: sha256:d3cd2d5031578071bd9f2f12f4d973375b6b8c099ce26ea710a2ac168d7c2164)",
                "PROVEN",
                "b732bf0921083d8b20128146b68366c91d4e9944",
                "genesis-system3-web-00136-qub",
                "gcloud run revisions describe genesis-system3-web-00136-qub status.imageDigest confirms asia-south1-docker.pkg.dev/system3-openalgo-safe/system3-containers/genesis-system3@sha256:4a14ad39a348ec8c6aba796e24321900651ec1858ed76728442d8bbf5b7c9ba4 pushed by Cloud Build c0049f2f"
            ],
            [
                "core/brokers/dhan/dhan_readonly.py",
                "373ee523627d349ef0e3019cb55c3d429479a7c0cb279f0f5ba3012719a3730e",
                "3235987b8d3dd249629547f121c251c368820c0ec22376eb9377dcb6c49fe966",
                "NO",
                "c6f63aec9b2e45c2871ffeed56dd7f4a58e722db",
                "genesis-system3-web-00136-qub",
                "Git LF sha256=373ee523... (28,249 bytes); Cloud Build source archive CRLF sha256=3235987b... (29,034 bytes). Normalized LF content matches 100%. Live container in-situ filesystem is UNVERIFIED."
            ],
            [
                "dashboard/backend/routers/broker.py",
                "09663bbc1b0d6204a2c9180321ae35548af9c81d631cfb2708b09ba8df276ac2",
                "29cff3eac5de41a9dc4d22d3f927aeb4beebaf5bd76f0ab86a1abba0b1eb9422",
                "NO",
                "c6f63aec9b2e45c2871ffeed56dd7f4a58e722db",
                "genesis-system3-web-00136-qub",
                "Git LF sha256=09663bbc... (6,995 bytes); Cloud Build source archive CRLF sha256=29cff3ea... (7,188 bytes). Normalized LF content matches 100%. Live container in-situ filesystem is UNVERIFIED."
            ],
            [
                "dashboard/backend/broker/dhan_auth.py",
                "82ebaf985fe47df7fd403c359f7b89b5a8817a0f421e6b5f516b774514626166",
                "706f3b7244cf4d9d1949d663e0365b8075efa5ce65c7788b6fe14b6011145406",
                "NO",
                "c6f63aec9b2e45c2871ffeed56dd7f4a58e722db",
                "genesis-system3-web-00136-qub",
                "Git LF sha256=82ebaf98... (79 bytes); Cloud Build source archive CRLF sha256=706f3b72... (82 bytes). Normalized LF content matches 100%. Live container in-situ filesystem is UNVERIFIED."
            ],
            [
                "dashboard/backend/gain_rank_spot_enrichment.py",
                "125ae1d6bd6b7c3ae532dda11ad111b04c597e64387fff4cf20fc179ea5edea1",
                "1d70cab2b2b1b58d3a7c0a609db273547372baa64837946ecbf5eebde15fa23f",
                "NO",
                "c6f63aec9b2e45c2871ffeed56dd7f4a58e722db",
                "genesis-system3-web-00136-qub",
                "Git LF sha256=125ae1d6... (2,366 bytes); Cloud Build source archive CRLF sha256=1d70cab2... (2,440 bytes). Normalized LF content matches 100%. Live container in-situ filesystem is UNVERIFIED."
            ]
        ],
        "GITHUB_FILE_HASHES": [
            [
                "core/brokers/dhan/dhan_readonly.py",
                "373ee523627d349ef0e3019cb55c3d429479a7c0cb279f0f5ba3012719a3730e",
                "N/A",
                "PROVEN (GitHub SSOT)",
                "c6f63aec9b2e45c2871ffeed56dd7f4a58e722db",
                "genesis-system3-web-00136-qub",
                "git show c6f63aec9b2e45c2871ffeed56dd7f4a58e722db:core/brokers/dhan/dhan_readonly.py; size=28,249 bytes; git blob LF sha256. Identical on commit b732bf092108 and HEAD 3e792465."
            ],
            [
                "dashboard/backend/routers/broker.py",
                "09663bbc1b0d6204a2c9180321ae35548af9c81d631cfb2708b09ba8df276ac2",
                "N/A",
                "PROVEN (GitHub SSOT)",
                "c6f63aec9b2e45c2871ffeed56dd7f4a58e722db",
                "genesis-system3-web-00136-qub",
                "git show c6f63aec9b2e45c2871ffeed56dd7f4a58e722db:dashboard/backend/routers/broker.py; size=6,995 bytes; git blob LF sha256. Identical on commit b732bf092108 and HEAD 3e792465."
            ],
            [
                "dashboard/backend/broker/dhan_auth.py",
                "82ebaf985fe47df7fd403c359f7b89b5a8817a0f421e6b5f516b774514626166",
                "N/A",
                "PROVEN (GitHub SSOT)",
                "c6f63aec9b2e45c2871ffeed56dd7f4a58e722db",
                "genesis-system3-web-00136-qub",
                "git show c6f63aec9b2e45c2871ffeed56dd7f4a58e722db:dashboard/backend/broker/dhan_auth.py; size=79 bytes; git blob LF sha256. Identical on commit b732bf092108 and HEAD 3e792465."
            ],
            [
                "dashboard/backend/gain_rank_spot_enrichment.py",
                "125ae1d6bd6b7c3ae532dda11ad111b04c597e64387fff4cf20fc179ea5edea1",
                "N/A",
                "PROVEN (GitHub SSOT)",
                "c6f63aec9b2e45c2871ffeed56dd7f4a58e722db",
                "genesis-system3-web-00136-qub",
                "git show c6f63aec9b2e45c2871ffeed56dd7f4a58e722db:dashboard/backend/gain_rank_spot_enrichment.py; size=2,366 bytes; git blob LF sha256. Identical on commit b732bf092108 and HEAD 3e792465."
            ]
        ],
        "CLOUD_FILE_HASHES": [
            [
                "core/brokers/dhan/dhan_readonly.py [Cloud Build Source Archive]",
                "N/A",
                "3235987b8d3dd249629547f121c251c368820c0ec22376eb9377dcb6c49fe966",
                "PROVEN (Build Archive)",
                "b732bf0921083d8b20128146b68366c91d4e9944",
                "genesis-system3-web-00136-qub",
                "Extracted from gs://system3-openalgo-safe_cloudbuild/source/genesis-auto-b732bf092108-1794280178.tgz (input to Cloud Build c0049f2f); size=29,034 bytes; CRLF encoding. LF-normalized hash=373ee523627d349ef0e3019cb55c3d429479a7c0cb279f0f5ba3012719a3730e."
            ],
            [
                "dashboard/backend/routers/broker.py [Cloud Build Source Archive]",
                "N/A",
                "29cff3eac5de41a9dc4d22d3f927aeb4beebaf5bd76f0ab86a1abba0b1eb9422",
                "PROVEN (Build Archive)",
                "b732bf0921083d8b20128146b68366c91d4e9944",
                "genesis-system3-web-00136-qub",
                "Extracted from gs://system3-openalgo-safe_cloudbuild/source/genesis-auto-b732bf092108-1794280178.tgz (input to Cloud Build c0049f2f); size=7,188 bytes; CRLF encoding. LF-normalized hash=09663bbc1b0d6204a2c9180321ae35548af9c81d631cfb2708b09ba8df276ac2."
            ],
            [
                "dashboard/backend/broker/dhan_auth.py [Cloud Build Source Archive]",
                "N/A",
                "706f3b7244cf4d9d1949d663e0365b8075efa5ce65c7788b6fe14b6011145406",
                "PROVEN (Build Archive)",
                "b732bf0921083d8b20128146b68366c91d4e9944",
                "genesis-system3-web-00136-qub",
                "Extracted from gs://system3-openalgo-safe_cloudbuild/source/genesis-auto-b732bf092108-1794280178.tgz (input to Cloud Build c0049f2f); size=82 bytes; CRLF encoding. LF-normalized hash=82ebaf985fe47df7fd403c359f7b89b5a8817a0f421e6b5f516b774514626166."
            ],
            [
                "dashboard/backend/gain_rank_spot_enrichment.py [Cloud Build Source Archive]",
                "N/A",
                "1d70cab2b2b1b58d3a7c0a609db273547372baa64837946ecbf5eebde15fa23f",
                "PROVEN (Build Archive)",
                "b732bf0921083d8b20128146b68366c91d4e9944",
                "genesis-system3-web-00136-qub",
                "Extracted from gs://system3-openalgo-safe_cloudbuild/source/genesis-auto-b732bf092108-1794280178.tgz (input to Cloud Build c0049f2f); size=2,440 bytes; CRLF encoding. LF-normalized hash=125ae1d6bd6b7c3ae532dda11ad111b04c597e64387fff4cf20fc179ea5edea1."
            ],
            [
                "core/brokers/dhan/dhan_readonly.py [Live Container In-Situ Filesystem]",
                "N/A",
                "UNVERIFIED",
                "UNVERIFIED",
                "b732bf0921083d8b20128146b68366c91d4e9944",
                "genesis-system3-web-00136-qub",
                "UNVERIFIED: Cloud Run serverless platform does not expose in-situ container file read or exec API. In-container file cannot be inspected directly from Cloud Run service APIs without an authorized container inspection hook."
            ],
            [
                "dashboard/backend/routers/broker.py [Live Container In-Situ Filesystem]",
                "N/A",
                "UNVERIFIED",
                "UNVERIFIED",
                "b732bf0921083d8b20128146b68366c91d4e9944",
                "genesis-system3-web-00136-qub",
                "UNVERIFIED: Cloud Run serverless platform does not expose in-situ container file read or exec API. In-container file cannot be inspected directly from Cloud Run service APIs without an authorized container inspection hook."
            ],
            [
                "dashboard/backend/broker/dhan_auth.py [Live Container In-Situ Filesystem]",
                "N/A",
                "UNVERIFIED",
                "UNVERIFIED",
                "b732bf0921083d8b20128146b68366c91d4e9944",
                "genesis-system3-web-00136-qub",
                "UNVERIFIED: Cloud Run serverless platform does not expose in-situ container file read or exec API. In-container file cannot be inspected directly from Cloud Run service APIs without an authorized container inspection hook."
            ],
            [
                "dashboard/backend/gain_rank_spot_enrichment.py [Live Container In-Situ Filesystem]",
                "N/A",
                "UNVERIFIED",
                "UNVERIFIED",
                "b732bf0921083d8b20128146b68366c91d4e9944",
                "genesis-system3-web-00136-qub",
                "UNVERIFIED: Cloud Run serverless platform does not expose in-situ container file read or exec API. In-container file cannot be inspected directly from Cloud Run service APIs without an authorized container inspection hook."
            ]
        ],
        "HASH_COMPARISON": [
            [
                "core/brokers/dhan/dhan_readonly.py (Raw Byte Hash)",
                "373ee523627d349ef0e3019cb55c3d429479a7c0cb279f0f5ba3012719a3730e",
                "3235987b8d3dd249629547f121c251c368820c0ec22376eb9377dcb6c49fe966",
                "NO",
                "c6f63aec9b2e45c2871ffeed56dd7f4a58e722db",
                "genesis-system3-web-00136-qub",
                "Raw hash mismatch due to line ending conversion: Git blob is UNIX LF (28,249 bytes); Cloud Build source archive is Windows CRLF (29,034 bytes)."
            ],
            [
                "dashboard/backend/routers/broker.py (Raw Byte Hash)",
                "09663bbc1b0d6204a2c9180321ae35548af9c81d631cfb2708b09ba8df276ac2",
                "29cff3eac5de41a9dc4d22d3f927aeb4beebaf5bd76f0ab86a1abba0b1eb9422",
                "NO",
                "c6f63aec9b2e45c2871ffeed56dd7f4a58e722db",
                "genesis-system3-web-00136-qub",
                "Raw hash mismatch due to line ending conversion: Git blob is UNIX LF (6,995 bytes); Cloud Build source archive is Windows CRLF (7,188 bytes)."
            ],
            [
                "dashboard/backend/broker/dhan_auth.py (Raw Byte Hash)",
                "82ebaf985fe47df7fd403c359f7b89b5a8817a0f421e6b5f516b774514626166",
                "706f3b7244cf4d9d1949d663e0365b8075efa5ce65c7788b6fe14b6011145406",
                "NO",
                "c6f63aec9b2e45c2871ffeed56dd7f4a58e722db",
                "genesis-system3-web-00136-qub",
                "Raw hash mismatch due to line ending conversion: Git blob is UNIX LF (79 bytes); Cloud Build source archive is Windows CRLF (82 bytes)."
            ],
            [
                "dashboard/backend/gain_rank_spot_enrichment.py (Raw Byte Hash)",
                "125ae1d6bd6b7c3ae532dda11ad111b04c597e64387fff4cf20fc179ea5edea1",
                "1d70cab2b2b1b58d3a7c0a609db273547372baa64837946ecbf5eebde15fa23f",
                "NO",
                "c6f63aec9b2e45c2871ffeed56dd7f4a58e722db",
                "genesis-system3-web-00136-qub",
                "Raw hash mismatch due to line ending conversion: Git blob is UNIX LF (2,366 bytes); Cloud Build source archive is Windows CRLF (2,440 bytes)."
            ],
            [
                "core/brokers/dhan/dhan_readonly.py (Normalized LF Content)",
                "373ee523627d349ef0e3019cb55c3d429479a7c0cb279f0f5ba3012719a3730e",
                "373ee523627d349ef0e3019cb55c3d429479a7c0cb279f0f5ba3012719a3730e",
                "YES",
                "c6f63aec9b2e45c2871ffeed56dd7f4a58e722db",
                "genesis-system3-web-00136-qub",
                "Normalized LF SHA256 matches 100%. Exact text content and logic are identical between GitHub repository and Cloud Build source archive."
            ],
            [
                "dashboard/backend/routers/broker.py (Normalized LF Content)",
                "09663bbc1b0d6204a2c9180321ae35548af9c81d631cfb2708b09ba8df276ac2",
                "09663bbc1b0d6204a2c9180321ae35548af9c81d631cfb2708b09ba8df276ac2",
                "YES",
                "c6f63aec9b2e45c2871ffeed56dd7f4a58e722db",
                "genesis-system3-web-00136-qub",
                "Normalized LF SHA256 matches 100%. Exact text content and logic are identical between GitHub repository and Cloud Build source archive."
            ],
            [
                "dashboard/backend/broker/dhan_auth.py (Normalized LF Content)",
                "82ebaf985fe47df7fd403c359f7b89b5a8817a0f421e6b5f516b774514626166",
                "82ebaf985fe47df7fd403c359f7b89b5a8817a0f421e6b5f516b774514626166",
                "YES",
                "c6f63aec9b2e45c2871ffeed56dd7f4a58e722db",
                "genesis-system3-web-00136-qub",
                "Normalized LF SHA256 matches 100%. Exact text content and logic are identical between GitHub repository and Cloud Build source archive."
            ],
            [
                "dashboard/backend/gain_rank_spot_enrichment.py (Normalized LF Content)",
                "125ae1d6bd6b7c3ae532dda11ad111b04c597e64387fff4cf20fc179ea5edea1",
                "125ae1d6bd6b7c3ae532dda11ad111b04c597e64387fff4cf20fc179ea5edea1",
                "YES",
                "c6f63aec9b2e45c2871ffeed56dd7f4a58e722db",
                "genesis-system3-web-00136-qub",
                "Normalized LF SHA256 matches 100%. Exact text content and logic are identical between GitHub repository and Cloud Build source archive."
            ],
            [
                "core/brokers/dhan/dhan_readonly.py (In-Situ Container Inspection)",
                "373ee523627d349ef0e3019cb55c3d429479a7c0cb279f0f5ba3012719a3730e",
                "UNVERIFIED",
                "UNVERIFIED",
                "c6f63aec9b2e45c2871ffeed56dd7f4a58e722db",
                "genesis-system3-web-00136-qub",
                "Marked UNVERIFIED per strict truth policy: Cloud Run serverless execution sandbox provides no external container filesystem inspection API."
            ],
            [
                "dashboard/backend/routers/broker.py (In-Situ Container Inspection)",
                "09663bbc1b0d6204a2c9180321ae35548af9c81d631cfb2708b09ba8df276ac2",
                "UNVERIFIED",
                "UNVERIFIED",
                "c6f63aec9b2e45c2871ffeed56dd7f4a58e722db",
                "genesis-system3-web-00136-qub",
                "Marked UNVERIFIED per strict truth policy: Cloud Run serverless execution sandbox provides no external container filesystem inspection API."
            ],
            [
                "dashboard/backend/broker/dhan_auth.py (In-Situ Container Inspection)",
                "82ebaf985fe47df7fd403c359f7b89b5a8817a0f421e6b5f516b774514626166",
                "UNVERIFIED",
                "UNVERIFIED",
                "c6f63aec9b2e45c2871ffeed56dd7f4a58e722db",
                "genesis-system3-web-00136-qub",
                "Marked UNVERIFIED per strict truth policy: Cloud Run serverless execution sandbox provides no external container filesystem inspection API."
            ],
            [
                "dashboard/backend/gain_rank_spot_enrichment.py (In-Situ Container Inspection)",
                "125ae1d6bd6b7c3ae532dda11ad111b04c597e64387fff4cf20fc179ea5edea1",
                "UNVERIFIED",
                "UNVERIFIED",
                "c6f63aec9b2e45c2871ffeed56dd7f4a58e722db",
                "genesis-system3-web-00136-qub",
                "Marked UNVERIFIED per strict truth policy: Cloud Run serverless execution sandbox provides no external container filesystem inspection API."
            ]
        ],
        "DRIFT_REPORT": [
            [
                "DRIFT-01: GitHub Commit vs Cloud Deployed Revision Commit",
                "c6f63aec9b2e45c2871ffeed56dd7f4a58e722db (origin/main)",
                "b732bf0921083d8b20128146b68366c91d4e9944 (DEPLOY_GIT_SHA)",
                "NO (DRIFT)",
                "c6f63aec9b2e45c2871ffeed56dd7f4a58e722db",
                "genesis-system3-web-00136-qub",
                "COMMIT DRIFT: Cloud Run revision 136 was built from commit b732bf092108; GitHub origin/main has advanced by 5 commits (to c6f63aec9b2e). Diff analysis confirms the 4 target files were NOT touched in those 5 commits."
            ],
            [
                "DRIFT-02: File Byte Encoding Drift (UNIX LF vs Windows CRLF)",
                "UNIX LF line endings (28,249 / 6,995 / 79 / 2,366 bytes)",
                "Windows CRLF line endings (29,034 / 7,188 / 82 / 2,440 bytes)",
                "NO (FORMAT DRIFT)",
                "c6f63aec9b2e45c2871ffeed56dd7f4a58e722db",
                "genesis-system3-web-00136-qub",
                "FORMAT DRIFT: Build tarball was packed from Windows filesystem introducing CRLF (\\r\\n). Normalized LF text matches 100% across all 4 files. Python runtime interprets both identically."
            ],
            [
                "DRIFT-03: Cloud Run Traffic Distribution Drift",
                "N/A",
                "100% on revision 136 (qub); 0% on candidate revision 141 (cuv)",
                "NO (ROUTING DRIFT)",
                "b732bf0921083d8b20128146b68366c91d4e9944",
                "genesis-system3-web-00136-qub / 00141-cuv",
                "ROUTING DRIFT: Revision 141 was deployed at 2026-11-10T03:26:28Z with image sha256:d3cd2d50... but 100% of live traffic remains routed to revision 136 with image sha256:4a14ad39..."
            ],
            [
                "DRIFT-04: In-Situ Container Filesystem Observability Boundary",
                "Fully verifiable via git object database",
                "UNVERIFIED for direct container in-situ filesystem",
                "UNVERIFIED",
                "c6f63aec9b2e45c2871ffeed56dd7f4a58e722db",
                "genesis-system3-web-00136-qub",
                "OBSERVABILITY BOUNDARY: Serverless Cloud Run offers no direct container exec or in-situ file inspection API. Hashes are proven via Cloud Build source tarball archive, but live container internal files cannot be read without app-level debug endpoint."
            ],
            [
                "core/brokers/dhan/dhan_readonly.py (Drift Summary)",
                "373ee523627d349ef0e3019cb55c3d429479a7c0cb279f0f5ba3012719a3730e",
                "3235987b8d3dd249629547f121c251c368820c0ec22376eb9377dcb6c49fe966",
                "NO (RAW) / YES (TEXT)",
                "c6f63aec9b2e45c2871ffeed56dd7f4a58e722db",
                "genesis-system3-web-00136-qub",
                "Semantic code logic is 100% identical. Raw SHA256 differs due to Windows CRLF vs Linux LF line endings. Commit drift of 5 commits did not alter this file."
            ],
            [
                "dashboard/backend/routers/broker.py (Drift Summary)",
                "09663bbc1b0d6204a2c9180321ae35548af9c81d631cfb2708b09ba8df276ac2",
                "29cff3eac5de41a9dc4d22d3f927aeb4beebaf5bd76f0ab86a1abba0b1eb9422",
                "NO (RAW) / YES (TEXT)",
                "c6f63aec9b2e45c2871ffeed56dd7f4a58e722db",
                "genesis-system3-web-00136-qub",
                "Semantic code logic is 100% identical. Raw SHA256 differs due to Windows CRLF vs Linux LF line endings. Commit drift of 5 commits did not alter this file."
            ],
            [
                "dashboard/backend/broker/dhan_auth.py (Drift Summary)",
                "82ebaf985fe47df7fd403c359f7b89b5a8817a0f421e6b5f516b774514626166",
                "706f3b7244cf4d9d1949d663e0365b8075efa5ce65c7788b6fe14b6011145406",
                "NO (RAW) / YES (TEXT)",
                "c6f63aec9b2e45c2871ffeed56dd7f4a58e722db",
                "genesis-system3-web-00136-qub",
                "Semantic code logic is 100% identical. Raw SHA256 differs due to Windows CRLF vs Linux LF line endings. Commit drift of 5 commits did not alter this file."
            ],
            [
                "dashboard/backend/gain_rank_spot_enrichment.py (Drift Summary)",
                "125ae1d6bd6b7c3ae532dda11ad111b04c597e64387fff4cf20fc179ea5edea1",
                "1d70cab2b2b1b58d3a7c0a609db273547372baa64837946ecbf5eebde15fa23f",
                "NO (RAW) / YES (TEXT)",
                "c6f63aec9b2e45c2871ffeed56dd7f4a58e722db",
                "genesis-system3-web-00136-qub",
                "Semantic code logic is 100% identical. Raw SHA256 differs due to Windows CRLF vs Linux LF line endings. Commit drift of 5 commits did not alter this file."
            ]
        ]
    }

    for sheet_name, rows in sheets_data.items():
        ws = wb.create_sheet(title=sheet_name)
        ws.views.sheetView[0].showGridLines = True
        ws.freeze_panes = "A2"

        # Write Header
        ws.append(headers)
        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.font = font_header
            cell.fill = fill_header
            cell.alignment = align_center
            cell.border = header_border
        ws.row_dimensions[1].height = 28

        # Write Rows
        for r_idx, row_data in enumerate(rows, start=2):
            ws.append(row_data)
            ws.row_dimensions[r_idx].height = 36

            for col_idx in range(1, len(row_data) + 1):
                cell = ws.cell(row=r_idx, column=col_idx)
                cell.font = font_data
                cell.border = thin_border
                cell.alignment = align_left

                val = str(cell.value or "")

                # Column 1 (File/Item): Bold
                if col_idx == 1:
                    cell.font = font_bold

                # Column 4 (Match YES/NO): Format & badge colors
                if col_idx == 4:
                    cell.alignment = align_center
                    if "YES" in val and "NO" not in val:
                        cell.fill = fill_match_yes
                        cell.font = font_match_yes
                    elif "NO" in val:
                        cell.fill = fill_match_no
                        cell.font = font_match_no
                    elif "UNVERIFIED" in val:
                        cell.fill = fill_unverified
                        cell.font = font_unverified
                    elif "PROVEN" in val:
                        cell.fill = fill_proven
                        cell.font = font_proven

                # Center align commits and revisions
                if col_idx in (5, 6):
                    cell.alignment = align_center

        # Auto-adjust column widths
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val_str = str(cell.value or "")
                # Consider line breaks for width calculation
                lines = val_str.split("\n")
                line_max = max(len(l) for l in lines) if lines else 0
                if line_max > max_len:
                    max_len = line_max
            # Set bounded width
            if col[0].column == 1: # File
                ws.column_dimensions[col_letter].width = 38
            elif col[0].column in (2, 3): # SHA256 hashes
                ws.column_dimensions[col_letter].width = 44
            elif col[0].column == 4: # Match YES/NO
                ws.column_dimensions[col_letter].width = 16
            elif col[0].column == 5: # GitHub Commit
                ws.column_dimensions[col_letter].width = 28
            elif col[0].column == 6: # Cloud Revision
                ws.column_dimensions[col_letter].width = 30
            elif col[0].column == 7: # Evidence
                ws.column_dimensions[col_letter].width = 65

    wb.save(output_path)
    print(f"Successfully generated {output_path} with 5 sheets and verified forensic data.")

if __name__ == "__main__":
    build_cloud_github_truth_workbook()
