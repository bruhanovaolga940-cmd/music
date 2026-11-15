const API = "/api";

/**
 * @param {string} url
 * @param {"best" | "medium" | "low"} quality
 */
export async function requestDownload(url, quality) {
  const res = await fetch(`${API}/download`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, quality }),
  });

  const data = await res.json().catch(() => null);

  if (!res.ok) {
    throw new Error(data?.detail ?? `Ошибка ${res.status}`);
  }
  return data;
}

export function fileUrl(filename) {
  return `${API}/download/file/${encodeURIComponent(filename)}`;
}