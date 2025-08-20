"use client"

import { useEffect, useRef, useState } from "react"
import WaveSurfer from "wavesurfer.js"
import RegionsPlugin from "wavesurfer.js/dist/plugins/regions.esm.js"
import { Play, Pause, SkipBack, SkipForward, Volume2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Slider } from "@/components/ui/slider"
import { Card, CardContent } from "@/components/ui/card"

interface WaveformEditorProps {
  audioUrl: string
  beats: Array<{ timestamp: number; confidence: number }>
  bars: Array<{ start: number; end: number; beat_count: number }>
  sections: Array<{ name: string; start: number; end: number }>
  onRegionSelect?: (start: number, end: number) => void
}

export function WaveformEditor({ audioUrl, beats, bars, sections, onRegionSelect }: WaveformEditorProps) {
  const waveformRef = useRef<HTMLDivElement>(null)
  const wavesurfer = useRef<WaveSurfer | null>(null)
  const regionsPlugin = useRef<any>(null)

  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [volume, setVolume] = useState([0.5])

  useEffect(() => {
    if (!waveformRef.current) return

    // Initialize regions plugin
    regionsPlugin.current = RegionsPlugin.create()

    // Initialize WaveSurfer
    wavesurfer.current = WaveSurfer.create({
      container: waveformRef.current,
      waveColor: "#8b5cf6",
      progressColor: "#7c3aed",
      cursorColor: "#6d28d9",
      barWidth: 2,
      barRadius: 1,
      responsive: true,
      height: 100,
      normalize: true,
      plugins: [regionsPlugin.current],
    })

    // Load audio
    wavesurfer.current.load(audioUrl)

    // Event listeners
    wavesurfer.current.on("ready", () => {
      setDuration(wavesurfer.current!.getDuration())
      addBeatMarkers()
      addBarRegions()
      addSectionMarkers()
    })

    wavesurfer.current.on("play", () => setIsPlaying(true))
    wavesurfer.current.on("pause", () => setIsPlaying(false))
    wavesurfer.current.on("timeupdate", (time) => setCurrentTime(time))

    // Region selection
    regionsPlugin.current.on("region-clicked", (region: any) => {
      if (onRegionSelect) {
        onRegionSelect(region.start, region.end)
      }
    })

    return () => {
      if (wavesurfer.current) {
        wavesurfer.current.destroy()
      }
    }
  }, [audioUrl])

  const addBeatMarkers = () => {
    if (!wavesurfer.current) return

    beats.forEach((beat, index) => {
      const marker = document.createElement("div")
      marker.style.position = "absolute"
      marker.style.top = "0"
      marker.style.bottom = "0"
      marker.style.width = "1px"
      marker.style.backgroundColor = "rgba(139, 92, 246, 0.3)"
      marker.style.left = `${(beat.timestamp / duration) * 100}%`
      marker.style.pointerEvents = "none"

      waveformRef.current?.appendChild(marker)
    })
  }

  const addBarRegions = () => {
    if (!regionsPlugin.current) return

    bars.forEach((bar, index) => {
      regionsPlugin.current.addRegion({
        start: bar.start,
        end: bar.end,
        color: "rgba(59, 130, 246, 0.1)",
        drag: false,
        resize: false,
        id: `bar-${index}`,
      })
    })
  }

  const addSectionMarkers = () => {
    if (!regionsPlugin.current) return

    const colors = {
      intro: "rgba(34, 197, 94, 0.2)",
      verse: "rgba(59, 130, 246, 0.2)",
      chorus: "rgba(239, 68, 68, 0.2)",
      bridge: "rgba(245, 158, 11, 0.2)",
      outro: "rgba(107, 114, 128, 0.2)",
    }

    sections.forEach((section, index) => {
      regionsPlugin.current.addRegion({
        start: section.start,
        end: section.end,
        color: colors[section.name as keyof typeof colors] || "rgba(139, 92, 246, 0.2)",
        drag: false,
        resize: false,
        id: `section-${index}`,
        content: section.name.toUpperCase(),
      })
    })
  }

  const togglePlayPause = () => {
    if (!wavesurfer.current) return
    wavesurfer.current.playPause()
  }

  const skipBackward = () => {
    if (!wavesurfer.current) return
    const newTime = Math.max(0, currentTime - 5)
    wavesurfer.current.seekTo(newTime / duration)
  }

  const skipForward = () => {
    if (!wavesurfer.current) return
    const newTime = Math.min(duration, currentTime + 5)
    wavesurfer.current.seekTo(newTime / duration)
  }

  const handleVolumeChange = (value: number[]) => {
    setVolume(value)
    if (wavesurfer.current) {
      wavesurfer.current.setVolume(value[0])
    }
  }

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60)
    const seconds = Math.floor(time % 60)
    return `${minutes}:${seconds.toString().padStart(2, "0")}`
  }

  return (
    <Card>
      <CardContent className="p-6">
        <div className="space-y-4">
          {/* Waveform */}
          <div className="relative">
            <div ref={waveformRef} className="w-full" />
            <div className="absolute top-0 left-0 right-0 h-full pointer-events-none">
              {/* Beat markers will be added here */}
            </div>
          </div>

          {/* Controls */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" onClick={skipBackward} disabled={!wavesurfer.current}>
                <SkipBack className="h-4 w-4" />
              </Button>

              <Button variant="outline" size="sm" onClick={togglePlayPause} disabled={!wavesurfer.current}>
                {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
              </Button>

              <Button variant="outline" size="sm" onClick={skipForward} disabled={!wavesurfer.current}>
                <SkipForward className="h-4 w-4" />
              </Button>
            </div>

            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-600 dark:text-gray-300">
                {formatTime(currentTime)} / {formatTime(duration)}
              </span>

              <div className="flex items-center gap-2">
                <Volume2 className="h-4 w-4" />
                <Slider value={volume} onValueChange={handleVolumeChange} max={1} min={0} step={0.1} className="w-20" />
              </div>
            </div>
          </div>

          {/* Legend */}
          <div className="flex flex-wrap gap-4 text-xs">
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 bg-purple-300 rounded"></div>
              <span>Beats</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 bg-blue-200 rounded"></div>
              <span>Bars</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 bg-green-200 rounded"></div>
              <span>Intro</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 bg-blue-200 rounded"></div>
              <span>Verse</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 bg-red-200 rounded"></div>
              <span>Chorus</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 bg-yellow-200 rounded"></div>
              <span>Bridge</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
