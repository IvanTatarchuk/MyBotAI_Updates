"use client";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

export default function LoginPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    const formData = new FormData(event.currentTarget);
    const password = String(formData.get("password") || "");
    if (password !== (process.env.NEXT_PUBLIC_DEMO_PASSWORD || "demo")) {
      setError("Невірний пароль");
      return;
    }
    document.cookie = `demo_auth=1; path=/; samesite=lax`;
    router.push("/dashboard");
  }

  return (
    <div className="min-h-dvh grid place-items-center p-6">
      <form onSubmit={onSubmit} className="w-full max-w-sm space-y-4">
        <h1 className="text-2xl font-semibold">Вхід</h1>
        <input
          name="password"
          type="password"
          placeholder="Пароль (demo)"
          className="w-full border rounded px-3 py-2"
          required
        />
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button
          type="submit"
          className="inline-flex items-center justify-center rounded bg-black text-white px-4 py-2"
        >
          Увійти
        </button>
      </form>
    </div>
  );
}
