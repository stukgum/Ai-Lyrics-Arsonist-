"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Clock, CheckCircle, XCircle, RefreshCw, Music, BarChart3 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"

interface JobStatus {
  job_id: string
  status: "pending" | "processing" | "completed" | "failed"
  progress: number
  message: string
  created_at: string
  updated_at: string
}

interface AudioFeatures {
  duration: number
  bpm: number
  key: string
  tempo_confidence: number
  beats: Array<{ timestamp: number; confidence: number }>
  bars: Array<{ start: number; end: number; beat_count: number }>
  sections: Array<{ name: string; start: number; end: number }>
}

export default function JobStatusPage({ params }: { params: { id: string } }) {
  const router = useRouter()
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null)
  const [audioFeatures, setAudioFeatures] = useState<AudioFeatures | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchJobStatus = async () => {
    try {
      const response = await fetch(`/api/v1/jobs/${params.id}/status`)
      if (!response.ok) {
        throw new Error("Failed to fetch job status")
      }
      const data = await response.json()
      setJobStatus(data)

      // If completed, fetch features
      if (data.status === "completed") {
        const featuresResponse = await fetch(`/api/v1/jobs/${params.id}/features`)
        if (featuresResponse.ok) {
          const featuresData = await response.json()
          setAudioFeatures(featuresData)
        }
      }
    } catch (err) {
      setError("Failed to load job status")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchJobStatus()

    // Poll for updates if job is not completed
    const interval = setInterval(() => {
      if (jobStatus?.status === "pending" || jobStatus?.status === "processing") {
        fetchJobStatus()
      }
    }, 2000)

    return () => clearInterval(interval)
  }, [params.id, jobStatus?.status])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "pending":
        return <Clock className="h-5 w-5 text-yellow-500" />
      case "processing":
        return <RefreshCw className="h-5 w-5 text-blue-500 animate-spin" />
      case "completed":
        return <CheckCircle className="h-5 w-5 text-green-500" />
      case "failed":
        return <XCircle className="h-5 w-5 text-red-500" />
      default:
        return <Clock className="h-5 w-5 text-gray-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "pending":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200"
      case "processing":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
      case "completed":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
      case "failed":
        return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200"
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p>Loading job status...</p>
        </div>
      </div>
    )
  }

  if (error || !jobStatus) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center">
        <Alert variant="destructive" className="max-w-md">
          <XCircle className="h-4 w-4" />
          <AlertDescription>{error || "Job not found"}</AlertDescription>
        </Alert>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto space-y-6">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">Audio Processing Status</h1>
            <p className="text-gray-600 dark:text-gray-300">Job ID: {params.id}</p>
          </div>

          {/* Status Card */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                {getStatusIcon(jobStatus.status)}
                Processing Status
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <Badge className={getStatusColor(jobStatus.status)}>{jobStatus.status.toUpperCase()}</Badge>
                <span className="text-sm text-gray-500">{Math.round(jobStatus.progress * 100)}% complete</span>
              </div>

              <Progress value={jobStatus.progress * 100} className="w-full" />

              <p className="text-sm text-gray-600 dark:text-gray-300">{jobStatus.message}</p>

              <div className="text-xs text-gray-500 space-y-1">
                <div>Created: {new Date(jobStatus.created_at).toLocaleString()}</div>
                <div>Updated: {new Date(jobStatus.updated_at).toLocaleString()}</div>
              </div>
            </CardContent>
          </Card>

          {/* Audio Features */}
          {audioFeatures && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  Audio Analysis Results
                </CardTitle>
                <CardDescription>Extracted musical features from your audio</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <div className="text-center p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <div className="text-2xl font-bold text-purple-600">{Math.round(audioFeatures.bpm)}</div>
                    <div className="text-sm text-gray-600 dark:text-gray-300">BPM</div>
                  </div>
                  <div className="text-center p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">{audioFeatures.key}</div>
                    <div className="text-sm text-gray-600 dark:text-gray-300">Key</div>
                  </div>
                  <div className="text-center p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">{Math.round(audioFeatures.duration)}s</div>
                    <div className="text-sm text-gray-600 dark:text-gray-300">Duration</div>
                  </div>
                  <div className="text-center p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <div className="text-2xl font-bold text-orange-600">{audioFeatures.bars.length}</div>
                    <div className="text-sm text-gray-600 dark:text-gray-300">Bars</div>
                  </div>
                </div>

                {audioFeatures.sections.length > 0 && (
                  <div className="mt-6">
                    <h4 className="font-medium mb-3">Detected Sections</h4>
                    <div className="flex flex-wrap gap-2">
                      {audioFeatures.sections.map((section, index) => (
                        <Badge key={index} variant="outline">
                          {section.name} ({Math.round(section.start)}s - {Math.round(section.end)}s)
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Actions */}
          <div className="flex gap-4 justify-center">
            <Button variant="outline" onClick={() => router.push("/upload")}>
              Upload Another File
            </Button>

            {jobStatus.status === "completed" && (
              <Button onClick={() => router.push(`/generate/${params.id}`)}>
                <Music className="mr-2 h-4 w-4" />
                Generate Lyrics
              </Button>
            )}

            <Button variant="outline" onClick={fetchJobStatus}>
              <RefreshCw className="mr-2 h-4 w-4" />
              Refresh
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
