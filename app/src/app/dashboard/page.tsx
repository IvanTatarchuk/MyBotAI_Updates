import { cookies } from "next/headers";
import Link from "next/link";
import AIClient from "./AIClient";

export default async function DashboardPage() {
  const cookieStore = await cookies();
  const isAuthed = cookieStore.get("demo_auth")?.value === "1";
  if (!isAuthed) {
    return (
      <div className="p-6">
        <p className="mb-4">Ви не авторизовані.</p>
        <Link className="underline" href="/login">Перейти до входу</Link>
      </div>
    );
  }

  return (
    <div className="max-w-2xl p-6 space-y-4">
      <h1 className="text-2xl font-semibold">Дашборд</h1>
      <AIClient />
    </div>
  );
}
