"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import { RefreshCw, Save } from "lucide-react"

interface LyricLine {
  id: string
  text: string
  start_time: number
  end_time: number
  syllable_count: number
  rhyme_scheme?: string
  bar_index: number
}

interface LyricEditorProps {
  lines: LyricLine[]
  onLinesChange: (lines: LyricLine[]) => void
  onRegenerateSection: (startBar: number, endBar: number) => void
  isPlaying?: boolean
  currentTime?: number
}

export function LyricEditor({
  lines,
  onLinesChange,
  onRegenerateSection,
  isPlaying,
  currentTime = 0,
}: LyricEditorProps) {
  const [selectedLines, setSelectedLines] = useState<string[]>([])
  const [editingLine, setEditingLine] = useState<string | null>(null)
  const [editText, setEditText] = useState("")

  const countSyllables = (text: string): number => {
    // Simple syllable counting heuristic
    const vowels = "aeiouyAEIOUY"
    let count = 0
    let previousWasVowel = false

    for (let i = 0; i < text.length; i++) {
      const isVowel = vowels.includes(text[i])
      if (isVowel && !previousWasVowel) {
        count++
      }
      previousWasVowel = isVowel
    }

    // Handle silent e
    if (text.toLowerCase().endsWith("e") && count > 1) {
      count--
    }

    return Math.max(1, count)
  }

  const getRhymeColor = (rhyme?: string) => {
    const colors = {
      A: "bg-red-100 text-red-800",
      B: "bg-blue-100 text-blue-800",
      C: "bg-green-100 text-green-800",
      D: "bg-yellow-100 text-yellow-800",
      E: "bg-purple-100 text-purple-800",
      F: "bg-pink-100 text-pink-800",
    }
    return rhyme ? colors[rhyme as keyof typeof colors] || "bg-gray-100 text-gray-800" : "bg-gray-100 text-gray-800"
  }

  const handleLineEdit = (lineId: string, newText: string) => {
    const updatedLines = lines.map((line) =>
      line.id === lineId ? { ...line, text: newText, syllable_count: countSyllables(newText) } : line,
    )
    onLinesChange(updatedLines)
  }

  const handleRegenerateSelected = () => {
    if (selectedLines.length === 0) return

    const selectedLineObjects = lines.filter((line) => selectedLines.includes(line.id))
    const minBar = Math.min(...selectedLineObjects.map((line) => line.bar_index))
    const maxBar = Math.max(...selectedLineObjects.map((line) => line.bar_index))

    onRegenerateSection(minBar, maxBar)
    setSelectedLines([])
  }

  const toggleLineSelection = (lineId: string) => {
    setSelectedLines((prev) => (prev.includes(lineId) ? prev.filter((id) => id !== lineId) : [...prev, lineId]))
  }

  const getCurrentLine = () => {
    return lines.find((line) => currentTime >= line.start_time && currentTime <= line.end_time)
  }

  const currentLine = getCurrentLine()

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Lyric Editor</CardTitle>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleRegenerateSelected}
              disabled={selectedLines.length === 0}
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Regenerate Selected
            </Button>
            <Button variant="outline" size="sm">
              <Save className="h-4 w-4 mr-2" />
              Save Changes
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {lines.map((line, index) => (
            <div
              key={line.id}
              className={`p-3 rounded-lg border transition-all ${
                selectedLines.includes(line.id)
                  ? "border-purple-300 bg-purple-50 dark:bg-purple-900/20"
                  : "border-gray-200 hover:border-gray-300"
              } ${currentLine?.id === line.id ? "ring-2 ring-blue-400 bg-blue-50 dark:bg-blue-900/20" : ""}`}
              onClick={() => toggleLineSelection(line.id)}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  {editingLine === line.id ? (
                    <Textarea
                      value={editText}
                      onChange={(e) => setEditText(e.target.value)}
                      onBlur={() => {
                        handleLineEdit(line.id, editText)
                        setEditingLine(null)
                      }}
                      onKeyDown={(e) => {
                        if (e.key === "Enter" && !e.shiftKey) {
                          e.preventDefault()
                          handleLineEdit(line.id, editText)
                          setEditingLine(null)
                        }
                      }}
                      className="min-h-[60px]"
                      autoFocus
                    />
                  ) : (
                    <p
                      className="text-sm leading-relaxed cursor-text"
                      onDoubleClick={() => {
                        setEditingLine(line.id)
                        setEditText(line.text)
                      }}
                    >
                      {line.text}
                    </p>
                  )}
                </div>

                <div className="flex flex-col gap-1 items-end">
                  <div className="flex gap-1">
                    <Badge variant="secondary" className="text-xs">
                      Bar {line.bar_index + 1}
                    </Badge>
                    <Badge variant="outline" className="text-xs">
                      {line.syllable_count} syl
                    </Badge>
                    {line.rhyme_scheme && (
                      <Badge className={`text-xs ${getRhymeColor(line.rhyme_scheme)}`}>{line.rhyme_scheme}</Badge>
                    )}
                  </div>
                  <div className="text-xs text-gray-500">
                    {line.start_time.toFixed(1)}s - {line.end_time.toFixed(1)}s
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {lines.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            No lyrics generated yet. Generate lyrics to start editing.
          </div>
        )}
      </CardContent>
    </Card>
  )
}
