---
title: Next.js App Router, Server Components & Streaming SSR
category: Full-Stack & Systems Engineering
tags: [frontend, nextjs, react, rsc, typescript]
created: 2026-11-01
status: ACTIVE
related: "[[TypeScript_Advanced_Type_System]], [[FastAPI_High_Performance_Design]], [[PostgreSQL_Query_Optimization]]"
---

# Next.js App Router, Server Components & Streaming SSR

Next.js represents the state of the art in full-stack React application architecture, leveraging **React Server Components (RSC)**, streaming server-side rendering, and integrated edge middleware.

## React Server Components (RSC) Paradigm
- **Server by Default:** Components in the App Router run exclusively on the server unless explicitly annotated with `'use client'`.
- **Zero Client Bundle Impact:** Heavy dependencies (like markdown parsers, database drivers, date formatters) execute on the server and transmit only serialized HTML/JSON to the client browser.
- **Direct Database Access:** RSCs fetch data directly via ORMs or SQL queries without needing separate REST or GraphQL endpoints.

## Streaming with Suspense
Streaming breaks page rendering into chunks, flushing fast outer UI skeletons immediately while slow async data fetches stream in progressively, boosting Time to First Byte (TTFB) and First Contentful Paint (FCP).

See also: [[TypeScript_Advanced_Type_System]], [[FastAPI_High_Performance_Design]], [[PostgreSQL_Query_Optimization]].
