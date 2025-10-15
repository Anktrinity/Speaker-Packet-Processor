# 🚀 Replit → Railway Migration Checklist

## Current Status: ✅ Local Development Setup Complete

Your app is already running locally at: `npm run dev` (port 5000)

## Next Steps to Complete Migration:

### Phase 1: Preparation ⏳
- [ ] **Download Replit codebase** (if not already done)
- [ ] **Document current Replit environment variables**
  - DATABASE_URL
  - SESSION_SECRET
  - OPENAI_API_KEY
  - SLACK_BOT_TOKEN
  - SLACK_SIGNING_SECRET
  - STRIPE_SECRET_KEY
  - VITE_STRIPE_PUBLIC_KEY
  - Any other secrets from Replit

### Phase 2: Set Up Railway ⏳
- [ ] **Install Railway CLI**: `npm install -g @railway/cli`
- [ ] **Create Railway account**: `railway login`
- [ ] **Initialize project**: `railway init`
- [ ] **Add PostgreSQL service** in Railway dashboard
- [ ] **Copy new DATABASE_URL** from Railway

### Phase 3: Deploy & Test ⏳
- [ ] **Deploy to Railway**: `railway up`
- [ ] **Set all environment variables** in Railway dashboard
- [ ] **Test Railway deployment** at provided URL
- [ ] **Migrate database data** from Replit to Railway

### Phase 4: Test Everything ⏳
- [ ] **Test user authentication**
- [ ] **Test task creation/management**
- [ ] **Test Slack integration**
- [ ] **Test AI features**
- [ ] **Test payment processing**
- [ ] **Verify all API endpoints work**

### Phase 5: Switch Domain ⏳
- [ ] **Add custom domain** `aitaskmanager.pro` in Railway
- [ ] **Update DNS records** in domain registrar
- [ ] **Test domain works** with new deployment
- [ ] **Verify SSL certificate** is working

### Phase 6: Final Steps ⏳
- [ ] **Monitor for 24-48 hours**
- [ ] **Export any final data** from Replit if needed
- [ ] **Cancel Replit subscription**
- [ ] **Update any external webhooks** to new domain
- [ ] **Celebrate saving $20+/month!** 🎉

## Important Commands to Remember:

### Start Local Development:
```bash
npm run dev
```

### Deploy to Railway:
```bash
railway up
```

### Set Environment Variables:
```bash
railway variables set VAR_NAME=value
```

### Database Migration:
```bash
# Export from Replit
pg_dump $REPLIT_DATABASE_URL > backup.sql

# Import to Railway
psql $RAILWAY_DATABASE_URL < backup.sql
```

## 🛡️ Safety Notes:
- Keep Replit running during entire migration
- Use short DNS TTL (300 seconds) for quick rollback
- Test everything thoroughly before canceling Replit
- Have this checklist open during migration

## 📞 When You Resume:
1. Open this file: `MIGRATION_CHECKLIST.md`
2. Start local server: `npm run dev`
3. Continue from where you left off in checklist
4. Reference the detailed steps in your saved conversation

## 💡 Pro Tips:
- Do migration during low traffic hours
- Keep browser tabs open to both Replit and Railway dashboards
- Take screenshots of working Replit setup before changing anything
- Test each phase completely before moving to next

---
**Created**: $(date)
**Local Setup**: ✅ Complete
**Next**: Railway deployment