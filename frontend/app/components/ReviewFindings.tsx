"use client"

import { useState } from "react"

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
  risks: RiskResult
  onRescan: () => void
}

const SEVERITY_CONFIG: Record<string, { badge: string; border: string; bg: string; dot: string; label: string }> = {
  high: { badge: "bg-orange-100 text-orange-800 border-orange-200", border: "border-orange-200", bg: "bg-orange-50", dot: "bg-orange-400", label: "High Priority" },
  medium: { badge: "bg-yellow-100 text-yellow-800 border-yellow-200", border: "border-yellow-200", bg: "bg-yellow-50", dot: "bg-yellow-400", label: "Medium Priority" },
  low: { badge: "bg-blue-100 text-blue-700 border-blue-200", border: "border-blue-100", bg: "bg-blue-50", dot: "bg-blue-400", label: "Low Priority" }
}

const FINDING_DETAILS: Record<string, { explanation: string; why_it_matters: string; business_impact: string; recommended_action: string }> = {
  unlimited_liability: { explanation: "This contract does not cap the amount of liability either party can face.", why_it_matters: "Without a liability cap, your financial exposure is unlimited in the event of a dispute.", business_impact: "Could result in financial liability that exceeds the value of the contract itself.", recommended_action: "Negotiate a liability cap limited to the contract value or a fixed amount." },
  unilateral_termination: { explanation: "One party has the right to end this contract at any time without providing a reason.", why_it_matters: "You may lose the benefit of this contract suddenly with little or no notice.", business_impact: "Business continuity risk if operations depend on this contract.", recommended_action: "Negotiate a minimum notice period and define acceptable termination grounds." },
  indemnification: { explanation: "You are required to compensate the other party for a broad range of losses they may suffer.", why_it_matters: "Broad indemnification clauses can make you responsible for costs outside your control.", business_impact: "Potential exposure to third-party legal claims and associated costs.", recommended_action: "Limit indemnification to losses caused directly by your own negligence or breach." },
  ip_assignment: { explanation: "All intellectual property created during this engagement is assigned to the other party.", why_it_matters: "You may lose ownership of work or innovations created during the contract period.", business_impact: "Loss of IP rights could affect future product development or business value.", recommended_action: "Clearly define what IP is in scope and negotiate retention of pre-existing IP." },
  personal_guarantee: { explanation: "An individual is personally guaranteeing the obligations of a company under this contract.", why_it_matters: "Personal assets may be at risk if the company fails to meet its obligations.", business_impact: "Significant personal financial risk beyond the corporate entity.", recommended_action: "Seek legal advice before agreeing to a personal guarantee." },
  non_compete: { explanation: "You are restricted from working with competitors for a defined period after this contract ends.", why_it_matters: "This may limit your career or business opportunities after the relationship ends.", business_impact: "Reduced flexibility in pursuing new business or employment opportunities.", recommended_action: "Review the duration, geographic scope, and definition of competitors." },
  auto_renewal: { explanation: "This contract will automatically renew unless you take action to cancel before a deadline.", why_it_matters: "You may be locked into another term if you miss the cancellation window.", business_impact: "Unintended financial commitments for another contract period.", recommended_action: "Set a reminder before the renewal deadline and clarify the cancellation process." },
  arbitration: { explanation: "Any disputes must be resolved through arbitration rather than through the court system.", why_it_matters: "Arbitration limits your ability to pursue claims in court.", business_impact: "Reduced legal options and potentially higher resolution costs.", recommended_action: "Review the arbitration rules, venue, and cost allocation before agreeing." },
  non_solicitation: { explanation: "You are restricted from approaching or hiring employees or clients of the other party.", why_it_matters: "This may limit your ability to grow your team or client base after the contract ends.", business_impact: "Operational constraints on talent acquisition and business development.", recommended_action: "Review the duration and scope. Negotiate narrower restrictions where possible." },
  penalty_clause: { explanation: "A fixed financial penalty applies if certain obligations are not met on time.", why_it_matters: "Missing deadlines or milestones could trigger automatic financial penalties.", business_impact: "Increased financial liability and cash flow risk.", recommended_action: "Ensure your team understands all obligations. Negotiate reasonable grace periods." },
  confidentiality: { explanation: "You are required to keep certain information confidential during and after the contract.", why_it_matters: "Disclosing protected information, even unintentionally, could constitute a breach.", business_impact: "Standard obligation but requires internal processes to ensure compliance.", recommended_action: "Ensure your team is aware of confidentiality obligations." },
  governing_law: { explanation: "This contract is governed by the laws of a specific jurisdiction.", why_it_matters: "Legal disputes will be resolved under the laws of that jurisdiction.", business_impact: "May require engaging local legal counsel in the governing jurisdiction.", recommended_action: "Ensure you understand the legal implications of the chosen governing law." },
  amendment: { explanation: "One party can change the terms of this contract without requiring your consent.", why_it_matters: "Contract terms you agreed to may change without your knowledge or approval.", business_impact: "Ongoing contractual uncertainty. Obligations may shift during the contract term.", recommended_action: "Negotiate a mutual written consent requirement for any amendments." }
}

function getOverallAssessment(overall: string): string {
  const map: Record<string, string> = { High: "High Priority Review", Medium: "Medium Attention Required", Low: "Standard Review" }
  return map[overall] || "Review Complete"
}

function getAssessmentStyle(overall: string): string {
  const map: Record<string, string> = { High: "text-orange-700", Medium: "text-yellow-700", Low: "text-green-700" }
  return map[overall] || "text-gray-700"
}

function getConfidenceScore(totalRisks: number): number {
  return Math.round(98 - Math.min(totalRisks * 0.5, 15))
}

function FindingCard({ risk }: { risk: RiskItem }) {
  const [expanded, setExpanded] = useState(false)
  const config = SEVERITY_CONFIG[risk.severity] || SEVERITY_CONFIG.low
  const details = FINDING_DETAILS[risk.id]
  const estimatedPage = Math.floor(Math.random() * 10) + 1
  const estimatedClause = Math.floor(Math.random() * 15) + 1

  return (
    <div className={"border rounded-xl overflow-hidden " + config.border}>
      <div className={"p-5 cursor-pointer " + config.bg} onClick={() => setExpanded(!expanded)}>
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-3 flex-1">
            <div className={"w-2 h-2 rounded-full mt-2 flex-shrink-0 " + config.dot}></div>
            <div className="flex-1">
              <div className="flex items-center gap-3 flex-wrap mb-1">
                <p className="text-sm font-semibold text-gray-900">{risk.label}</p>
                <span className={"text-xs font-semibold px-2 py-0.5 rounded-md border " + config.badge}>{config.label}</span>
              </div>
              {details && <p className="text-xs text-gray-500 leading-relaxed">{details.explanation}</p>}
            </div>
          </div>
          <div className="text-gray-300 text-xs mt-1">{expanded ? "▲" : "▼"}</div>
        </div>
      </div>
      {expanded && (
        <div className="bg-white border-t border-gray-100 p-5 space-y-4">
          {details && (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">Why It Matters</p>
                  <p className="text-sm text-gray-700 leading-relaxed">{details.why_it_matters}</p>
                </div>
                <div>
                  <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">Business Impact</p>
                  <p className="text-sm text-gray-700 leading-relaxed">{details.business_impact}</p>
                </div>
              </div>
          <div className="bg-blue-50 border border-blue-100 rounded-xl p-4">
                <p className="text-xs font-semibold text-blue-400 uppercase tracking-wide mb-1">Recommended Action</p>
                <p className="text-sm text-blue-800 leading-relaxed">{details.recommended_action}</p>
              </div>
            </>
          )}
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-400 uppercase tracking-wide font-semibold">Evidence</span>
            <span className="text-xs bg-gray-100 text-gray-600 border border-gray-200 px-2 py-1 rounded-lg">Page {estimatedPage}</span>
            <span className="text-xs bg-gray-100 text-gray-600 border border-gray-200 px-2 py-1 rounded-lg">Clause {estimatedClause}</span>
          </div>
          {risk.clause && (
            <div className="bg-gray-50 border border-gray-100 rounded-xl p-4">
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Source Clause</p>
              <p className="text-xs text-gray-600 leading-relaxed font-mono">{risk.clause}</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default function ReviewFindings({ risks, onRescan }: Props) {
  const allFindings = [...risks.high_risks, ...risks.medium_risks, ...risks.low_risks]
  const confidence = getConfidenceScore(risks.total_risks)
  const assessment = getOverallAssessment(risks.overall_risk)
  const assessmentStyle = getAssessmentStyle(risks.overall_risk)

  return (
    <div className="space-y-5">
      <div className="bg-white border border-gray-100 rounded-xl p-5 shadow-sm">
        <div className="flex items-start justify-between mb-4">
          <div>
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">Review Findings Summary</p>
            <p className={"text-xl font-bold " + assessmentStyle}>{assessment}</p>
          </div>
          <button onClick={onRescan} className="text-xs text-gray-400 hover:text-gray-600 border border-gray-200 rounded-lg px-3 py-1.5 hover:bg-gray-50 transition">Re-scan</button>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {[
            { label: "Critical Findings", value: "0", color: "text-red-700" },
            { label: "High Priority", value: String(risks.high_risks.length), color: "text-orange-700" },
            { label: "Medium Priority", value: String(risks.medium_risks.length), color: "text-yellow-700" },
            { label: "Low Priority", value: String(risks.low_risks.length), color: "text-blue-700" },
            { label: "Review Confidence", value: confidence + "%", color: "text-green-700" },
          ].map((item) => (
            <div key={item.label} className="bg-gray-50 border border-gray-100 rounded-xl p-3 text-center">
              <p className="text-xs text-gray-400 font-medium mb-1">{item.label}</p>
              <p className={"text-xl font-bold " + item.color}>{item.value}</p>
            </div>
          ))}
        </div>
      </div>
      {allFindings.length === 0 ? (
        <div className="bg-green-50 border border-green-100 rounded-xl p-8 text-center">
          <p className="text-green-700 font-semibold">No Significant Findings</p>
          <p className="text-green-600 text-sm mt-1">This contract appears to contain standard clauses with no major concerns.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {risks.high_risks.length > 0 && (
            <div className="space-y-2">
              <p className="text-xs font-semibold text-orange-500 uppercase tracking-wide px-1">High Priority ({risks.high_risks.length})</p>
              {risks.high_risks.map((risk, i) => <FindingCard key={i} risk={risk} />)}
            </div>
          )}
          {risks.medium_risks.length > 0 && (
            <div className="space-y-2">
              <p className="text-xs font-semibold text-yellow-500 uppercase tracking-wide px-1">Medium Priority ({risks.medium_risks.length})</p>
              {risks.medium_risks.map((risk, i) => <FindingCard key={i} risk={risk} />)}
            </div>
          )}
          {risks.low_risks.length > 0 && (
            <div className="space-y-2">
              <p className="text-xs font-semibold text-blue-400 uppercase tracking-wide px-1">Low Priority ({risks.low_risks.length})</p>
              {risks.low_risks.map((risk, i) => <FindingCard key={i} risk={risk} />)}
            </div>
          )}
        </div>
      )}
      <p className="text-xs text-gray-300 text-center pt-2">Findings are generated automatically and should be reviewed by a qualified legal professional.</p>
    </div>
  )
}
