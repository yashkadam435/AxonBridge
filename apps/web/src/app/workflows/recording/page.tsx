"use client";

import React, { useState } from 'react';
import { Mic, Square, Pause, Play, Save } from 'lucide-react';

export default function RecordingStudioPage() {
  const [isRecording, setIsRecording] = useState(false);
  const [steps, setSteps] = useState([
    { id: 1, action: "Navigate", detail: "ehospital.example.com/login", time: "00:01" },
    { id: 2, action: "Type", detail: "username field", time: "00:05" }
  ]);

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Workflow Recording Studio</h1>
          <p className="text-muted-foreground">Record manual HIS interactions to generate automation templates.</p>
        </div>
        <div className="flex gap-2">
          {!isRecording ? (
            <button 
              onClick={() => setIsRecording(true)}
              className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 bg-destructive text-destructive-foreground shadow-sm hover:bg-destructive/90 h-9 px-4 py-2">
              <Mic className="w-4 h-4 mr-2" /> Start Recording
            </button>
          ) : (
            <>
              <button className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 bg-secondary text-secondary-foreground shadow-sm hover:bg-secondary/80 h-9 px-4 py-2">
                <Pause className="w-4 h-4 mr-2" /> Pause
              </button>
              <button 
                onClick={() => setIsRecording(false)}
                className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 bg-primary text-primary-foreground shadow-sm hover:bg-primary/90 h-9 px-4 py-2">
                <Square className="w-4 h-4 mr-2" /> Stop & Save
              </button>
            </>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 border rounded-lg bg-card p-4 min-h-[500px] flex items-center justify-center relative overflow-hidden">
          {isRecording ? (
            <div className="absolute top-4 right-4 flex items-center gap-2 px-3 py-1 bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400 rounded-full text-sm font-medium animate-pulse">
              <span className="w-2 h-2 rounded-full bg-red-600 dark:bg-red-500"></span>
              Recording Live Session
            </div>
          ) : null}
          <div className="text-muted-foreground text-center space-y-2">
            <MonitorIcon />
            <p>Select an HIS target and click Start Recording to begin.</p>
          </div>
        </div>

        <div className="border rounded-lg bg-card">
          <div className="p-4 border-b font-semibold">Recorded Steps</div>
          <div className="p-0">
            {steps.length > 0 ? (
              <ul className="divide-y">
                {steps.map((step) => (
                  <li key={step.id} className="p-4 hover:bg-muted/30 transition-colors">
                    <div className="flex items-start justify-between">
                      <div>
                        <span className="font-semibold text-sm">{step.id}. {step.action}</span>
                        <p className="text-xs text-muted-foreground mt-1">{step.detail}</p>
                      </div>
                      <span className="text-xs font-mono text-muted-foreground">{step.time}</span>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="p-8 text-center text-muted-foreground text-sm">
                No steps recorded yet.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function MonitorIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round" className="mx-auto opacity-20">
      <rect width="20" height="14" x="2" y="3" rx="2" />
      <line x1="8" x2="16" y1="21" y2="21" />
      <line x1="12" x2="12" y1="17" y2="21" />
    </svg>
  );
}
