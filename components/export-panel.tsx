"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import { Download, FileText, Music, Video, File } from "lucide-react"

interface ExportPanelProps {
  generationId: string
  onExport: (format: string, options: any) => void
}

export function ExportPanel({ generationId, onExport }: ExportPanelProps) {
  const [selectedFormat, setSelectedFormat] = useState<string>("")
  const [includeTimestamps, setIncludeTimestamps] = useState(true)
  const [includeMetadata, setIncludeMetadata] = useState(true)
  const [fontSize, setFontSize] = useState("12")
  const [isExporting, setIsExporting] = useState(false)

  const exportFormats = [
    { value: "lrc", label: "LRC (Lyrics with timestamps)", icon: Music },
    { value: "srt", label: "SRT (SubRip subtitle format)", icon: Video },
    { value: "txt", label: "TXT (Plain text)", icon: FileText },
    { value: "pdf", label: "PDF (Formatted document)", icon: File },
  ]

  const handleExport = async () => {
    if (!selectedFormat) return

    setIsExporting(true)

    const options = {
      includeTimestamps,
      includeMetadata,
      fontSize: Number.parseInt(fontSize),
    }

    try {
      await onExport(selectedFormat, options)
    } finally {
      setIsExporting(false)
    }
  }

  const getFormatIcon = (format: string) => {
    const formatData = exportFormats.find((f) => f.value === format)
    return formatData?.icon || FileText
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Download className="h-5 w-5" />
          Export Lyrics
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <label className="text-sm font-medium mb-2 block">Export Format</label>
          <Select value={selectedFormat} onValueChange={setSelectedFormat}>
            <SelectTrigger>
              <SelectValue placeholder="Choose export format" />
            </SelectTrigger>
            <SelectContent>
              {exportFormats.map((format) => {
                const Icon = format.icon
                return (
                  <SelectItem key={format.value} value={format.value}>
                    <div className="flex items-center gap-2">
                      <Icon className="h-4 w-4" />
                      {format.label}
                    </div>
                  </SelectItem>
                )
              })}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-3">
          <div className="flex items-center space-x-2">
            <Checkbox
              id="timestamps"
              checked={includeTimestamps}
              onCheckedChange={(checked) => setIncludeTimestamps(checked as boolean)}
            />
            <label htmlFor="timestamps" className="text-sm">
              Include timestamps
            </label>
          </div>

          <div className="flex items-center space-x-2">
            <Checkbox
              id="metadata"
              checked={includeMetadata}
              onCheckedChange={(checked) => setIncludeMetadata(checked as boolean)}
            />
            <label htmlFor="metadata" className="text-sm">
              Include metadata (BPM, key, etc.)
            </label>
          </div>
        </div>

        {selectedFormat === "pdf" && (
          <div>
            <label className="text-sm font-medium mb-2 block">Font Size</label>
            <Select value={fontSize} onValueChange={setFontSize}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="10">10pt</SelectItem>
                <SelectItem value="12">12pt</SelectItem>
                <SelectItem value="14">14pt</SelectItem>
                <SelectItem value="16">16pt</SelectItem>
                <SelectItem value="18">18pt</SelectItem>
              </SelectContent>
            </Select>
          </div>
        )}

        <Button onClick={handleExport} disabled={!selectedFormat || isExporting} className="w-full">
          {isExporting ? (
            "Exporting..."
          ) : (
            <>
              <Download className="h-4 w-4 mr-2" />
              Export as {selectedFormat?.toUpperCase()}
            </>
          )}
        </Button>

        <div className="text-xs text-gray-500 space-y-1">
          <p>
            <strong>LRC:</strong> Standard karaoke format with precise timestamps
          </p>
          <p>
            <strong>SRT:</strong> Subtitle format compatible with video players
          </p>
          <p>
            <strong>TXT:</strong> Simple text format without timestamps
          </p>
          <p>
            <strong>PDF:</strong> Professional formatted document
          </p>
        </div>
      </CardContent>
    </Card>
  )
}
