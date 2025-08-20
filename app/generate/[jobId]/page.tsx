"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Music, Settings, Sparkles, RefreshCw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Slider } from "@/components/ui/slider"
import { Switch } from "@/components/ui/switch"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription } from "@/components/ui/alert"

interface GenerationRequest {
  job_id: string
  genre: string
  mood: string
  explicit: boolean
  language: string
  rhyme_scheme: string
  syllables_per_beat: number
}

export default function GeneratePage({ params }: { params: { jobId: string } }) {
  const router = useRouter()
  const [isGenerating, setIsGenerating] = useState(false)
  const [generationProgress, setGenerationProgress] = useState(0)
  const [error, setError] = useState<string | null>(null)

  // Generation parameters
  const [genre, setGenre] = useState("hip-hop")
  const [mood, setMood] = useState("energetic")
  const [explicit, setExplicit] = useState(false)
  const [language, setLanguage] = useState("en")
  const [rhymeScheme, setRhymeScheme] = useState("AABB")
  const [syllablesPerBeat, setSyllablesPerBeat] = useState([1.4])

  const genres = [
    { value: "hip-hop", label: "Hip-Hop" },
    { value: "trap", label: "Trap" },
    { value: "pop", label: "Pop" },
    { value: "rock", label: "Rock" },
    { value: "country", label: "Country" },
    { value: "r&b", label: "R&B" },
    { value: "electronic", label: "Electronic" },
    { value: "jazz", label: "Jazz" },
  ]

  const moods = [
    { value: "energetic", label: "Energetic" },
    { value: "introspective", label: "Introspective" },
    { value: "uplifting", label: "Uplifting" },
    { value: "melancholic", label: "Melancholic" },
    { value: "aggressive", label: "Aggressive" },
    { value: "romantic", label: "Romantic" },
    { value: "nostalgic", label: "Nostalgic" },
    { value: "confident", label: "Confident" },
  ]

  const rhymeSchemes = [
    { value: "AABB", label: "AABB (Couplets)" },
    { value: "ABAB", label: "ABAB (Alternating)" },
    { value: "ABCB", label: "ABCB (Ballad)" },
    { value: "AAAA", label: "AAAA (Monorhyme)" },
    { value: "ABCC", label: "ABCC (Triplet)" },
  ]

  const applyPreset = (presetType: string) => {
    switch (presetType) {
      case "rap":
        setGenre("trap")
        setMood("introspective")
        setRhymeScheme("AABB")
        setSyllablesPerBeat([1.6])
        break
      case "pop":
        setGenre("pop")
        setMood("uplifting")
        setRhymeScheme("ABAB")
        setSyllablesPerBeat([1.0])
        break
      case "country":
        setGenre("country")
        setMood("nostalgic")
        setRhymeScheme("AABB")
        setSyllablesPerBeat([1.1])
        break
    }
  }

  const handleGenerate = async () => {
    setIsGenerating(true)
    setError(null)
    setGenerationProgress(0)

    const request: GenerationRequest = {
      job_id: params.jobId,
      genre,
      mood,
      explicit,
      language,
      rhyme_scheme: rhymeScheme,
      syllables_per_beat: syllablesPerBeat[0],
    }

    try {
      const response = await fetch("/api/v1/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
      })

      if (!response.ok) {
        throw new Error("Generation failed")
      }

      const result = await response.json()

      // Redirect to editor with generation ID
      router.push(`/editor/${result.generation_id}`)
    } catch (err) {
      setError("Failed to generate lyrics. Please try again.")
    } finally {
      setIsGenerating(false)
      setGenerationProgress(0)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto space-y-6">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">Generate Lyrics</h1>
            <p className="text-gray-600 dark:text-gray-300">Configure your lyric generation parameters</p>
          </div>

          {/* Preset Buttons */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="h-5 w-5" />
                Quick Presets
              </CardTitle>
              <CardDescription>Apply genre-specific settings with one click</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-3 gap-4">
                <Button
                  variant="outline"
                  onClick={() => applyPreset("rap")}
                  className="h-auto p-4 flex flex-col items-center gap-2"
                >
                  <div className="font-medium">Rap/Trap</div>
                  <div className="text-xs text-gray-500">Introspective • AABB • 1.6 syl/beat</div>
                </Button>
                <Button
                  variant="outline"
                  onClick={() => applyPreset("pop")}
                  className="h-auto p-4 flex flex-col items-center gap-2"
                >
                  <div className="font-medium">Pop</div>
                  <div className="text-xs text-gray-500">Uplifting • ABAB • 1.0 syl/beat</div>
                </Button>
                <Button
                  variant="outline"
                  onClick={() => applyPreset("country")}
                  className="h-auto p-4 flex flex-col items-center gap-2"
                >
                  <div className="font-medium">Country</div>
                  <div className="text-xs text-gray-500">Nostalgic • AABB • 1.1 syl/beat</div>
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Generation Settings */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                Generation Settings
              </CardTitle>
              <CardDescription>Customize the style and structure of your lyrics</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="genre">Genre</Label>
                  <Select value={genre} onValueChange={setGenre}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {genres.map((g) => (
                        <SelectItem key={g.value} value={g.value}>
                          {g.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="mood">Mood</Label>
                  <Select value={mood} onValueChange={setMood}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {moods.map((m) => (
                        <SelectItem key={m.value} value={m.value}>
                          {m.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="rhyme">Rhyme Scheme</Label>
                  <Select value={rhymeScheme} onValueChange={setRhymeScheme}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {rhymeSchemes.map((r) => (
                        <SelectItem key={r.value} value={r.value}>
                          {r.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="language">Language</Label>
                  <Select value={language} onValueChange={setLanguage}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="en">English</SelectItem>
                      <SelectItem value="es">Spanish</SelectItem>
                      <SelectItem value="fr">French</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label>Syllables per Beat: {syllablesPerBeat[0]}</Label>
                <Slider
                  value={syllablesPerBeat}
                  onValueChange={setSyllablesPerBeat}
                  max={3}
                  min={0.5}
                  step={0.1}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500">
                  <span>Sparse (0.5)</span>
                  <span>Dense (3.0)</span>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <Switch id="explicit" checked={explicit} onCheckedChange={setExplicit} />
                <Label htmlFor="explicit">Allow explicit content</Label>
              </div>
            </CardContent>
          </Card>

          {/* Generation Progress */}
          {isGenerating && (
            <Card>
              <CardContent className="pt-6">
                <div className="text-center space-y-4">
                  <RefreshCw className="h-8 w-8 animate-spin mx-auto text-purple-600" />
                  <div>
                    <h3 className="font-medium">Generating Lyrics...</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-300">This may take 30-60 seconds</p>
                  </div>
                  <Progress value={generationProgress} className="w-full" />
                </div>
              </CardContent>
            </Card>
          )}

          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Generate Button */}
          <div className="text-center">
            <Button
              onClick={handleGenerate}
              disabled={isGenerating}
              size="lg"
              className="bg-purple-600 hover:bg-purple-700"
            >
              <Music className="mr-2 h-5 w-5" />
              {isGenerating ? "Generating..." : "Generate Lyrics"}
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
