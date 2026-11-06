# Supabase Row-Level Security (RLS) and Auth

## Declarative Database Authorization
PostgreSQL Row-Level Security (RLS) evaluates access policies at the SQL engine level, guaranteeing that API clients cannot bypass permissions even if frontend code is manipulated.

```sql
-- Enable RLS on document table
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Policy 1: Users can read their own documents
CREATE POLICY "Users can read own documents"
ON documents FOR SELECT
USING (auth.uid() = user_id);

-- Policy 2: Organization admins can view all org documents
CREATE POLICY "Org Admins can view org documents"
ON documents FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM org_memberships
    WHERE org_memberships.org_id = documents.org_id
      AND org_memberships.user_id = auth.uid()
      AND org_memberships.role = 'ADMIN'
  )
);
```
