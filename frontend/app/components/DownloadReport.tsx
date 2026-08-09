"use client"

import { useState } from "react"

interface Props {
  extractedText: string
  fileName: string
  fileSize?: string
  pageCount?: number
  wordCount?: number
  collectionName?: string
}

export default function DownloadReport({
  extractedText,
  fileName,
  fileSize,
  pageCount,
  wordCount,
  collectionName
}: Props) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleDownload = async () => {
    setLoading(true)
    setError("")

    try {
      const response = await fetch("http://localhost:8000/download-report", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          extracted_text: extractedText,
          file_name: fileName,
          file_size: fileSize || null,
          page_count: pageCount || null,
          word_count: wordCount || null,
          collection_name: collectionName || null,
          include_summary: true,
          include_risks: true,
          include_clauses: true,
          include_financials: true,
          include_timeline: true,
          include_obligations: true
        })
      })

      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.detail || "Report generation failed")
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = fileName.replace(".pdf", "_review_report.pdf")
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)

    } catch (err: any) {
      setError(err.message || "Could not generate report. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col items-center gap-2">
      <button
        onClick={handleDownload}
        disabled={loading}
        className="flex items-center gap-2 bg-gray-900 text-white px-6 py-3 rounded-xl text-sm font-semibold hover:bg-gray-700 disabled:opacity-50 transition shadow-sm"
      >
        {loading ? (
          <>
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            Generating Report...
          </>
        ) : (
          <>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Download AI Review Report
          </>
        )}
      </button>
      {loading && (
        <p className="text-xs text-gray-400">This may take 60-90 seconds. All modules are being analyzed.</p>
      )}
      {error && (
        <p className="text-xs text-red-500">{error}</p>
      )}
    </div>
  )
}