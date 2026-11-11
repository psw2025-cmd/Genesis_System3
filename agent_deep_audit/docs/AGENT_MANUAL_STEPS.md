# What You Must Do (One-Time) for Full Agent Autonomy

After running `agent_autonomous_setup.ps1`, **2 manual steps** remain. The agent cannot do these.

---

## Step 1: GitHub Email Setting

**Why:** Prevents GH007 "private email" push rejection.

**What to do:**
1. Open: **https://github.com/settings/emails**
2. Find: **"Block command line pushes that expose my email address"**
3. Turn it **OFF** (uncheck the box)
4. Save if there is a button

---

## Step 2: First Git Push (Store Credentials)

**Why:** Git Credential Manager needs you to sign in once. After that, the agent can push without you.

**What to do:**
1. Open PowerShell in `C:\Genesis_System3`
2. Run:
   ```powershell
   git push
   ```
3. When prompted, sign in to GitHub (browser or dialog)
4. Done – credentials are stored for future pushes

---

## Optional: Run Finish Script

To commit the setup changes and see this summary again:

```powershell
cd C:\Genesis_System3
powershell -ExecutionPolicy Bypass -File .\scripts\agent_finish_setup.ps1
```

---

## After Both Steps

| Agent can do | Without you |
|--------------|-------------|
| Run pytest, black, flake8 | ✓ |
| Edit files, fix issues | ✓ |
| `git add`, `git commit` | ✓ |
| `git push` | ✓ (credentials stored) |
| Change GitHub settings | ✗ (browser only) |
| Answer interactive prompts (y/n) | ✗ |

---

## Checklist

- [ ] Step 1: Turn OFF "Block command line pushes" at github.com/settings/emails
- [ ] Step 2: Run `git push` once and sign in
- [ ] Optional: Run `agent_finish_setup.ps1` to commit setup changes
