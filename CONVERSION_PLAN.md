# 📋 MongoDB Conversion Plan

## Current Status:
- app.py: 828 lines
- Database: MySQL queries throughout
- Complexity: High (many JOINs, complex queries)

## Conversion Strategy:

### Phase 1: Core Routes (DONE ✅)
- ✅ Imports updated
- ✅ get_workers() converted
- ✅ Landing page counts converted
- ✅ Login converted
- ✅ Register converted
- ✅ User dashboard converted

### Phase 2: Admin & Department Routes (IN PROGRESS)
Routes that need conversion:
1. `/admin/dashboard` - Complex JOINs
2. `/department/<dept_name>` - JOINs with users
3. `/submit_complaint` - INSERT
4. `/update_status/<id>` - UPDATE
5. `/add_worker` - INSERT + UPDATE
6. `/upload_admin_image/<id>` - UPDATE
7. `/feedback` routes - INSERT + SELECT
8. Department admin routes - Multiple queries

### Phase 3: Testing & Deployment
1. Test locally
2. Fix bugs
3. Push to GitHub
4. Deploy to Render

## Estimated Time:
- Phase 2: 2 hours
- Phase 3: 1 hour
- **Total remaining: 3 hours**

## Current Approach:
Creating helper functions for each route type, then replacing route by route.

## Progress: 30% Complete

Next: Convert admin_dashboard route
