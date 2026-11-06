# Next.js 15 App Router and Server Actions Architecture

## Core Architectural Primitives
Next.js 15 leverages React 19 architecture, unifying frontend rendering and backend mutations:
1. **React Server Components (RSC):** Render exclusively on the server, streaming lightweight virtual DOM representations to the client with zero bundle-size overhead.
2. **Server Actions (`'use server'`):** Asynchronous functions executed on the server, callable directly from client forms or event handlers without writing boilerplate REST/GraphQL routes.

```tsx
// app/actions/update-profile.ts
'use server';
import { z } from 'zod';
import { prisma } from '@/lib/db';
import { revalidatePath } from 'next/cache';

const ProfileSchema = z.object({
  name: z.string().min(2),
  bio: z.string().max(250),
});

export async function updateProfile(formData: FormData) {
  const parsed = ProfileSchema.safeParse(Object.fromEntries(formData));
  if (!parsed.success) return { error: parsed.error.flatten() };

  await prisma.user.update({
    where: { id: 'user_123' },
    data: parsed.data,
  });

  revalidatePath('/profile');
  return { success: true };
}
```

## Caching Behavior in Next.js 15
Next.js 15 changed `fetch` requests, `GET` route handlers, and client navigations to **uncached by default**, giving developers complete predictability over live data freshness.
