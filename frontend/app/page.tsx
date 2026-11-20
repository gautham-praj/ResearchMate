
"use client";

import { FormEvent, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const API_URL = "http://127.0.0.1:8000";

interface UploadedDocument {
  document_id: string;
  filename: string;
  page_count: number;
  chunk_count: number;
}

interface Source {
  page_number: number;
  chunk_index: number;
  score: number;
  text: string;
}

interface Answer {
  answer: string;
  sources: Source[];
}

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [document, setDocument] = useState<UploadedDocument | null>(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<Answer | null>(null);
  const [uploading, setUploading] = useState(false);
  const [asking, setAsking] = useState(false);
  const [error, setError] = useState("");

  async function getErrorMessage(response: Response) {
    const body = await response.json().catch(() => ({}));
    return body.detail || `Request failed (${response.status})`;
  }

  async function handleUpload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!file) {
      setError("Please select a PDF first.");
      return;
    }

    setUploading(true);
    setError("");
    setDocument(null);
    setAnswer(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(`${API_URL}/documents/upload`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(await getErrorMessage(response));
      }

      const result: UploadedDocument = await response.json();
      setDocument(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed.");
    } finally {
      setUploading(false);
    }
  }

  async function handleAsk(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!document || !question.trim()) return;

    setAsking(true);
    setError("");
    setAnswer(null);

    try {
      const response = await fetch(
        `${API_URL}/documents/${document.document_id}/ask`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ question }),
        }
      );

      if (!response.ok) {
        throw new Error(await getErrorMessage(response));
      }

      const result: Answer = await response.json();
      setAnswer(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Question failed.");
    } finally {
      setAsking(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 px-4 py-10 text-white sm:px-6">
      <div className="mx-auto max-w-4xl">
        <header className="mb-12 text-center">
          <h1 className="text-4xl font-bold tracking-tight">
            ResearchMate
          </h1>
          <p className="mt-3 text-slate-400">
            Your AI-powered assistant for understanding PDF documents.
          </p>
        </header>

        <section className="rounded-xl border border-slate-700 bg-slate-900 p-6">
          <h2 className="text-xl font-semibold">1. Upload a document</h2>

          <form onSubmit={handleUpload} className="mt-5 space-y-4">
            <input
              type="file"
              accept=".pdf,application/pdf"
              onChange={(event) =>
                setFile(event.target.files?.[0] ?? null)
              }
              className="block w-full text-sm text-slate-300 file:mr-4 file:rounded-lg file:border-0 file:bg-blue-600 file:px-4 file:py-2 file:font-medium file:text-white hover:file:bg-blue-500"
            />

            <button
              type="submit"
              disabled={!file || uploading}
              className="rounded-lg bg-blue-600 px-5 py-2.5 font-medium hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {uploading ? "Uploading and processing..." : "Upload PDF"}
            </button>
          </form>
        </section>

        {document && (
          <section className="mt-6 rounded-xl border border-green-800 bg-slate-900 p-6">
            <h2 className="text-xl font-semibold text-green-400">
              Document processed successfully
            </h2>

            <p className="mt-3 text-slate-300">
              <strong>Filename:</strong> {document.filename}
            </p>
            <p className="text-slate-300">
              <strong>Pages:</strong> {document.page_count}
            </p>
          </section>
        )}

        {document && (
          <section className="mt-6 rounded-xl border border-slate-700 bg-slate-900 p-6">
            <h2 className="text-xl font-semibold">2. Ask a question</h2>

            <form onSubmit={handleAsk} className="mt-5 space-y-4">
              <textarea
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                placeholder="Ask something about your PDF..."
                rows={3}
                className="w-full rounded-lg border border-slate-700 bg-slate-950 p-3 text-white placeholder:text-slate-500 focus:border-blue-500 focus:outline-none"
              />

              <button
                type="submit"
                disabled={!question.trim() || asking}
                className="rounded-lg bg-blue-600 px-5 py-2.5 font-medium hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {asking ? "Thinking..." : "Ask ResearchMate"}
              </button>
            </form>
          </section>
        )}

        {error && (
          <div className="mt-6 rounded-lg border border-red-800 bg-red-950 p-4 text-red-300">
            {error}
          </div>
        )}

        {answer && (
          <section className="mt-6 rounded-xl border border-slate-700 bg-slate-900 p-6">
            <h2 className="text-xl font-semibold">Answer</h2>

            <article className="markdown-answer mt-5 space-y-4 text-slate-200">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  h1: ({ children }) => (
                    <h1 className="text-2xl font-bold text-white">
                      {children}
                    </h1>
                  ),
                  h2: ({ children }) => (
                    <h2 className="text-xl font-semibold text-white">
                      {children}
                    </h2>
                  ),
                  h3: ({ children }) => (
                    <h3 className="text-lg font-semibold text-white">
                      {children}
                    </h3>
                  ),
                  p: ({ children }) => (
                    <p className="leading-7">{children}</p>
                  ),
                  ul: ({ children }) => (
                    <ul className="ml-6 list-disc space-y-2">
                      {children}
                    </ul>
                  ),
                  ol: ({ children }) => (
                    <ol className="ml-6 list-decimal space-y-2">
                      {children}
                    </ol>
                  ),
                  li: ({ children }) => <li className="pl-1">{children}</li>,
                  strong: ({ children }) => (
                    <strong className="font-semibold text-white">
                      {children}
                    </strong>
                  ),
                  blockquote: ({ children }) => (
                    <blockquote className="border-l-4 border-blue-500 pl-4 italic text-slate-300">
                      {children}
                    </blockquote>
                  ),
                  table: ({ children }) => (
                    <div className="my-4 overflow-x-auto rounded-lg border border-slate-700">
                      <table className="w-full min-w-[500px] border-collapse text-left text-sm">
                        {children}
                      </table>
                    </div>
                  ),
                  thead: ({ children }) => (
                    <thead className="bg-slate-800 text-white">
                      {children}
                    </thead>
                  ),
                  th: ({ children }) => (
                    <th className="border-b border-slate-700 px-4 py-3 font-semibold">
                      {children}
                    </th>
                  ),
                  td: ({ children }) => (
                    <td className="border-b border-slate-700 px-4 py-3 align-top leading-6">
                      {children}
                    </td>
                  ),
                  a: ({ children, href }) => (
                    <a
                      href={href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-400 underline hover:text-blue-300"
                    >
                      {children}
                    </a>
                  ),
                  code: ({ children }) => (
                    <code className="rounded bg-slate-800 px-1.5 py-0.5 text-sm text-blue-200">
                      {children}
                    </code>
                  ),
                }}
              >
                {answer.answer}
              </ReactMarkdown>
            </article>

            <div className="mt-8 border-t border-slate-700 pt-5">
              <h3 className="text-lg font-semibold">Sources</h3>

              {answer.sources.length === 0 ? (
                <p className="mt-3 text-sm text-slate-400">
                  No source passages were retrieved.
                </p>
              ) : (
                <div className="mt-3 space-y-2">
                  {answer.sources.map((source, index) => (
                    <details
                      key={`${source.page_number}-${source.chunk_index}-${index}`}
                      className="group rounded-lg border border-slate-700 bg-slate-950"
                    >
                      <summary className="flex cursor-pointer list-none items-center justify-between gap-3 px-4 py-3 text-sm font-medium text-blue-400 hover:text-blue-300">
                        <span>
                          <span className="mr-2 inline-block">📄</span>
                          Page {source.page_number}
                        </span>
                        <span className="text-xs text-slate-400 group-open:hidden">
                          View passage +
                        </span>
                        <span className="hidden text-xs text-slate-400 group-open:inline">
                          Hide passage −
                        </span>
                      </summary>

                      <div className="border-t border-slate-800 px-4 py-3 text-sm leading-6 text-slate-300">
                        {source.text}
                      </div>
                    </details>
                  ))}
                </div>
              )}
            </div>
          </section>
        )}

        <footer className="mt-12 text-center text-sm text-slate-500">
          Powered by FastAPI · Ollama · FAISS · Next.js
        </footer>
      </div>
    </main>
  );
}
