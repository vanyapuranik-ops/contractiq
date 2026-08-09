"use client"

import { useState } from "react"

interface TimelineEvent {
  title: string
  date_value: string
  date_type: string
  category: string
  importance: string
  description: string
  evidence: string
  related_clause: string
  page_hint: string
  confidence: string
}

interface TimelineData {
  events: TimelineEvent[]
  summary: string
  missing_dates: string[]
  total_events: number
  has_exact_dates: boolean
  has_relative_dates: boolean
}

interface Props {
  extractedText: string
}

const CATEGORY_STYLES: Record<string, { bg: string; border: string; dot: string; badge: string }> = {
  "Contract Date": { bg: "bg-blue-50", border: "border-blue-200", dot: "bg-blue-500", badge: "bg-blue-100 text-blue-700 border-blue-200" },
  Payment: { bg: "bg-green-50", border: "border-green-200", dot: "bg-green-500", badge: "bg-green-100 text-green-700 border-green-200" },
  Renewal: { bg: "bg-purple-50", border: "border-purple-200", dot: "bg-purple-500", badge: "bg-purple-100 text-purple-700 border-purple-200" },
  Termination: { bg: "bg-red-50", border: "border-red-200", dot: "bg-red-500", badge: "bg-red-100 text-red-700 border-red-200" },
  Notice: { bg: "bg-yellow-50", border: "border-yellow-200", dot: "bg-yellow-500", badge: "bg-yellow-100 text-yellow-700 border-yellow-200" },
  Milestone: { bg: "bg-indigo-50", border: "border-indigo-200", dot: "bg-indigo-500", badge: "bg-indigo-100 text-indigo-700 border-indigo-200" },
  Delivery: { bg: "bg-orange-50", border: "border-orange-200", dot: "bg-orange-500", badge: "bg-orange-100 text-orange-700 border-orange-200" },
  Confidentiality: { bg: "bg-slate-50", border: "border-slate-200", dot: "bg-slate-500", badge: "bg-slate-100 text-slate-700 border-slate-200" },
  "Non-compete": { bg: "bg-rose-50", border: "border-rose-200", dot: "bg-rose-500", badge: "bg-rose-100 text-rose-700 border-rose-200" },
  "Grace Period": { bg: "bg-teal-50", border: "border-teal-200", dot: "bg-teal-500", badge: "bg-teal-100 text-teal-700 border-teal-200" },
  Other: { bg: "bg-gray-50", border: "border-gray-200", dot: "bg-gray-400", badge: "bg-gray-100 text-gray-600 border-gray-200" }
}

const IMPORTANCE_STYLES: Record<string, string> = {
  High: "bg-red-50 text-red-700 border-red-200",
  Medium: "bg-yellow-50 text-yellow-700 border-yellow-200",
  Low: "bg-green-50 text-green-700 border-green-200"
}

const DATE_TYPE_LABELS: Record<string, string> = {
  exact: "Exact Date",
  relative: "Relative Date",
  duration: "Duration",
  recurring: "Recurring",
  conditional: "Conditional"
}

const DATE_TYPE_STYLES: Record<string, string> = {
  exact: "bg-blue-50 text-blue-600 border-blue-200",
  relative: "bg-yellow-50 text-yellow-600 border-yellow-200",
  duration: "bg-purple-50 text-purple-600 border-purple-200",
  recurring: "bg-green-50 text-green-600 border-green-200",
  conditional: "bg-orange-50 text-orange-600 border-orange-200"
}

const CATEGORY_FILTERS = ["All Events", "Contract Date", "Payment", "Renewal", "Termination", "Notice", "Milestone", "Delivery", "Confidentiality", "Non-compete", "Grace Period", "Other"]
const IMPORTANCE_FILTERS = ["All", "High", "Medium", "Low"]

function TimelineItem({ event, isLast }: { event: TimelineEvent; isLast: boolean }) {
  const [expanded, setExpanded] = useState(false)
  const style = CATEGORY_STYLES[event.category] || CATEGORY_STYLES.Other
  const dateTypeStyle = DATE_TYPE_STYLES[event.date_type] || DATE_TYPE_STYLES.relative
  const dateTypeLabel = DATE_TYPE_LABELS[event.date_type] || event.date_type

  return (
    <div className="flex gap-4">
      <div className="flex flex-col items-center flex-shrink-0">
        <div className={"w-3 h-3 rounded-full mt-5 flex-shrink-0 ring-4 ring-white shadow-sm " + style.dot}></div>
        {!isLast && <div className="w-px bg-gray-150 flex-1 mt-1" style={{backgroundColor: "#e8eaed", minHeight: "2rem"}}></div>}
      </div>
      <div className={"border rounded-xl overflow-hidden mb-4 flex-1 transition-shadow hover:shadow-sm " + style.border}>
        <div className={"p-4 cursor-pointer " + style.bg} onClick={() => setExpanded(!expanded)}>
          <div className="flex items-start justify-between gap-3">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap mb-2">
                <span className={"text-xs font-semibold px-2 py-0.5 rounded-md border " + (IMPORTANCE_STYLES[event.importance] || IMPORTANCE_STYLES.Low)}>
                  {event.importance}
                </span>
                <span className={"text-xs font-semibold px-2 py-0.5 rounded-md border " + style.badge}>
                  {event.category}
                </span>
                <span className={"text-xs font-medium px-2 py-0.5 rounded-md border " + dateTypeStyle}>
                  {dateTypeLabel}
                </span>
              </div>
              <p className="text-sm font-semibold text-gray-900 mb-1">{event.title}</p>
              <p className="text-sm font-bold text-gray-700 mb-1">{event.date_value}</p>
              <p className="text-xs text-gray-500 leading-relaxed line-clamp-2">{event.description}</p>
            </div>
            <div className="flex flex-col items-end gap-1 flex-shrink-0">
              {event.page_hint && (
                <span className="text-xs bg-white border border-gray-200 text-gray-400 px-2 py-0.5 rounded-lg whitespace-nowrap">
                  {event.page_hint}
                </span>
              )}
              <span className="text-gray-300 text-xs">{expanded ? "▲" : "▼"}</span>
            </div>
          </div>
        </div>
        {expanded && (
          <div className="bg-white border-t border-gray-100 p-4 space-y-4">
            <div>
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">Plain English Explanation</p>
              <p className="text-sm text-gray-700 leading-relaxed">{event.description}</p>
            </div>
            {event.evidence && (
              <div className="bg-gray-50 border border-gray-100 rounded-xl p-3">
                <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Contract Evidence</p>
                <p className="text-xs text-gray-600 leading-relaxed font-mono italic">{event.evidence}</p>
              </div>
            )}
            <div className="flex items-center gap-2 flex-wrap">
              {event.related_clause && (
                <span className="text-xs bg-blue-50 text-blue-600 border border-blue-200 px-2 py-1 rounded-lg font-medium">
                  {event.related_clause}
                </span>
              )}
              {event.page_hint && (
                <span className="text-xs bg-gray-100 text-gray-500 border border-gray-200 px-2 py-1 rounded-lg">
                  {event.page_hint}
                </span>
              )}
              {event.confidence && (
                <span className="text-xs bg-gray-50 text-gray-400 border border-gray-200 px-2 py-1 rounded-lg">
                  Confidence: {event.confidence}
                </span>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default function ContractTimeline({ extractedText }: Props) {
  const [data, setData] = useState<TimelineData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [categoryFilter, setCategoryFilter] = useState("All Events")
  const [importanceFilter, setImportanceFilter] = useState("All")

  const handleExtract = async () => {
    setLoading(true)
    setError("")
    setData(null)
    try {
      const response = await fetch("http://localhost:8000/extract-timeline", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ extracted_text: extractedText })
      })
      if (!response.ok) throw new Error("Request failed")
      const result = await response.json()
      setData(result)
    } catch {
      setError("Could not extract timeline data. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  const filtered = data ? data.events.filter(e => {
    const matchCat = categoryFilter === "All Events" || e.category === categoryFilter
    const matchImp = importanceFilter === "All" || e.importance === importanceFilter
    return matchCat && matchImp
  }) : []

  const highCount = data ? data.events.filter(e => e.importance === "High").length : 0
  const renewalCount = data ? data.events.filter(e => e.category === "Renewal").length : 0
  const exactCount = data ? data.events.filter(e => e.date_type === "exact").length : 0

  return (
    <div className="space-y-5">

      {!data && !loading && (
        <div className="text-center py-12">
          <div className="w-14 h-14 bg-indigo-50 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <svg className="w-7 h-7 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          <p className="text-gray-700 font-semibold mb-1">Contract Timeline</p>
          <p className="text-gray-400 text-sm mb-2 max-w-sm mx-auto">
            Extract and visualize every date, deadline, and time obligation from this contract
          </p>
          <p className="text-xs text-gray-300 mb-6">Powered by contract-aware AI. Only real data from your document is shown.</p>
          <button onClick={handleExtract} className="bg-indigo-600 text-white px-8 py-3 rounded-xl text-sm font-semibold hover:bg-indigo-700 transition shadow-sm">
            Extract Timeline
          </button>
        </div>
      )}

      {loading && (
        <div className="text-center py-12">
          <div className="w-10 h-10 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 font-medium text-sm">Analyzing contract dates and deadlines...</p>
          <p className="text-gray-400 text-xs mt-1">This may take 15-30 seconds</p>
        </div>
      )}

      {error && (
        <div className="p-4 bg-red-50 border border-red-100 rounded-xl text-red-600 text-sm">{error}</div>
      )}

      {data && (
        <>
          <div className="bg-indigo-50 border border-indigo-100 rounded-xl p-5">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <p className="text-xs font-semibold text-indigo-400 uppercase tracking-wide mb-1">Timeline Summary</p>
                <p className="text-sm text-gray-800 leading-relaxed">{data.summary}</p>
              </div>
              <button onClick={() => { setData(null); setCategoryFilter("All Events"); setImportanceFilter("All") }}
                className="text-xs text-gray-400 hover:text-gray-600 border border-gray-200 rounded-lg px-3 py-1.5 hover:bg-white transition flex-shrink-0 bg-white">
                Re-extract
              </button>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {[
              { label: "Total Events", value: data.total_events, color: "text-indigo-700", bg: "bg-indigo-50 border-indigo-100" },
              { label: "Critical Dates", value: highCount, color: "text-red-700", bg: "bg-red-50 border-red-100" },
              { label: "Renewal Events", value: renewalCount, color: "text-purple-700", bg: "bg-purple-50 border-purple-100" },
              { label: "Exact Dates", value: exactCount, color: "text-blue-700", bg: "bg-blue-50 border-blue-100" },
            ].map(item => (
              <div key={item.label} className={"border rounded-xl p-4 text-center " + item.bg}>
                <p className="text-xs text-gray-400 font-medium mb-1">{item.label}</p>
                <p className={"text-2xl font-bold " + item.color}>{item.value}</p>
              </div>
            ))}
          </div>

          {data.missing_dates && data.missing_dates.length > 0 && (
            <div className="bg-yellow-50 border border-yellow-100 rounded-xl p-4">
              <p className="text-xs font-semibold text-yellow-600 uppercase tracking-wide mb-2">Dates Not Found in Contract</p>
              <div className="flex flex-wrap gap-2">
                {data.missing_dates.map((d, i) => (
                  <span key={i} className="text-xs bg-white border border-yellow-200 text-yellow-700 px-2 py-1 rounded-lg">{d}</span>
                ))}
              </div>
            </div>
          )}

          <div className="space-y-3">
            <div className="flex flex-wrap gap-2">
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide w-full mb-1">Filter by Category</p>
              {CATEGORY_FILTERS.map(cat => (
                <button key={cat} onClick={() => setCategoryFilter(cat)}
                  className={"text-xs font-medium px-3 py-1.5 rounded-lg border transition " + (categoryFilter === cat ? "bg-indigo-600 text-white border-indigo-600" : "bg-white text-gray-500 border-gray-200 hover:border-indigo-300 hover:text-indigo-600")}
                >{cat}</button>
              ))}
            </div>
            <div className="flex flex-wrap gap-2">
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide w-full mb-1">Filter by Importance</p>
              {IMPORTANCE_FILTERS.map(imp => (
                <button key={imp} onClick={() => setImportanceFilter(imp)}
                  className={"text-xs font-medium px-3 py-1.5 rounded-lg border transition " + (importanceFilter === imp ? "bg-gray-900 text-white border-gray-900" : "bg-white text-gray-500 border-gray-200 hover:border-gray-400 hover:text-gray-700")}
                >{imp}</button>
              ))}
            </div>
          </div>

          <div className="flex items-center justify-between">
            <p className="text-xs text-gray-400">
              Showing {filtered.length} of {data.total_events} events
            </p>
            <div className="flex gap-2">
              {data.has_exact_dates && <span className="text-xs bg-blue-50 text-blue-600 border border-blue-200 px-2 py-1 rounded-lg">Has exact dates</span>}
              {data.has_relative_dates && <span className="text-xs bg-yellow-50 text-yellow-600 border border-yellow-200 px-2 py-1 rounded-lg">Has relative dates</span>}
            </div>
          </div>

          {filtered.length === 0 ? (
            <div className="text-center py-10 bg-gray-50 border border-gray-100 rounded-xl">
              <p className="text-gray-500 font-medium text-sm">No events match the selected filters</p>
              <p className="text-gray-400 text-xs mt-1">Try changing the category or importance filter</p>
            </div>
          ) : (
            <div className="pl-1 pt-2">
              {filtered.map((event, index) => (
                <TimelineItem key={index} event={event} isLast={index === filtered.length - 1} />
              ))}
            </div>
          )}

          <p className="text-xs text-gray-300 text-center pb-2">
            Timeline events are extracted from contract text. Always verify dates with original documents.
          </p>
        </>
      )}

      {data && data.total_events === 0 && !loading && (
        <div className="text-center py-10 bg-gray-50 border border-gray-100 rounded-xl mt-4">
          <p className="text-gray-500 font-medium text-sm">No significant dates or deadlines were detected in this contract</p>
          <p className="text-gray-400 text-xs mt-1">The contract may use relative terms without specific dates</p>
          <button onClick={handleExtract} className="mt-4 text-xs text-indigo-500 hover:text-indigo-700 underline">Try again</button>
        </div>
      )}
    </div>
  )
}