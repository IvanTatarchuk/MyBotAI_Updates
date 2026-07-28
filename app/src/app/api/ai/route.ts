import { NextRequest } from "next/server";

export async function POST(request: NextRequest) {
  try {
    const { prompt } = await request.json();
    if (!prompt || typeof prompt !== "string") {
      return new Response(JSON.stringify({ error: "Missing prompt" }), {
        status: 400,
        headers: { "content-type": "application/json" },
      });
    }

    const reversed = prompt.split("").reverse().join("");
    const message = `Echo AI (demo): ${reversed}`;

    return new Response(JSON.stringify({ message }), {
      status: 200,
      headers: { "content-type": "application/json" },
    });
  } catch (error) {
    return new Response(JSON.stringify({ error: "Invalid JSON" }), {
      status: 400,
      headers: { "content-type": "application/json" },
    });
  }
}
