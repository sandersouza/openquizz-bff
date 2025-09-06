export async function joinGame(name: string, code: string) {
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE}/join`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, code }),
  });

  if (!res.ok) {
    throw new Error("Failed to join");
  }

  return res.json();
}
