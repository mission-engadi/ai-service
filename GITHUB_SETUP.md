# GitHub Repository Setup - AI Service

## Step 1: Create GitHub Repository

### Option A: Using GitHub Web Interface (Recommended)

1. **Go to GitHub**: https://github.com/mission-engadi
2. **Click "New repository"**
3. **Repository details:**
   - Repository name: `ai-service`
   - Description: `AI-powered content generation, translation, and automation service for Mission Engadi`
   - Visibility: **Private** (or Public if preferred)
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
4. **Click "Create repository"**

### Option B: Using GitHub CLI (if installed)

```bash
gh repo create mission-engadi/ai-service \
  --private \
  --description "AI-powered content generation, translation, and automation service" \
  --source=. \
  --remote=origin \
  --push
```

---

## Step 2: Configure Repository Topics

After creating the repo, add these topics:
- `fastapi`
- `python`
- `ai`
- `microservice`
- `mission-engadi`
- `abacus-ai`
- `content-generation`
- `translation`

---

## Step 3: Push to GitHub

### Method 1: Using HTTPS (with Personal Access Token)

**3.1 Add remote:**
```bash
cd /home/ubuntu/ai_service
git remote add origin https://github.com/mission-engadi/ai-service.git
```

**3.2 Push:**
```bash
git push -u origin master
```

**If authentication fails**, you need a Personal Access Token:
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo`, `workflow`
4. Copy the token
5. Use token as password when prompted

---

### Method 2: Using SSH (Recommended)

**3.1 Check for existing SSH key:**
```bash
ls -la ~/.ssh/id_*.pub
```

**3.2 If no key exists, generate one:**
```bash
ssh-keygen -t ed25519 -C "misionengadi@gmail.com"
# Press Enter to accept default location
# Enter passphrase (optional)
```

**3.3 Add SSH key to GitHub:**
```bash
# Copy public key
cat ~/.ssh/id_ed25519.pub
```

1. Go to https://github.com/settings/keys
2. Click "New SSH key"
3. Paste the key
4. Click "Add SSH key"

**3.4 Test SSH connection:**
```bash
ssh -T git@github.com
# Should see: "Hi mission-engadi! You've successfully authenticated..."
```

**3.5 Add SSH remote:**
```bash
cd /home/ubuntu/ai_service
git remote add origin git@github.com:mission-engadi/ai-service.git
```

**3.6 Push:**
```bash
git push -u origin master
```

---

## Step 4: Configure Repository Settings

### Branch Protection (Recommended for Production)

1. Go to repository **Settings** → **Branches**
2. Add branch protection rule for `master`:
   - ✅ Require pull request reviews before merging
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging

### GitHub Actions Permissions

From the screenshots, ensure proper permissions:

1. Go to **Settings** → **Actions** → **General**
2. Workflow permissions:
   - ✅ Read and write permissions
   - ✅ Allow GitHub Actions to create and approve pull requests

### Secrets (for CI/CD)

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add repository secrets:
   - `DATABASE_URL`
   - `SECRET_KEY`
   - `JWT_SECRET_KEY`
   - `ABACUS_API_KEY`

---

## Step 5: Verify Push

**Check repository:**
```bash
git remote -v
git log --oneline -5
```

**Visit GitHub:**
https://github.com/mission-engadi/ai-service

You should see:
- ✅ 43 files
- ✅ README.md displayed
- ✅ All documentation files
- ✅ Complete service implementation

---

## Troubleshooting

### Error: "Authentication failed"

**For HTTPS:**
- Use Personal Access Token as password
- Token needs `repo` and `workflow` scopes

**For SSH:**
- Ensure SSH key is added to GitHub
- Test: `ssh -T git@github.com`
- Check key: `cat ~/.ssh/id_ed25519.pub`

### Error: "Permission denied (workflows)"

Based on the Permission Fix screenshot:
1. Go to **AbacusAI GitHub App Settings**
2. Ensure `workflows` permission is enabled
3. OR use SSH authentication instead

### Error: "Repository already exists"

If you created it already:
```bash
git remote add origin https://github.com/mission-engadi/ai-service.git
# or
git remote add origin git@github.com:mission-engadi/ai-service.git

git push -u origin master
```

---

## Quick Command Summary

```bash
# Using HTTPS
cd /home/ubuntu/ai_service
git remote add origin https://github.com/mission-engadi/ai-service.git
git push -u origin master

# Using SSH (recommended)
cd /home/ubuntu/ai_service
git remote add origin git@github.com:mission-engadi/ai-service.git
git push -u origin master
```

---

**Status**: Ready to push ✅  
**Total Commits**: 2  
**Total Files**: 43  
**Lines Added**: 7,627  

---

**Created**: December 2024
