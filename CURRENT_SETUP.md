# Current Local Setup Documentation

## ✅ What's Already Working:
- Local development server at port 5000
- TypeScript compilation working
- Dependencies installed (699 packages)
- Environment variables configured in `.env`
- Database schema ready (in `shared/schema.ts`)
- Server structure organized:
  - `server/` - Backend TypeScript files
  - `shared/` - Common schemas and utilities
  - Root - React frontend components

## 🔧 Local Development:
```bash
# Start development server
npm run dev

# Will start at: http://localhost:5000
```

## 📁 Project Structure:
```
/Users/treefanevents/
├── server/
│   ├── simple-server.ts (current dev server)
│   ├── index.ts (full server - needs path fixes)
│   └── various route files
├── shared/
│   ├── schema.ts (database schema)
│   ├── analytics.ts
│   └── other shared utilities
├── .env (local environment variables)
├── package.json (updated scripts)
└── React components (*.tsx files)
```

## 🗄️ Database Status:
- Schema: PostgreSQL/SQLite compatible
- Current: Using SQLite for local dev (`tasks.db`)
- Production: Ready for PostgreSQL migration

## 🔄 Next Session Commands:
1. `cd /Users/treefanevents`
2. `npm run dev` (to start local server)
3. Open `MIGRATION_CHECKLIST.md`
4. Continue migration from Phase 2

## 📋 Environment Variables Needed from Replit:
- [ ] DATABASE_URL
- [ ] SESSION_SECRET
- [ ] OPENAI_API_KEY
- [ ] SLACK_BOT_TOKEN
- [ ] SLACK_SIGNING_SECRET
- [ ] STRIPE_SECRET_KEY
- [ ] VITE_STRIPE_PUBLIC_KEY
- [ ] Any other secrets

## 🎯 Goal:
Migrate from Replit ($20+/month) to Railway ($5/month) while keeping domain `aitaskmanager.pro`