"use client";
import { useState } from "react";

export default function AIClient() {
  const [prompt, setPrompt] = useState("");
  const [output, setOutput] = useState<string>("");
  const [loading, setLoading] = useState(false);

  async function onSend() {
    setLoading(true);
    setOutput("...");
    try {
      const res = await fetch("/api/ai", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ prompt }),
      });
      const data = await res.json();
      setOutput(JSON.stringify(data, null, 2));
    } catch (err) {
      setOutput("Error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-2">
      <label className="block text-sm">Промпт</label>
      <input
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        className="w-full border rounded px-3 py-2"
        placeholder="Введіть текст"
      />
      <button
        type="button"
        onClick={onSend}
        disabled={loading}
        className="rounded bg-black text-white px-4 py-2 disabled:opacity-50"
      >
        {loading ? "Надсилаю..." : "Надіслати"}
      </button>
      <pre className="bg-gray-100 rounded p-3 whitespace-pre-wrap">{output}</pre>
    </div>
  );
}
