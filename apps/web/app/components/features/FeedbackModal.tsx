"use client";

import { useState } from "react";
import { X, MessageSquare } from "lucide-react";
import { Button } from "../ui/Button";
import clsx from "clsx";

type FeedbackReason = "too_hard" | "too_easy" | "not_interested" | "already_taken";

interface FeedbackModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (reason: FeedbackReason) => void;
  issueTitle?: string;
}

const REASONS: { value: FeedbackReason; label: string; description: string }[] = [
  { value: "too_hard", label: "Too hard", description: "The issue requires skills I don't have yet" },
  { value: "too_easy", label: "Too easy", description: "I'm looking for more challenging contributions" },
  { value: "not_interested", label: "Not interested", description: "The topic or domain doesn't interest me" },
  { value: "already_taken", label: "Already taken", description: "Someone else is already working on this" },
];

export function FeedbackModal({ isOpen, onClose, onSubmit, issueTitle }: FeedbackModalProps) {
  const [selected, setSelected] = useState<FeedbackReason | null>(null);

  if (!isOpen) return null;

  const handleSubmit = () => {
    if (selected) {
      onSubmit(selected);
      setSelected(null);
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative w-full max-w-md mx-4 rounded-xl border border-zinc-700 bg-zinc-900 shadow-2xl animate-fade-in">
        {/* Header */}
        <div className="flex items-center justify-between p-5 border-b border-zinc-800">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-zinc-800">
              <MessageSquare className="w-4 h-4 text-zinc-400" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-zinc-100">
                Why isn&apos;t this a good match?
              </h3>
              {issueTitle && (
                <p className="text-xs text-zinc-500 mt-0.5 truncate max-w-[280px]">
                  {issueTitle}
                </p>
              )}
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-zinc-500 hover:text-zinc-300 hover:bg-zinc-800 transition-colors"
            aria-label="Close"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Reasons */}
        <div className="p-5 space-y-2">
          {REASONS.map((reason) => (
            <button
              key={reason.value}
              onClick={() => setSelected(reason.value)}
              className={clsx(
                "w-full text-left p-3.5 rounded-lg border transition-all",
                selected === reason.value
                  ? "border-indigo-500 bg-indigo-500/10"
                  : "border-zinc-800 bg-zinc-800/50 hover:border-zinc-700 hover:bg-zinc-800"
              )}
            >
              <p
                className={clsx(
                  "text-sm font-medium",
                  selected === reason.value ? "text-indigo-300" : "text-zinc-200"
                )}
              >
                {reason.label}
              </p>
              <p className="text-xs text-zinc-500 mt-0.5">{reason.description}</p>
            </button>
          ))}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-2 p-5 pt-0">
          <Button variant="ghost" size="sm" onClick={onClose}>
            Cancel
          </Button>
          <Button
            variant="primary"
            size="sm"
            disabled={!selected}
            onClick={handleSubmit}
          >
            Submit Feedback
          </Button>
        </div>
      </div>
    </div>
  );
}
