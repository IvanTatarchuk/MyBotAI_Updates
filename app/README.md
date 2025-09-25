This is a modern Next.js SaaS foundation scaffold.

## Getting Started

Quickstart

1. Install deps: `npm install`
2. Copy env: `cp .env.example .env`
3. Migrate DB (SQLite dev): `npx prisma migrate dev`
4. Start dev: `npm run dev`

Open [http://localhost:3000](http://localhost:3000).

Routes: `src/app/login`, `src/app/dashboard`, `src/app/api/ai`.

Demo login: go to `/login` and use password `NEXT_PUBLIC_DEMO_PASSWORD` (default `demo`).

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.

## Environment

- Copy `.env.example` to `.env`
- Update `NEXT_PUBLIC_DEMO_PASSWORD` if desired

## Routes

- `/login` – demo login (password protected)
- `/dashboard` – protected page with AI demo form
- `/api/ai` – demo AI endpoint (echo)
