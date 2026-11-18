const API = "/api";

export async function requestDownload(url, kind = "audio", quality = "best") {
  const res = await fetch(`${API}/download`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, kind, quality }),
  });

  const data = await res.json().catch(() => null);
  if (!res.ok) throw new Error(data?.detail ?? `Ошибка ${res.status}`);
  return data;
}

export function fileUrl(filename) {
  return `${API}/download/file/${encodeURIComponent(filename)}`;
}