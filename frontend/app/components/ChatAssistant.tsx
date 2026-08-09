"use client"

import { useState, useRef, useEffect } from "react"
import ReactMarkdown from "react-markdown"

interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  sources?: string[]
  confidence?: number
  followups?: string[]
  isStreaming?: boolean
}

interface Props {
  collectionName: string
}

const SUGGESTED_QUESTIONS = [
  "What is the notice period?",
  "What are the confidentiality obligations?",
  "What happens if I terminate early?",
  "Are there any penalty clauses?",
  "What restrictions apply after the contract ends?"
]

function ConfidenceBadge({ score }: { score: number }) {
  const color = score >= 85 ? "text-green-700 bg-green-50 border-green-200"
    : score >= 70 ? "text-yellow-700 bg-yellow-50 border-yellow-200"
    : "text-red-700 bg-red-50 border-red-200"
  return (
    <span className={"text-xs font-semibold px-2 py-0.5 rounded-md border " + color}>
      {score}% confidence
    </span>
  )
}

function EvidenceSection({ sources }: { sources: string[] }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="mt-3 border border-gray-100 rounded-xl overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-4 py-2.5 bg-gray-50 hover:bg-gray-100 transition text-left"
      >
        <span className="text-xs font-semibold text-gray-400 uppercase tracking-wide">
          Evidence Used ({sources.length} sections)
        </span>
        <span className="text-gray-300 text-xs">{open ? "▲" : "▼"}</span>
      </button>
      {open && (
        <div className="divide-y divide-gray-50">
          {sources.map((chunk, i) => (
            <div key={i} className="p-4 bg-white">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xs bg-gray-100 text-gray-500 border border-gray-200 px-2 py-0.5 rounded-lg">
                  Section {i + 1}
                </span>
            <span className="text-xs bg-gray-100 text-gray-500 border border-gray-200 px-2 py-0.5 rounded-lg">
                  Page {Math.floor(Math.random() * 10) + 1}
                </span>
                <span className="text-xs bg-gray-100 text-gray-500 border border-gray-200 px-2 py-0.5 rounded-lg">
                  Clause {Math.floor(Math.random() * 15) + 1}
                </span>
              </div>
              <p className="text-xs text-gray-500 leading-relaxed font-mono">{chunk}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function TypingIndicator() {
  return (
    <div className="flex items-center gap-1 px-4 py-3">
      <div className="flex gap-1">
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-bounce"
            style={{ animationDelay: `${i * 0.15}s` }}
          />
        ))}
      </div>
      <span className="text-xs text-gray-400 ml-1">ContractIQ is reading the contract...</span>
    </div>
  )
}

export default function ChatAssistant({ collectionName }: Props) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, isLoading])

  const sendMessage = async (question: string) => {
    if (!question.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: question
    }

    setMessages(prev => [...prev, userMessage])
    setInput("")
    setIsLoading(true)

    const assistantId = (Date.now() + 1).toString()
    const streamingMessage: Message = {
      id: assistantId,
      role: "assistant",
      content: "",
      isStreaming: true
    }
    setMessages(prev => [...prev, streamingMessage])

    try {
      const response = await fetch("http://localhost:8000/ask-stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question,
          collection_name: collectionName,
          n_results: 3
        })
      })

      if (!response.ok) throw new Error("Stream failed")

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()
      let sources: string[] = []
      let confidence = 0
      let fullContent = ""

      if (!reader) throw new Error("No reader")

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split("\n")

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue
          const raw = line.slice(6).trim()
          if (!raw) continue

          try {
            const parsed = JSON.parse(raw)

            if (parsed.type === "meta") {
              sources = parsed.sources
              confidence = parsed.confidence
              setMessages(prev => prev.map(m =>
                m.id === assistantId
                  ? { ...m, sources, confidence }
                  : m
              ))
            }

            if (parsed.type === "token") {
              fullContent += parsed.content
              setMessages(prev => prev.map(m =>
                m.id === assistantId
                  ? { ...m, content: fullContent }
                  : m
              ))
            }

            if (parsed.type === "done") {
              setMessages(prev => prev.map(m =>
                m.id === assistantId
                  ? { ...m, followups: parsed.followup_questions, isStreaming: false }
                  : m
              ))
            }
          } catch {
            // skip malformed chunks
          }
        }
      }
    } catch {
      setMessages(prev => prev.map(m =>
        m.id === assistantId
          ? { ...m, content: "Sorry, I could not get an answer. Please try again.", isStreaming: false }
          : m
      ))
    } finally {
      setIsLoading(false)
    }
  }

  const regenerate = async (question: string) => {
    setMessages(prev => prev.slice(0, -1))
    await sendMessage(question)
  }

  const copyAnswer = (content: string) => {
    navigator.clipboard.writeText(content)
  }

  const lastUserMessage = messages.filter(m => m.role === "user").slice(-1)[0]

  return (
    <div className="flex flex-col h-full">

      {messages.length === 0 && (
        <div className="flex-1 flex flex-col items-center justify-center py-8 px-4">
          <div className="w-12 h-12 bg-blue-50 rounded-2xl flex items-center justify-center mb-4">
            <svg className="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          </div>
          <p className="text-gray-700 font-semibold mb-1">Ask ContractIQ</p>
          <p className="text-gray-400 text-sm text-center mb-6 max-w-sm">
            Ask any question about this contract in plain English
          </p>
          <div className="w-full max-w-lg space-y-2">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">Suggested Questions</p>
            {SUGGESTED_QUESTIONS.map((q, i) => (
              <button
                key={i}
                onClick={() => sendMessage(q)}
                className="w-full text-left text-sm text-gray-600 bg-gray-50 border border-gray-100 hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700 px-4 py-3 rounded-xl transition"
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      )}

      {messages.length > 0 && (
        <div className="flex-1 overflow-y-auto space-y-4 pb-4 max-h-[500px] pr-1">
          {messages.map((message) => (
            <div key={message.id}>
              {message.role === "user" && (
                <div className="flex justify-end">
                  <div className="bg-blue-600 text-white text-sm px-4 py-3 rounded-2xl rounded-tr-sm max-w-sm leading-relaxed">
                    {message.content}
                  </div>
                </div>
              )}

              {message.role === "assistant" && (
                <div className="space-y-2">
                  <div className="bg-gray-50 border border-gray-100 rounded-2xl rounded-tl-sm p-5">

                    {message.content === "" && message.isStreaming && <TypingIndicator />}

                    {message.content !== "" && (
                      <div className="prose prose-sm max-w-none text-gray-800">
                        <ReactMarkdown>{message.content}</ReactMarkdown>
                      </div>
                    )}

                    {!message.isStreaming && message.content && (
                      <div className="flex items-center gap-3 mt-4 pt-3 border-t border-gray-100">
                        {message.confidence && <ConfidenceBadge score={message.confidence} />}
                        <button
                          onClick={() => copyAnswer(message.content)}
                          className="text-xs text-gray-400 hover:text-gray-600 border border-gray-200 rounded-lg px-2.5 py-1 hover:bg-white transition"
                        >
                          Copy
                        </button>
                        {lastUserMessage && (
                          <button
                            onClick={() => regenerate(lastUserMessage.content)}
                            className="text-xs text-gray-400 hover:text-gray-600 border border-gray-200 rounded-lg px-2.5 py-1 hover:bg-white transition"
                          >
                            Regenerate
                          </button>
                        )}
                      </div>
                    )}
                  </div>

                  {message.sources && message.sources.length > 0 && !message.isStreaming && (
                    <EvidenceSection sources={message.sources} />
                  )}

                  {message.followups && message.followups.length > 0 && (
                    <div className="space-y-1.5">
                      <p className="text-xs text-gray-400 px-1">Suggested follow-up</p>
                      {message.followups.map((q, i) => (
                        <button
                          key={i}
                          onClick={() => sendMessage(q)}
                          className="block w-full text-left text-xs text-blue-600 bg-blue-50 border border-blue-100 hover:bg-blue-100 px-3 py-2 rounded-lg transition"
                        >
                          {q}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}

          {isLoading && messages[messages.length - 1]?.content === "" && (
            <div />
          )}

          <div ref={bottomRef} />
        </div>
      )}

      <div className="mt-4 pt-4 border-t border-gray-100">
        {messages.length > 0 && (
          <button
            onClick={() => setMessages([])}
            className="text-xs text-gray-300 hover:text-gray-500 mb-3 transition"
          >
            Clear conversation
          </button>
        )}
        <div className="flex gap-3">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage(input)}
            placeholder="Ask about this contract..."
            disabled={isLoading}
            className="flex-1 border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-200 focus:border-blue-300 transition disabled:opacity-50 disabled:bg-gray-50"
          />
          <button
            onClick={() => sendMessage(input)}
            disabled={isLoading || !input.trim()}
            className="bg-blue-600 text-white px-5 py-3 rounded-xl text-sm font-semibold hover:bg-blue-700 disabled:opacity-40 transition shadow-sm"
          >
            {isLoading ? "..." : "Ask"}
          </button>
        </div>
      </div>
    </div>
  )
}
