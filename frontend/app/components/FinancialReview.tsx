"use client"

import { useState } from "react"

interface FinancialField {
  value: string | null
  found: boolean
  evidence: string | null
  page_hint: string | null
  risk_level: string
  ai_explanation: string
}

interface FinancialData {
  payment_amount: FinancialField
  currency: FinancialField
  deposit: FinancialField
  security_deposit: FinancialField
  payment_schedule: FinancialField
  billing_cycle: FinancialField
  late_payment_penalty: FinancialField
  refund_policy: FinancialField
  taxes: FinancialField
  renewal_cost: FinancialField
  interest: FinancialField
  additional_charges: FinancialField
  overall_financial_risk: string
  financial_summary: string
  hidden_risks: string[]
  missing_fields: string[]
}

interface Props {
  extractedText: string
}

const FIELD_LABELS: Record<string, string> = {
  payment_amount: "Payment Amount",
  currency: "Currency",
  deposit: "Deposit",
  security_deposit: "Security Deposit",
  payment_schedule: "Payment Schedule",
  billing_cycle: "Billing Cycle",
  late_payment_penalty: "Late Payment Penalty",
  refund_policy: "Refund Policy",
  taxes: "Taxes",
  renewal_cost: "Renewal Cost",
  interest: "Interest",
  additional_charges: "Additional Charges"
}

const FIELD_ICONS: Record<string, string> = {
  payment_amount: "dollar",
  currency: "globe",
  deposit: "arrow-down",
  security_deposit: "shield",
  payment_schedule: "calendar",
  billing_cycle: "refresh",
  late_payment_penalty: "warning",
  refund_policy: "arrow-left",
  taxes: "receipt",
  renewal_cost: "refresh",
  interest: "trending-up",
  additional_charges: "plus"
}

const RISK_STYLES: Record<string, string> = {
  High: "bg-red-50 text-red-700 border-red-200",
  Medium: "bg-yellow-50 text-yellow-700 border-yellow-200",
  Low: "bg-green-50 text-green-700 border-green-200"
}

const OVERALL_RISK_STYLES: Record<string, string> = {
  High: "bg-red-50 border-red-200 text-red-700",
  Medium: "bg-yellow-50 border-yellow-200 text-yellow-700",
  Low: "bg-green-50 border-green-200 text-green-700"
}

function FinancialCard({ fieldKey, field }: { fieldKey: string; field: FinancialField }) {
  const [expanded, setExpanded] = useState(false)
  const label = FIELD_LABELS[fieldKey] || fieldKey

  return (
    <div className={"border rounded-xl overflow-hidden transition-all " + (field.found ? "border-gray-100 bg-white" : "border-dashed border-gray-200 bg-gray-50")}>
      <div className="p-4">
        <div className="flex items-start justify-between gap-2 mb-2">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide">{label}</p>
          <div className="flex items-center gap-1.5 flex-shrink-0">
            {field.found && (
              <span className={"text-xs font-semibold px-2 py-0.5 rounded-md border " + (RISK_STYLES[field.risk_level] || RISK_STYLES.Low)}>
                {field.risk_level}
              </span>
            )}
            {!field.found && (
              <span className="text-xs font-semibold px-2 py-0.5 rounded-md border bg-gray-100 text-gray-400 border-gray-200">
                Not Found
              </span>
            )}
          </div>
        </div>

        <p className={"text-base font-bold mb-2 " + (field.found ? "text-gray-900" : "text-gray-300")}>
          {field.found ? (field.value || "Present") : "Not specified"}
        </p>

        {field.found && field.ai_explanation && (
          <p className="text-xs text-gray-500 leading-relaxed">{field.ai_explanation}</p>
        )}

        {!field.found && (
          <p className="text-xs text-gray-400 italic">This financial term was not found in the contract.</p>
        )}

        {field.found && (field.evidence || field.page_hint) && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-xs text-blue-500 hover:text-blue-700 mt-2 underline"
          >
            {expanded ? "Hide evidence" : "View evidence"}
          </button>
        )}
      </div>

      {expanded && field.found && (
        <div className="border-t border-gray-100 p-4 bg-gray-50 space-y-2">
          {field.page_hint && (
            <div className="flex items-center gap-2">
              <span className="text-xs bg-white border border-gray-200 text-gray-500 px-2 py-1 rounded-lg">
                Location: {field.page_hint}
              </span>
            </div>
          )}
          {field.evidence && (
            <div>
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">Source Text</p>
              <p className="text-xs text-gray-600 leading-relaxed font-mono bg-white border border-gray-100 rounded-lg p-3">
                {field.evidence}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

const FIELD_KEYS = [
  "payment_amount", "currency", "deposit", "security_deposit",
  "payment_schedule", "billing_cycle", "late_payment_penalty",
  "refund_policy", "taxes", "renewal_cost", "interest", "additional_charges"
]

export default function FinancialReview({ extractedText }: Props) {
  const [data, setData] = useState<FinancialData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleExtract = async () => {
    setLoading(true)
    setError("")
    setData(null)
    try {
      const response = await fetch("http://localhost:8000/extract-financials", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ extracted_text: extractedText })
      })
      if (!response.ok) throw new Error("Failed")
      const result = await response.json()
      setData(result)
    } catch {
      setError("Could not extract financial data. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  const foundCount = data ? FIELD_KEYS.filter(k => (data as any)[k]?.found).length : 0
  const highRiskCount = data ? FIELD_KEYS.filter(k => (data as any)[k]?.found && (data as any)[k]?.risk_level === "High").length : 0

  return (
    <div className="space-y-5">

      {!data && !loading && (
        <div className="text-center py-10">
          <div className="w-12 h-12 bg-green-50 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <svg className="w-6 h-6 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <p className="text-gray-600 font-medium mb-1">Financial Review</p>
          <p className="text-gray-400 text-sm mb-6">Extract and analyze all financial terms from this contract</p>
          <button
            onClick={handleExtract}
            className="bg-green-600 text-white px-8 py-3 rounded-xl text-sm font-semibold hover:bg-green-700 transition shadow-sm"
          >
            Extract Financial Data
          </button>
        </div>
      )}

      {loading && (
        <div className="text-center py-10">
          <div className="w-8 h-8 border-2 border-green-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-500 text-sm">Analyzing financial terms...</p>
          <p className="text-gray-400 text-xs mt-1">This may take 15-30 seconds</p>
        </div>
      )}

      {error && (
        <div className="p-4 bg-red-50 border border-red-100 rounded-xl text-red-600 text-sm">{error}</div>
      )}

      {data && (
        <>
          <div className={"border rounded-xl p-5 " + (OVERALL_RISK_STYLES[data.overall_financial_risk] || "bg-gray-50 border-gray-100")}>
            <div className="flex items-start justify-between mb-3">
              <div>
                <p className="text-xs font-semibold uppercase tracking-wide opacity-60 mb-1">Overall Financial Risk</p>
                <p className="text-2xl font-bold">{data.overall_financial_risk} Risk</p>
              </div>
              <div className="text-right">
                <p className="text-xs opacity-60 mb-1">Fields Found</p>
                <p className="text-2xl font-bold">{foundCount} / {FIELD_KEYS.length}</p>
              </div>
            </div>
            <p className="text-sm leading-relaxed opacity-80">{data.financial_summary}</p>
          </div>

          <div className="grid grid-cols-3 gap-3">
            {[
              { label: "Fields Found", value: foundCount, color: "text-blue-700", bg: "bg-blue-50 border-blue-100" },
              { label: "High Risk Items", value: highRiskCount, color: "text-red-700", bg: "bg-red-50 border-red-100" },
              { label: "Missing Fields", value: data.missing_fields?.length || 0, color: "text-gray-500", bg: "bg-gray-50 border-gray-100" },
            ].map(item => (
              <div key={item.label} className={"border rounded-xl p-4 text-center " + item.bg}>
                <p className="text-xs text-gray-400 font-medium mb-1">{item.label}</p>
                <p className={"text-2xl font-bold " + item.color}>{item.value}</p>
              </div>
            ))}
          </div>

          {data.hidden_risks && data.hidden_risks.length > 0 && (
            <div className="bg-red-50 border border-red-100 rounded-xl p-4">
              <p className="text-xs font-semibold text-red-400 uppercase tracking-wide mb-3">Hidden Risks and Penalties Detected</p>
              <ul className="space-y-2">
                {data.hidden_risks.map((risk, i) => (
                  <li key={i} className="flex gap-3 text-sm text-red-700">
                    <span className="w-1.5 h-1.5 rounded-full bg-red-400 mt-2 flex-shrink-0"></span>
                    <span>{risk}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {data.missing_fields && data.missing_fields.length > 0 && (
            <div className="bg-yellow-50 border border-yellow-100 rounded-xl p-4">
              <p className="text-xs font-semibold text-yellow-500 uppercase tracking-wide mb-3">Missing Financial Information</p>
              <div className="flex flex-wrap gap-2">
                {data.missing_fields.map((field, i) => (
                  <span key={i} className="text-xs bg-white border border-yellow-200 text-yellow-700 px-2 py-1 rounded-lg">
                    {FIELD_LABELS[field] || field}
                  </span>
                ))}
              </div>
            </div>
          )}

          <div>
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3 px-1">Financial Terms</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {FIELD_KEYS.map(key => {
                const field = (data as any)[key] as FinancialField
                if (!field) return null
                return <FinancialCard key={key} fieldKey={key} field={field} />
              })}
            </div>
          </div>

          <div className="flex justify-center pt-2">
            <button
              onClick={() => setData(null)}
              className="text-xs text-gray-400 hover:text-gray-600 border border-gray-200 rounded-lg px-3 py-1.5 hover:bg-gray-50 transition"
            >
              Re-extract
            </button>
          </div>

          <p className="text-xs text-gray-300 text-center">
            Financial data is extracted automatically. Always verify with official documents.
          </p>
        </>
      )}
    </div>
  )
}
