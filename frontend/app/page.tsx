"use client"

import { useState } from "react"
import Navbar from "./components/Navbar"
import UploadSection from "./components/UploadSection"
import ResultSection from "./components/ResultSection"

interface UploadResult {
  file_name: string
  file_size: string
  page_count: number
  word_count: number
  extracted_text: string
  chunks: string[]
  chunk_stats: {
    total_chunks: number
    avg_chunk_size: number
    min_chunk_size: number
    max_chunk_size: number
  }
  collection_name: string
  embeddings_stored: number
}

export default function Home() {
  const [result, setResult] = useState<UploadResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [processingTime, setProcessingTime] = useState(0)

  const handleResult = (data: UploadResult, time: number) => {
    setResult(data)
    setProcessingTime(time)
  }

  return (
    <main className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="px-4 py-6">
        {loading && (
          <div className="flex flex-col items-center justify-center mt-32 gap-4">
            <div className="w-10 h-10 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            <p className="text-gray-400 text-sm">Processing contract...</p>
          </div>
        )}

        {!result && !loading && (
          <UploadSection onResult={handleResult} onLoading={setLoading} />
        )}

        {result && !loading && (
          <>
            <ResultSection result={result} processingTime={processingTime} />
            <div className="text-center mt-2 mb-8">
              <button
                onClick={() => setResult(null)}
                className="text-xs text-gray-400 hover:text-gray-600 transition"
              >
                Upload a different contract
              </button>
            </div>
          </>
        )}
      </div>
    </main>
  )
}
