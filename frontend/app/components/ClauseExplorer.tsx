"use client"

import { useState } from "react"

interface Clause {
  id: number
  title: string
  category: string
  risk_level: string
  plain_english: string
  risk_assessment: string
  related_categories: string[]
  original_text: string
  page_number: number
  clause_number: string
}

interface Props {
  chunks: string[]
}

const CATEGORIES = [
  "All", "Termination", "Payment", "Confidentiality", "Liability",
  "Intellectual Property", "Governing Law", "Dispute Resolution",
  "Renewal", "Indemnification", "Non-compete", "Force Majeure",
  "Notices", "General"
]

const RISK_LEVELS = ["All", "Low", "Medium", "High"]

const RISK_STYLES: Record<string, string> = {
  High: "bg-red-50 text-red-700 border-red-200",
  Medium: "bg-yellow-50 text-yellow-700 border-yellow-200",
  Low: "bg-green-50 text-green-700 border-green-200"
}

const CATEGORY_STYLES: Record<string, string> = {
  Termination: "bg-red-50 text-red-600 border-red-100",
  Payment: "bg-green-50 text-green-600 border-green-100",
  Confidentiality: "bg-blue-50 text-blue-600 border-blue-100",
  Liability: "bg-orange-50 text-orange-600 border-orange-100",
  "Intellectual Property": "bg-purple-50 text-purple-600 border-purple-100",
  "Governing Law": "bg-gray-50 text-gray-600 border-gray-200",
  "Dispute Resolution": "bg-yellow-50 text-yellow-600 border-yellow-100",
  Renewal: "bg-teal-50 text-teal-600 border-teal-100",
  Indemnification: "bg-rose-50 text-rose-600 border-rose-100",
  "Non-compete": "bg-amber-50 text-amber-600 border-amber-100",
  "Force Majeure": "bg-sky-50 text-sky-600 border-sky-100",
  Notices: "bg-indigo-50 text-indigo-600 border-indigo-100",
  General: "bg-gray-50 text-gray-500 border-gray-100"
}

const PAGE_SIZE = 8

function ClauseCard({ clause, onClick }: { clause: Clause; onClick: () => void }) {
  return (
    <div
      onClick={onClick}
      className="bg-white border border-gray-100 rounded-xl p-4 hover:border-blue-200 hover:shadow-sm cursor-pointer transition-all group"
    >
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex items-center gap-2 flex-wrap">
          <span className={"text-xs font-semibold px-2 py-0.5 rounded-md border " + (CATEGORY_STYLES[clause.category] || CATEGORY_STYLES.General)}>
            {clause.category}
          </span>
          <span className={"text-xs font-semibold px-2 py-0.5 rounded-md border " + (RISK_STYLES[clause.risk_level] || RISK_STYLES.Low)}>
            {clause.risk_level} Risk
          </span>
        </div>
        <div className="flex items-center gap-1 flex-shrink-0">
          <span className="text-xs text-gray-300">P.{clause.page_number}</span>
          <span className="text-xs text-gray-300">|</span>
          <span className="text-xs text-gray-300">{clause.clause_number}</span>
        </div>
      </div>
      <p className="text-sm font-semibold text-gray-900 mb-1 group-hover:text-blue-700 transition">{clause.title}</p>
      <p className="text-xs text-gray-500 leading-relaxed line-clamp-2">{clause.plain_english}</p>
    </div>
  )
}

function ClauseDetail({ clause, onClose }: { clause: Clause; onClose: () => void }) {
  const [showOriginal, setShowOriginal] = useState(false)

  return (
    <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-xl max-w-2xl w-full max-h-[85vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-gray-100 px-6 py-4 flex items-center justify-between rounded-t-2xl">
          <div>
            <p className="text-xs text-gray-400 uppercase tracking-wide font-semibold mb-1">Clause Detail</p>
            <h3 className="text-base font-bold text-gray-900">{clause.title}</h3>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-gray-100 text-gray-400 hover:text-gray-600 transition"
          >
            x
          </button>
        </div>

        <div className="p-6 space-y-4">

          <div className="flex items-center gap-2 flex-wrap">
            <span className={"text-xs font-semibold px-2 py-1 rounded-md border " + (CATEGORY_STYLES[clause.category] || CATEGORY_STYLES.General)}>
              {clause.category}
            </span>
            <span className={"text-xs font-semibold px-2 py-1 rounded-md border " + (RISK_STYLES[clause.risk_level] || RISK_STYLES.Low)}>
              {clause.risk_level} Risk
            </span>
            <span className="text-xs bg-gray-100 text-gray-500 border border-gray-200 px-2 py-1 rounded-md">
              Page {clause.page_number}
            </span>
            <span className="text-xs bg-gray-100 text-gray-500 border border-gray-200 px-2 py-1 rounded-md">
              Clause {clause.clause_number}
            </span>
          </div>

          <div className="bg-blue-50 border border-blue-100 rounded-xl p-4">
            <p className="text-xs font-semibold text-blue-400 uppercase tracking-wide mb-2">Plain English Explanation</p>
            <p className="text-sm text-gray-800 leading-relaxed">{clause.plain_english}</p>
          </div>

          <div className="bg-gray-50 border border-gray-100 rounded-xl p-4">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Risk Assessment</p>
            <p className="text-sm text-gray-700 leading-relaxed">{clause.risk_assessment}</p>
          </div>

          {clause.related_categories.length > 0 && (
            <div className="bg-gray-50 border border-gray-100 rounded-xl p-4">
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">Related Clauses</p>
              <div className="flex flex-wrap gap-2">
                {clause.related_categories.map((cat, i) => (
                  <span key={i} className={"text-xs font-medium px-2 py-1 rounded-md border " + (CATEGORY_STYLES[cat] || CATEGORY_STYLES.General)}>
                    {cat}
                  </span>
                ))}
              </div>
            </div>
          )}

          <div className="border border-gray-100 rounded-xl overflow-hidden">
            <button
              onClick={() => setShowOriginal(!showOriginal)}
              className="w-full flex items-center justify-between px-4 py-3 bg-gray-50 hover:bg-gray-100 transition text-left"
            >
              <span className="text-xs font-semibold text-gray-400 uppercase tracking-wide">Original Legal Text</span>
              <span className="text-gray-300 text-xs">{showOriginal ? "Hide" : "Show"}</span>
            </button>
            {showOriginal && (
              <div className="p-4 bg-white">
                <p className="text-xs text-gray-600 leading-relaxed font-mono whitespace-pre-wrap">{clause.original_text}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default function ClauseExplorer({ chunks }: Props) {
  const [clauses, setClauses] = useState<Clause[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [search, setSearch] = useState("")
  const [categoryFilter, setCategoryFilter] = useState("All")
  const [riskFilter, setRiskFilter] = useState("All")
  const [selectedClause, setSelectedClause] = useState<Clause | null>(null)
  const [page, setPage] = useState(1)

  const handleExtract = async () => {
    setLoading(true)
    setError("")
    try {
      const response = await fetch("http://localhost:8000/extract-clauses", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ chunks: chunks.slice(0, 20) })
      })
      if (!response.ok) throw new Error("Failed")
      const data = await response.json()
      setClauses(data.clauses)
    } catch {
      setError("Could not extract clauses. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  const filtered = clauses.filter(c => {
    const matchSearch = search === "" ||
      c.title.toLowerCase().includes(search.toLowerCase()) ||
      c.plain_english.toLowerCase().includes(search.toLowerCase())
    const matchCategory = categoryFilter === "All" || c.category === categoryFilter
    const matchRisk = riskFilter === "All" || c.risk_level === riskFilter
    return matchSearch && matchCategory && matchRisk
  })

  const totalPages = Math.ceil(filtered.length / PAGE_SIZE)
  const paginated = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE)

  const riskCounts = {
    High: clauses.filter(c => c.risk_level === "High").length,
    Medium: clauses.filter(c => c.risk_level === "Medium").length,
    Low: clauses.filter(c => c.risk_level === "Low").length
  }

  return (
    <div className="space-y-5">

      {clauses.length === 0 && !loading && (
        <div className="text-center py-10">
          <div className="w-12 h-12 bg-blue-50 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <svg className="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 6h16M4 10h16M4 14h10M4 18h6" />
            </svg>
          </div>
          <p className="text-gray-600 font-medium mb-1">Explore Contract Clauses</p>
          <p className="text-gray-400 text-sm mb-6">Automatically classify and analyze every clause in this contract</p>
          <button
            onClick={handleExtract}
            className="bg-blue-600 text-white px-8 py-3 rounded-xl text-sm font-semibold hover:bg-blue-700 transition shadow-sm"
          >
            Extract Clauses
          </button>
        </div>
      )}

      {loading && (
        <div className="text-center py-10">
          <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-500 text-sm">Classifying contract clauses...</p>
          <p className="text-gray-400 text-xs mt-1">This may take 30-60 seconds</p>
        </div>
      )}

      {error && (
        <div className="p-4 bg-red-50 border border-red-100 rounded-xl text-red-600 text-sm">{error}</div>
      )}

      {clauses.length > 0 && (
        <>
          <div className="grid grid-cols-3 gap-3">
            {[
              { label: "High Risk", value: riskCounts.High, color: "text-red-700", bg: "bg-red-50 border-red-100" },
              { label: "Medium Risk", value: riskCounts.Medium, color: "text-yellow-700", bg: "bg-yellow-50 border-yellow-100" },
              { label: "Low Risk", value: riskCounts.Low, color: "text-green-700", bg: "bg-green-50 border-green-100" },
            ].map(item => (
              <div key={item.label} className={"border rounded-xl p-4 text-center " + item.bg}>
                <p className="text-xs text-gray-400 font-medium mb-1">{item.label}</p>
                <p className={"text-2xl font-bold " + item.color}>{item.value}</p>
              </div>
            ))}
          </div>

          <div className="flex flex-col md:flex-row gap-3">
            <div className="flex-1 relative">
              <svg className="w-4 h-4 text-gray-300 absolute left-3 top-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                type="text"
                value={search}
                onChange={(e) => { setSearch(e.target.value); setPage(1) }}
                placeholder="Search clauses..."
                className="w-full pl-9 pr-4 py-2.5 text-sm border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-200 focus:border-blue-300 transition"
              />
            </div>
            <select
              value={categoryFilter}
              onChange={(e) => { setCategoryFilter(e.target.value); setPage(1) }}
              className="text-sm border border-gray-200 rounded-xl px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-200 bg-white text-gray-600"
            >
              {CATEGORIES.map(c => <option key={c}>{c}</option>)}
            </select>
            <select
              value={riskFilter}
              onChange={(e) => { setRiskFilter(e.target.value); setPage(1) }}
              className="text-sm border border-gray-200 rounded-xl px-3 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-200 bg-white text-gray-600"
            >
              {RISK_LEVELS.map(r => <option key={r}>{r}</option>)}
            </select>
          </div>

          <div className="flex items-center justify-between">
            <p className="text-xs text-gray-400">
              Showing {paginated.length} of {filtered.length} clauses
            </p>
            <button
              onClick={() => { setClauses([]); setSearch(""); setCategoryFilter("All"); setRiskFilter("All"); setPage(1) }}
              className="text-xs text-gray-400 hover:text-gray-600 border border-gray-200 rounded-lg px-3 py-1.5 hover:bg-gray-50 transition"
            >
              Re-extract
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {paginated.map(clause => (
              <ClauseCard key={clause.id} clause={clause} onClick={() => setSelectedClause(clause)} />
            ))}
          </div>

          {filtered.length === 0 && (
            <div className="text-center py-8 text-gray-400 text-sm">
              No clauses match your filters.
            </div>
          )}

          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 pt-2">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="text-xs border border-gray-200 rounded-lg px-3 py-1.5 hover:bg-gray-50 disabled:opacity-40 transition"
              >
                Previous
              </button>
              <span className="text-xs text-gray-400">Page {page} of {totalPages}</span>
              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="text-xs border border-gray-200 rounded-lg px-3 py-1.5 hover:bg-gray-50 disabled:opacity-40 transition"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}

      {selectedClause && (
        <ClauseDetail clause={selectedClause} onClose={() => setSelectedClause(null)} />
      )}
    </div>
  )
}
