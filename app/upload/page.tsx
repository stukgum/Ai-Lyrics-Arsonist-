"use client"

import type React from "react"

import { useState, useCallback } from "react"
import { useRouter } from "next/navigation"
import { useDropzone } from "react-dropzone"
import { Upload, Link, Music, AlertCircle, CheckCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { RightsConfirmationModal } from "@/components/rights-confirmation-modal"

export default function UploadPage() {
  const router = useRouter()
  const [uploadProgress, setUploadProgress] = useState(0)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null)
  const [url, setUrl] = useState("")
  const [showRightsModal, setShowRightsModal] = useState(false)
  const [pendingUrl, setPendingUrl] = useState("")

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      const file = acceptedFiles[0]
      if (!file) return

      // Validate file type
      const allowedTypes = ["audio/wav", "audio/mpeg", "audio/mp4", "audio/aac", "audio/ogg", "audio/flac"]
      if (!allowedTypes.includes(file.type)) {
        setUploadError("Unsupported file format. Please use WAV, MP3, M4A, AAC, OGG, or FLAC.")
        return
      }

      // Validate file size (200MB)
      if (file.size > 200 * 1024 * 1024) {
        setUploadError("File too large. Maximum size is 200MB.")
        return
      }

      setIsUploading(true)
      setUploadError(null)
      setUploadProgress(0)

      try {
        const formData = new FormData()
        formData.append("file", file)

        const response = await fetch("/api/v1/upload", {
          method: "POST",
          body: formData,
        })

        if (!response.ok) {
          throw new Error("Upload failed")
        }

        const result = await response.json()
        setUploadSuccess(`File uploaded successfully! Job ID: ${result.job_id}`)

        // Redirect to job status page
        setTimeout(() => {
          router.push(`/job/${result.job_id}`)
        }, 2000)
      } catch (error) {
        setUploadError("Upload failed. Please try again.")
      } finally {
        setIsUploading(false)
        setUploadProgress(0)
      }
    },
    [router],
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "audio/*": [".wav", ".mp3", ".m4a", ".aac", ".ogg", ".flac"],
    },
    maxFiles: 1,
    disabled: isUploading,
  })

  const handleUrlSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!url.trim()) return

    setPendingUrl(url)
    setShowRightsModal(true)
  }

  const handleRightsConfirmation = async (confirmed: boolean, metadataOnly = false) => {
    setShowRightsModal(false)

    if (!confirmed && !metadataOnly) {
      setPendingUrl("")
      return
    }

    setIsUploading(true)
    setUploadError(null)

    try {
      const response = await fetch("/api/v1/ingest-url", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          url: pendingUrl,
          confirm_rights: confirmed,
          metadata_only: metadataOnly,
        }),
      })

      if (!response.ok) {
        throw new Error("URL processing failed")
      }

      const result = await response.json()
      setUploadSuccess(`URL processing started! Job ID: ${result.job_id}`)

      // Redirect to job status page
      setTimeout(() => {
        router.push(`/job/${result.job_id}`)
      }, 2000)
    } catch (error) {
      setUploadError("URL processing failed. Please try again.")
    } finally {
      setIsUploading(false)
      setPendingUrl("")
      setUrl("")
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">Upload Your Audio</h1>
            <p className="text-xl text-gray-600 dark:text-gray-300">
              Upload an audio file or provide a URL to get started with AI lyric generation
            </p>
          </div>

          <Tabs defaultValue="upload" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="upload">Upload File</TabsTrigger>
              <TabsTrigger value="url">From URL</TabsTrigger>
            </TabsList>

            <TabsContent value="upload" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Upload className="h-5 w-5" />
                    Upload Audio File
                  </CardTitle>
                  <CardDescription>Supported formats: WAV, MP3, M4A, AAC, OGG, FLAC (max 200MB)</CardDescription>
                </CardHeader>
                <CardContent>
                  <div
                    {...getRootProps()}
                    className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                      isDragActive
                        ? "border-purple-500 bg-purple-50 dark:bg-purple-900/20"
                        : "border-gray-300 dark:border-gray-600 hover:border-purple-400"
                    } ${isUploading ? "pointer-events-none opacity-50" : ""}`}
                  >
                    <input {...getInputProps()} />
                    <Music className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    {isDragActive ? (
                      <p className="text-lg text-purple-600 dark:text-purple-400">Drop your audio file here...</p>
                    ) : (
                      <div>
                        <p className="text-lg text-gray-600 dark:text-gray-300 mb-2">
                          Drag and drop your audio file here, or click to browse
                        </p>
                        <Button variant="outline" disabled={isUploading}>
                          Choose File
                        </Button>
                      </div>
                    )}
                  </div>

                  {isUploading && (
                    <div className="mt-4">
                      <Progress value={uploadProgress} className="w-full" />
                      <p className="text-sm text-gray-600 dark:text-gray-300 mt-2">Uploading... {uploadProgress}%</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="url" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Link className="h-5 w-5" />
                    Process from URL
                  </CardTitle>
                  <CardDescription>Provide a YouTube URL or direct audio link</CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleUrlSubmit} className="space-y-4">
                    <div>
                      <Label htmlFor="url">Audio URL</Label>
                      <Input
                        id="url"
                        type="url"
                        placeholder="https://www.youtube.com/watch?v=..."
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        disabled={isUploading}
                      />
                    </div>
                    <Button type="submit" disabled={isUploading || !url.trim()}>
                      Process URL
                    </Button>
                  </form>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>

          {uploadError && (
            <Alert variant="destructive" className="mt-6">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{uploadError}</AlertDescription>
            </Alert>
          )}

          {uploadSuccess && (
            <Alert className="mt-6">
              <CheckCircle className="h-4 w-4" />
              <AlertDescription>{uploadSuccess}</AlertDescription>
            </Alert>
          )}

          {/* Sample Files */}
          <Card className="mt-8">
            <CardHeader>
              <CardTitle>Try with Sample Beats</CardTitle>
              <CardDescription>Test the system with our sample audio files</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-3 gap-4">
                <Button variant="outline" className="h-auto p-4 flex flex-col items-center gap-2 bg-transparent">
                  <Music className="h-6 w-6" />
                  <div className="text-center">
                    <div className="font-medium">Hip-Hop Beat</div>
                    <div className="text-sm text-gray-500">120 BPM • 4/4</div>
                  </div>
                </Button>
                <Button variant="outline" className="h-auto p-4 flex flex-col items-center gap-2 bg-transparent">
                  <Music className="h-6 w-6" />
                  <div className="text-center">
                    <div className="font-medium">Pop Track</div>
                    <div className="text-sm text-gray-500">128 BPM • 4/4</div>
                  </div>
                </Button>
                <Button variant="outline" className="h-auto p-4 flex flex-col items-center gap-2 bg-transparent">
                  <Music className="h-6 w-6" />
                  <div className="text-center">
                    <div className="font-medium">Country Song</div>
                    <div className="text-sm text-gray-500">100 BPM • 4/4</div>
                  </div>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <RightsConfirmationModal
        isOpen={showRightsModal}
        onClose={() => setShowRightsModal(false)}
        onConfirm={handleRightsConfirmation}
        url={pendingUrl}
      />
    </div>
  )
}
