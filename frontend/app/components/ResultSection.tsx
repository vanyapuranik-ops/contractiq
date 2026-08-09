
      
"use client"

import { useState } from "react"
import SummaryTab from "./SummaryTab"
import ReviewFindings from "./ReviewFindings"
import ChatAssistant from "./ChatAssistant"
import ClauseExplorer from "./ClauseExplorer"
import FinancialReview from "./FinancialReview"
import ContractTimeline from "./ContractTimeline"
import DownloadReport from "./DownloadReport"

interface ChunkStats {
  total_chunks: number
  avg_chunk_size: number
  min_chunk_size: number
  max_chunk_size: number
}

interface Summary {
  contract_type: string
  parties: string[]
  effective_date: string
  duration: string
  key_points: string[]
  financial_terms: string
  termination: string
  risks: string[]
  summary: string
}

interface RiskItem {
  id: string
  label: string
  severity: string
  clause: string
}

interface RiskResult {
  overall_risk: string
  high_risks: RiskItem[]
  medium_risks: RiskItem[]
  low_risks: RiskItem[]
  total_risks: number
  risk_score: number
}

interface Props {
  result: {
    file_name: string
    file_size: string
    page_count: number
    word_count: number
    extracted_text: string
    chunks: string[]
    chunk_stats: ChunkStats
    collection_name: string
    embeddings_stored: number
  }
  processingTime: number
}

function getConfidence(wordCount: number) {
  if (wordCount > 2000) return { label: "High", color: "text-green-700", bg: "bg-green-50 border-green-200" }
  if (wordCount > 800) return { label: "Medium", color: "text-yellow-700", bg: "bg-yellow-50 border-yellow-200" }
  return { label: "Low", color: "text-red-700", bg: "bg-red-50 border-red-200" }
}

function getReadingTime(wordCount: number) {
  return Math.ceil(wordCount / 200) + " min"
}

export default function ResultSection({ result, processingTime }: Props) {
  const [activeTab, setActiveTab] = useState<"summary" | "ask" | "risks" | "clauses" | "financials" | "timeline" | "raw">("summary")
  const [summary, setSummary] = useState<Summary | null>(null)
  const [summarizing, setSummarizing] = useState(false)
  const [summaryError, setSummaryError] = useState("")
  const [risks, setRisks] = useState<RiskResult | null>(null)
  const [detecting, setDetecting] = useState(false)
  const [riskError, setRiskError] = useState("")

  const confidence = getConfidence(result.word_count)
  const readingTime = getReadingTime(result.word_count)
  const contractName = result.file_name.replace(".pdf", "").replace(/_/g, " ")

  const handleSummarize = async () => {
    setSummarizing(true)
    setSummaryError("")
    setSummary(null)
    try {
      const response = await fetch("http://localhost:8000/summarize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ extracted_text: result.extracted_text })
      })
      if (!response.ok) throw new Error("Failed")
      const data = await response.json()
      setSummary(data)
    } catch {
      setSummaryError("Could not generate summary. Please try again.")
    } finally {
      setSummarizing(false)
    }
  }

  const handleDetectRisks = async () => {
    setDetecting(true)
    setRiskError("")
    setRisks(null)
    try {
      const response = await fetch("http://localhost:8000/detect-risks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ extracted_text: result.extracted_text })
      })
      if (!response.ok) throw new Error("Failed")
      const data = await response.json()
      setRisks(data)
    } catch {
      setRiskError("Could not detect risks. Please try again.")
    } finally {
      setDetecting(false)
    }
  }

  return (
    <div className="w-full max-w-4xl mx-auto mt-8 space-y-5 px-4">

      <div className="bg-white border border-gray-100 rounded-2xl p-6 shadow-sm">
        <div className="flex items-start justify-between mb-5">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-50 rounded-xl flex items-center justify-center flex-shrink-0">
              <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900 leading-tight">{contractName}</h2>
              <p className="text-sm text-gray-400 mt-0.5">{result.file_size} • PDF Document</p>
            </div>
          </div>
          <span className="text-xs font-medium bg-blue-50 text-blue-600 border border-blue-100 px-3 py-1.5 rounded-full">
            Under Review
          </span>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[
            { label: "Pages", value: result.page_count.toString() },
            { label: "Est. Reading Time", value: readingTime },
            { label: "Processing Time", value: processingTime + "s" },
            { label: "Review Confidence", value: confidence.label, extra: confidence },
          ].map((item) => (
            <div key={item.label} className="bg-gray-50 rounded-xl p-4 border border-gray-100">
              <p className="text-xs text-gray-400 font-medium uppercase tracking-wide mb-1">{item.label}</p>
              {item.extra ? (
                <span className={"text-sm font-semibold px-2 py-0.5 rounded-md border " + item.extra.bg + " " + item.extra.color}>
                  {item.value}
                </span>
              ) : (
                <p className="text-lg font-bold text-gray-800">{item.value}</p>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white border border-gray-100 rounded-2xl overflow-hidden shadow-sm">
        <div className="flex border-b border-gray-100 px-2 pt-2 overflow-x-auto">
          {([
            { key: "summary", label: "Executive Review" },
            { key: "ask", label: "Ask AI" },
            { key: "risks", label: "Review Findings" },
            { key: "clauses", label: "Clause Explorer" },
            { key: "financials", label: "Financial Review" },
            { key: "timeline", label: "Timeline" },
            { key: "raw", label: "Raw Text" },
          ] as const).map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={"px-4 py-3 text-sm font-medium rounded-t-xl transition-all whitespace-nowrap " +
                (activeTab === tab.key
                  ? "text-blue-600 bg-blue-50 border-b-2 border-blue-500"
                  : "text-gray-500 hover:text-gray-700 hover:bg-gray-50")}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div className="p-6">

          {activeTab === "summary" && (
            <div className="space-y-5">
              {!summary && !summarizing && (
                <div className="text-center py-10">
                  <div className="w-12 h-12 bg-blue-50 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <svg className="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <p className="text-gray-600 font-medium mb-1">Generate Executive Review</p>
                  <p className="text-gray-400 text-sm mb-6">Get a plain English breakdown of all key contract details</p>
                  <button onClick={handleSummarize} className="bg-blue-600 text-white px-8 py-3 rounded-xl text-sm font-semibold hover:bg-blue-700 transition shadow-sm">
                    Generate Review
                  </button>
                </div>
              )}
              {summarizing && (
                <div className="text-center py-10">
                  <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                  <p className="text-gray-500 text-sm">Analyzing contract...</p>
                </div>
              )}
              {summaryError && (
                <div className="p-4 bg-red-50 border border-red-100 rounded-xl text-red-600 text-sm">{summaryError}</div>
              )}
              {summary && <SummaryTab summary={summary} onRegenerate={handleSummarize} />}
            </div>
          )}

          {activeTab === "ask" && (
            <ChatAssistant collectionName={result.collection_name} />
          )}

          {activeTab === "risks" && (
            <div className="space-y-5">
              {!risks && !detecting && (
                <div className="text-center py-10">
                  <div className="w-12 h-12 bg-gray-50 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                  </div>
                  <p className="text-gray-600 font-medium mb-1">Run Contract Review</p>
                  <p className="text-gray-400 text-sm mb-6">Identify clauses that may require attention before signing</p>
                  <button onClick={handleDetectRisks} className="bg-gray-900 text-white px-8 py-3 rounded-xl text-sm font-semibold hover:bg-gray-800 transition shadow-sm">
                    Start Review
                  </button>
                </div>
              )}
              {detecting && (
                <div className="text-center py-10">
                  <div className="w-8 h-8 border-2 border-gray-400 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                  <p className="text-gray-500 text-sm">Reviewing contract clauses...</p>
                </div>
              )}
              {riskError && (
                <div className="p-4 bg-red-50 border border-red-100 rounded-xl text-red-600 text-sm">{riskError}</div>
              )}
              {risks && <ReviewFindings risks={risks} onRescan={handleDetectRisks} />}
            </div>
          )}

          {activeTab === "clauses" && (
            <ClauseExplorer chunks={result.chunks} />
          )}

          {activeTab === "financials" && (
            <FinancialReview extractedText={result.extracted_text} />
          )}

          {activeTab === "timeline" && (
            <ContractTimeline extractedText={result.extracted_text} />
          )}

          {activeTab === "raw" && (
            <textarea
              readOnly
              value={result.extracted_text}
              className="w-full h-80 text-sm text-gray-500 bg-gray-50 border border-gray-100 rounded-xl p-4 resize-none focus:outline-none font-mono"
            />
          )}
        </div>
      </div>

      <div className="flex flex-col items-center gap-4 pb-8">
        <DownloadReport
          extractedText={result.extracted_text}
          fileName={result.file_name}
          fileSize={result.file_size}
          pageCount={result.page_count}
          wordCount={result.word_count}
          collectionName={result.collection_name}
        />
        <p className="text-center text-xs text-gray-300">
          ContractIQ is not a law firm and does not provide legal advice.
        </p>
      </div>

    </div>
  );
}