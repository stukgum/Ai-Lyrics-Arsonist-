"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"

interface LyricLine {
  line_index: number
  text: string
  syllable_target: number
  rhyme_tag: string
  suggested_bar_start: number
  timestamp_start?: number
  timestamp_end?: number
  actual_syllables?: number
}

interface LyricSection {
  name: string
  bars: number[]
  lines: LyricLine[]
}

interface GeneratedLyrics {
  title: string
  sections: LyricSection[]
  metadata: {
    estimated_total_syllables: number
    actual_total_syllables?: number
    total_lines?: number
  }
}

interface Generation {
  generation_id: string
  status: string
  lyrics: GeneratedLyrics
  quality_metrics: {
    rhyme_accuracy: number
    syllable_accuracy: number
    structure_match: number
  }
  export_urls: {
    lrc?: string
    srt?: string
    txt?: string
    pdf?: string
  }
}

export default function EditorPage({ params }: { params: { generationId: string } }) {
  const router = useRouter()
  const [generation, setGeneration] = useState<Generation | null>(null)
  const [audioFeatures, setAudioFeatures] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [editedLyrics, setEditedLyrics] = useState<GeneratedLyrics | null>(null)
  const [selectedLine, setSelectedLine] = useState<number | null>(null)
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)

  useEffect(() => {
    fetchGeneration()
  }, [params.generationId])

  const fetchGeneration = async () => {
    try {
      const response = await fetch(`/api/v1/generation/${params.generationId}`)
      if (!response.ok) {
        throw new Error('Failed to fetch generation')
      }
      const data = await response.json()
      setGeneration(data)
      setEditedLyrics(data.lyrics)
      
      // Fetch audio features from the job
      if (data.job_id) {
        const featuresResponse = await fetch(`/api/v1/jobs/${data.job_id}/features`)
        if (featuresResponse.ok) {
          const featuresData = await featuresResponse.json()
          setAudioFeatures(featuresData)
        }
      }
    } catch (err) {
      setError('Failed to load generation')
    } finally {
      setLoading(false)
    }
  }

  const countSyllables = (text: string): number => {
    // Simple syllable counting - in production, use the backend syllable counter
    const words = text.toLowerCase().match(/[a-z]+/g) || []
    return words.reduce((count, word) => {
      const syllables = word.match(/[aeiouy]+/g)?.length || 1
      return count + Math.max(1, syllables)
    }, 0)
  }

  const updateLineText = (sectionIndex: number, lineIndex: number, newText: string) => {
    if (!editedLyrics) return

    const newLyrics = { ...editedLyrics }
    const line = newLyrics.sections[sectionIndex].lines[lineIndex]
    line.text = newText
    line.actual_syllables = countSyllables(newText)
    
    setEditedLyrics(newLyrics)
    setHasUnsavedChanges(true)
  }

  const updateTitle = (newTitle: string) => {
    if (!editedLyrics) return
    
    const newLyrics = { ...editedLyrics }
    newLyrics.title = newTitle
    setEditedLyrics(newLyrics)
    setHasUnsavedChanges(true)
  }

  const getSyllableAccuracy = (line: LyricLine): 'perfect' | 'good' | 'poor' => {
    const actual = line.actual_syllables || countSyllables(line.text)
    const target = line.syllable_target
    const diff = Math.abs(actual - target)
    
    if (diff === 0) return 'perfect'
    if (diff <= 1) return 'good'
    return 'poor'
  }

  const getSyllableColor = (accuracy: string) => {
    switch (accuracy) {
      case 'perfect': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
      case 'good': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
      case 'poor': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
    }
  }

  const handleExport = (format: string) => {
    window.open(`/api/v1/export/${params.generationId}?format=${format}`, '_blank')
  }

  if\
