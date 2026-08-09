"use client"

import { useState, useRef } from "react"

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

interface Props {
  onResult: (result: UploadResult, processingTime: number) => void
  onLoading: (loading: boolean) => void
}

export default function UploadSection({ onResult, onLoading }: Props) {
  const [dragOver, setDragOver] = useState(false)
  const [error, setError] = useState("")
  const [fileName, setFileName] = useState("")
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFile = async (file: File) => {
    if (file.type !== "application/pdf") {
      setError("Only PDF files are accepted.")
      return
    }

    setError("")
    setFileName(file.name)
    onLoading(true)

    const formData = new FormData()
    formData.append("file", file)

    const startTime = Date.now()

    try {
      const response = await fetch("http://localhost:8000/upload-pdf", {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.detail || "Upload failed")
      }

      const data: UploadResult = await response.json()
      const processingTime = ((Date.now() - startTime) / 1000).toFixed(1)
      onResult(data, parseFloat(processingTime))
    } catch (err: any) {
      setError(err.message || "Something went wrong.")
    } finally {
      onLoading(false)
    }
  }

  return (
    <div className="w-full max-w-2xl mx-auto mt-16">

      <div className="text-center mb-10">
        <h1 className="text-4xl font-bold text-gray-900 tracking-tight mb-3">
          Contract Intelligence
        </h1>
        <p className="text-gray-500 text-lg">
          Upload any contract for instant AI-powered analysis
        </p>
      </div>

      <div
        className={"border-2 border-dashed rounded-2xl p-16 text-center cursor-pointer transition-all duration-200 " +
          (dragOver
            ? "border-blue-400 bg-blue-50"
            : "border-gray-200 bg-white hover:border-blue-300 hover:bg-gray-50")}
        onClick={() => fileInputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault()
          setDragOver(false)
          const file = e.dataTransfer.files[0]
          if (file) handleFile(file)
        }}
      >
        <div className="w-14 h-14 bg-blue-50 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <svg className="w-7 h-7 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <p className="text-base font-semibold text-gray-700 mb-1">
          {fileName ? fileName : "Drop your contract here"}
        </p>
        <p className="text-sm text-gray-400">PDF files only — click to browse</p>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0]
            if (file) handleFile(file)
          }}
        />
      </div>

      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-100 rounded-xl text-red-600 text-sm">
          {error}
        </div>
      )}

      <p className="text-center text-xs text-gray-300 mt-6">
        Not legal advice. For informational purposes only.
      </p>
    </div>
  )
}
