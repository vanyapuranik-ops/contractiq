"use client"

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

interface Props {
  summary: Summary
  onRegenerate: () => void
}

function SectionCard({
  title,
  children,
  accent = "gray"
}: {
  title: string
  children: React.ReactNode
  accent?: "gray" | "blue" | "red" | "green" | "yellow"
}) {
  const accentStyles: Record<string, string> = {
    gray: "border-gray-100 bg-gray-50",
    blue: "border-blue-100 bg-blue-50",
    red: "border-red-100 bg-red-50",
    green: "border-green-100 bg-green-50",
    yellow: "border-yellow-100 bg-yellow-50"
  }
  const titleStyles: Record<string, string> = {
    gray: "text-gray-400",
    blue: "text-blue-400",
    red: "text-red-400",
    green: "text-green-500",
    yellow: "text-yellow-500"
  }

  return (
    <div className={"border rounded-xl p-5 " + accentStyles[accent]}>
      <p className={"text-xs font-semibold uppercase tracking-widest mb-3 " + titleStyles[accent]}>
        {title}
      </p>
      {children}
    </div>
  )
}

function BulletList({ items, color = "blue" }: { items: string[], color?: string }) {
  const dotColor: Record<string, string> = {
    blue: "bg-blue-400",
    red: "bg-red-400",
    yellow: "bg-yellow-400",
    green: "bg-green-400",
    gray: "bg-gray-300"
  }
  return (
    <ul className="space-y-2">
      {items.map((item, i) => (
        <li key={i} className="flex gap-3 text-sm text-gray-700">
          <span className={"w-1.5 h-1.5 rounded-full mt-2 flex-shrink-0 " + (dotColor[color] || dotColor.blue)}></span>
          <span className="leading-relaxed">{item}</span>
        </li>
      ))}
    </ul>
  )
}

export default function SummaryTab({ summary, onRegenerate }: Props) {
  return (
    <div className="space-y-4">

      <div className="flex items-center justify-between mb-2">
        <div>
          <h3 className="text-base font-semibold text-gray-900">Executive Review</h3>
          <p className="text-xs text-gray-400 mt-0.5">AI-generated summary for non-lawyers</p>
        </div>
        <button
          onClick={onRegenerate}
          className="text-xs text-gray-400 hover:text-gray-600 border border-gray-200 rounded-lg px-3 py-1.5 hover:bg-gray-50 transition"
        >
          Regenerate
        </button>
      </div>

      <SectionCard title="Overview" accent="blue">
        <p className="text-sm text-gray-800 leading-relaxed">{summary.summary}</p>
      </SectionCard>

      <div className="grid grid-cols-2 gap-3">
        <SectionCard title="Contract Type" accent="gray">
          <p className="text-sm font-semibold text-gray-800">{summary.contract_type || "Not specified"}</p>
        </SectionCard>
        <SectionCard title="Agreement Status" accent="gray">
          <span className="text-xs font-semibold bg-blue-100 text-blue-700 px-2 py-1 rounded-lg">
            Under Review
          </span>
        </SectionCard>
      </div>

      {summary.parties.length > 0 && (
        <SectionCard title="Who Are the Parties?" accent="gray">
          <div className="flex flex-wrap gap-2">
            {summary.parties.map((party, i) => (
              <div key={i} className="flex items-center gap-2 bg-white border border-gray-200 rounded-lg px-3 py-2 shadow-sm">
                <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                  <span className="text-xs font-bold text-blue-600">{party.charAt(0)}</span>
                </div>
                <span className="text-sm text-gray-700 font-medium">{party}</span>
              </div>
            ))}
          </div>
        </SectionCard>
      )}

      {summary.key_points.length > 0 && (
        <SectionCard title="Most Important Obligations" accent="blue">
          <BulletList items={summary.key_points} color="blue" />
        </SectionCard>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <SectionCard title="Financial Commitments" accent="green">
          <p className="text-sm text-gray-700 leading-relaxed">
            {summary.financial_terms || "No specific financial terms identified."}
          </p>
        </SectionCard>

        <SectionCard title="Important Dates" accent="yellow">
          <div className="space-y-2">
            {[
              { label: "Effective Date", value: summary.effective_date },
              { label: "Duration", value: summary.duration }
            ].map((item) => (
              <div key={item.label} className="flex justify-between items-center">
                <span className="text-xs text-gray-400">{item.label}</span>
                <span className="text-xs font-semibold text-gray-700 bg-white border border-gray-200 px-2 py-1 rounded-lg">
                  {item.value || "Unknown"}
                </span>
              </div>
            ))}
          </div>
        </SectionCard>
      </div>

      <SectionCard title="Restrictions to Know" accent="yellow">
        <p className="text-sm text-gray-700 leading-relaxed">
          {summary.termination || "No specific restrictions identified."}
        </p>
      </SectionCard>

      {summary.risks.length > 0 && (
        <SectionCard title="Before You Sign — Key Risks" accent="red">
          <BulletList items={summary.risks} color="red" />
          <p className="text-xs text-red-400 mt-4 pt-3 border-t border-red-100">
            This is not legal advice. Consult a qualified lawyer before signing any contract.
          </p>
        </SectionCard>
      )}

    </div>
  )
}
