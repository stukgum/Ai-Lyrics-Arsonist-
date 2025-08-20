"use client"

import { useState } from "react"
import { AlertTriangle, ExternalLink } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Checkbox } from "@/components/ui/checkbox"
import { Alert, AlertDescription } from "@/components/ui/alert"

interface RightsConfirmationModalProps {
  isOpen: boolean
  onClose: () => void
  onConfirm: (confirmed: boolean, metadataOnly?: boolean) => void
  url: string
}

export function RightsConfirmationModal({ isOpen, onClose, onConfirm, url }: RightsConfirmationModalProps) {
  const [hasRights, setHasRights] = useState(false)
  const [understands, setUnderstands] = useState(false)

  const handleConfirm = () => {
    onConfirm(hasRights && understands)
  }

  const handleMetadataOnly = () => {
    onConfirm(false, true)
  }

  const isYouTube = url.includes("youtube.com") || url.includes("youtu.be")

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-amber-500" />
            Rights Confirmation Required
          </DialogTitle>
          <DialogDescription>
            Before processing audio from this URL, we need to confirm your rights to use this content.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <Alert>
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              <strong>Important:</strong> You must have the legal right to download and process this audio content. This
              includes owning the content, having explicit permission from the copyright holder, or the content being in
              the public domain.
            </AlertDescription>
          </Alert>

          <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
            <h4 className="font-medium mb-2">URL to process:</h4>
            <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300">
              <ExternalLink className="h-4 w-4" />
              <span className="break-all">{url}</span>
            </div>
          </div>

          {isYouTube && (
            <Alert>
              <AlertDescription>
                <strong>YouTube Content:</strong> Most YouTube videos are copyrighted. Only proceed if you own the
                content, have explicit permission, or the video is marked as Creative Commons or public domain.
              </AlertDescription>
            </Alert>
          )}

          <div className="space-y-3">
            <div className="flex items-start space-x-2">
              <Checkbox
                id="rights"
                checked={hasRights}
                onCheckedChange={(checked) => setHasRights(checked as boolean)}
              />
              <label htmlFor="rights" className="text-sm leading-relaxed">
                I confirm that I have the legal right to download and process this audio content for lyric generation
                purposes. I understand that I am responsible for ensuring compliance with copyright laws.
              </label>
            </div>

            <div className="flex items-start space-x-2">
              <Checkbox
                id="understands"
                checked={understands}
                onCheckedChange={(checked) => setUnderstands(checked as boolean)}
              />
              <label htmlFor="understands" className="text-sm leading-relaxed">
                I understand that BeatLyrics will download and process this audio file, and I accept full responsibility
                for any copyright implications.
              </label>
            </div>
          </div>
        </div>

        <DialogFooter className="flex-col sm:flex-row gap-2">
          <div className="flex gap-2 w-full sm:w-auto">
            <Button variant="outline" onClick={onClose} className="flex-1 sm:flex-none bg-transparent">
              Cancel
            </Button>
            <Button variant="secondary" onClick={handleMetadataOnly} className="flex-1 sm:flex-none">
              Metadata Only
            </Button>
          </div>
          <Button onClick={handleConfirm} disabled={!hasRights || !understands} className="w-full sm:w-auto">
            Confirm & Download
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
