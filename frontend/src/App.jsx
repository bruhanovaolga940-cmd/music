import { useState } from "react";
import { fileUrl, requestDownload } from "./api/client";

const QUALITY_OPTIONS = {
  audio: [
    { value: "best", label: "Лучшее" },
    { value: "medium", label: "192 kbps" },
    { value: "low", label: "128 kbps" },
  ],
  video: [
    { value: "best", label: "Максимум" },
    { value: "1080", label: "1080p" },
    { value: "720", label: "720p" },
    { value: "480", label: "480p" },
  ],
};

export default function App() {
  const [url, setUrl] = useState("");
  const [kind, setKind] = useState("audio");
  const [quality, setQuality] = useState("best");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const switchKind = (next) => {
    setKind(next);
    setQuality("best");
    setResult(null);
    setError(null);
  };

  const submit = async (e) => {
    e.preventDefault();
    if (!url.trim() || loading) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      setResult(await requestDownload(url.trim(), kind, quality));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Неизвестная ошибка");
    } finally {
      setLoading(false);
    }
  };

  const save = (filename) => {
    const a = document.createElement("a");
    a.href = fileUrl(filename);
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
  };

  return (
    <div className="min-h-dvh bg-slate-950 text-slate-100 flex justify-center px-4 py-10">
      <div className="w-full max-w-lg">
        <h1 className="text-2xl font-semibold mb-1">Загрузчик с YouTube</h1>
        <p className="text-slate-400 text-sm mb-6">
          Вставьте ссылку и выберите, что нужно сохранить.
        </p>

        <div className="grid grid-cols-2 gap-2 mb-6 rounded-xl bg-slate-900 p-1">
          {[
            { value: "audio", label: "Аудио" },
            { value: "video", label: "Видео" },
          ].map((tab) => (
            <button
              key={tab.value}
              type="button"
              onClick={() => switchKind(tab.value)}
              className={`rounded-lg py-2 text-sm font-medium transition ${
                kind === tab.value
                  ? "bg-slate-700 text-white"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <form onSubmit={submit} className="space-y-4">
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://www.youtube.com/watch?v=..."
            className="w-full rounded-xl bg-slate-900 border border-slate-800 px-4 py-3
                       outline-none focus:border-emerald-500"
          />

          <div className="flex flex-wrap gap-2">
            {QUALITY_OPTIONS[kind].map((q) => (
              <button
                key={q.value}
                type="button"
                onClick={() => setQuality(q.value)}
                className={`flex-1 rounded-xl px-3 py-2 text-sm border transition ${
                  quality === q.value
                    ? "bg-emerald-600 border-emerald-500 text-white"
                    : "bg-slate-900 border-slate-800 text-slate-300"
                }`}
              >
                {q.label}
              </button>
            ))}
          </div>

          <button
            type="submit"
            disabled={loading || !url.trim()}
            className="w-full rounded-xl bg-emerald-600 hover:bg-emerald-500
                       disabled:opacity-40 disabled:cursor-not-allowed
                       px-4 py-3 font-medium transition"
          >
            {loading
              ? kind === "video"
                ? "Скачиваю видео…"
                : "Скачиваю аудио…"
              : kind === "video"
                ? "Скачать видео"
                : "Скачать mp3"}
          </button>
        </form>

        {loading && (
          <p className="mt-6 text-sm text-slate-400">
            {kind === "video"
              ? "Видео качается дольше аудио: 20–90 секунд в зависимости от длины."
              : "Обычно 5–20 секунд. Не закрывайте вкладку."}
          </p>
        )}

        {error && (
          <div className="mt-6 rounded-xl border border-red-900 bg-red-950/50 p-4 text-sm text-red-300">
            {error}
          </div>
        )}

        {result && (
          <div className="mt-6 rounded-xl border border-slate-800 bg-slate-900 p-4">
            <p className="text-sm text-slate-400 mb-1 break-all">{result.filename}</p>
            {result.filesize_mb != null && (
              <p className="text-xs text-slate-500">{result.filesize_mb} МБ</p>
            )}
            <button
              onClick={() => save(result.filename)}
              className="mt-3 w-full rounded-lg bg-slate-800 hover:bg-slate-700 px-4 py-2 text-sm"
            >
              Сохранить в «Загрузки»
            </button>
          </div>
        )}
      </div>
    </div>
  );
}