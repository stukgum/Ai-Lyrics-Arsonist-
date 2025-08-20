"use client"

import { Upload, Music, AudioWaveformIcon as Waveform, FileText } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useRouter } from "next/navigation"

export default function HomePage() {
  const router = useRouter()

  const handleUploadClick = () => {
    router.push("/upload")
  }

  const handleGetStartedClick = () => {
    router.push("/upload")
  }

  const handleTrySampleClick = () => {
    // For now, redirect to upload page - could add sample functionality later
    router.push("/upload")
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 dark:from-gray-900 dark:to-gray-800">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm dark:bg-gray-900/80">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Music className="h-8 w-8 text-purple-600" />
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">BeatLyrics</h1>
            </div>
            <nav className="flex items-center space-x-4">
              <Button variant="ghost">Sign In</Button>
              <Button onClick={handleGetStartedClick}>Get Started</Button>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h2 className="text-5xl font-bold text-gray-900 dark:text-white mb-6">
            Generate Beat-Synced Lyrics
            <span className="text-purple-600"> Instantly</span>
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-3xl mx-auto">
            Upload your beats or audio files and let AI create perfectly timed lyrics that sync to every bar and beat.
            Export as LRC, SRT, PDF, or plain text.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" className="bg-purple-600 hover:bg-purple-700" onClick={handleUploadClick}>
              <Upload className="mr-2 h-5 w-5" />
              Upload Audio File
            </Button>
            <Button size="lg" variant="outline" onClick={handleTrySampleClick}>
              Try with Sample Beat
            </Button>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <Card>
            <CardHeader>
              <Waveform className="h-12 w-12 text-purple-600 mb-4" />
              <CardTitle>Audio Analysis</CardTitle>
              <CardDescription>
                Advanced beat detection, tempo analysis, and key estimation using state-of-the-art audio processing
              </CardDescription>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <Music className="h-12 w-12 text-blue-600 mb-4" />
              <CardTitle>AI Lyric Generation</CardTitle>
              <CardDescription>
                Generate high-quality lyrics that match your beat's structure, tempo, and mood using advanced AI
              </CardDescription>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <FileText className="h-12 w-12 text-green-600 mb-4" />
              <CardTitle>Multiple Export Formats</CardTitle>
              <CardDescription>
                Export your synced lyrics as LRC, SRT, TXT, or professional PDF with timestamps and formatting
              </CardDescription>
            </CardHeader>
          </Card>
        </div>

        {/* How It Works */}
        <div className="text-center">
          <h3 className="text-3xl font-bold text-gray-900 dark:text-white mb-12">How It Works</h3>
          <div className="grid md:grid-cols-4 gap-8">
            <div className="flex flex-col items-center">
              <div className="w-16 h-16 bg-purple-100 dark:bg-purple-900 rounded-full flex items-center justify-center mb-4">
                <span className="text-2xl font-bold text-purple-600">1</span>
              </div>
              <h4 className="font-semibold mb-2">Upload Audio</h4>
              <p className="text-gray-600 dark:text-gray-300 text-sm">
                Upload your beat or provide a YouTube/audio URL
              </p>
            </div>
            <div className="flex flex-col items-center">
              <div className="w-16 h-16 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center mb-4">
                <span className="text-2xl font-bold text-blue-600">2</span>
              </div>
              <h4 className="font-semibold mb-2">AI Analysis</h4>
              <p className="text-gray-600 dark:text-gray-300 text-sm">
                Our AI analyzes tempo, beats, bars, and musical structure
              </p>
            </div>
            <div className="flex flex-col items-center">
              <div className="w-16 h-16 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center mb-4">
                <span className="text-2xl font-bold text-green-600">3</span>
              </div>
              <h4 className="font-semibold mb-2">Generate Lyrics</h4>
              <p className="text-gray-600 dark:text-gray-300 text-sm">
                AI creates lyrics perfectly synced to your beat structure
              </p>
            </div>
            <div className="flex flex-col items-center">
              <div className="w-16 h-16 bg-orange-100 dark:bg-orange-900 rounded-full flex items-center justify-center mb-4">
                <span className="text-2xl font-bold text-orange-600">4</span>
              </div>
              <h4 className="font-semibold mb-2">Export & Use</h4>
              <p className="text-gray-600 dark:text-gray-300 text-sm">
                Download in your preferred format and start creating
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
