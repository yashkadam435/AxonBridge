"use client";

import React, { useState, useEffect } from 'react';
import { Monitor, Play, Pause, Square } from 'lucide-react';

interface Session {
  id: string;
  status: string;
  url: string;
  his_target: string;
  user: string;
  action_count: number;
}

export default function AgentsPage() {
  const [sessions, setSessions] = useState<Session[]>([]);

  useEffect(() => {
    // In a real app, this would fetch from /api/v1/agent/sessions
    // or connect via WebSocket to /ws/sessions
    setSessions([
      {
        id: "sess-001",
        status: "active",
        url: "https://ehospital.example.com/patients",
        his_target: "eHospital PROD",
        user: "Admin",
        action_count: 42
      }
    ]);
  }, []);

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Agent Sessions</h1>
          <p className="text-muted-foreground">Monitor and control active clinical automation agents.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {sessions.map(session => (
          <div key={session.id} className="border rounded-lg bg-card text-card-foreground shadow-sm">
            <div className="p-4 flex flex-col space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold flex items-center gap-2">
                  <Monitor className="w-4 h-4 text-primary" />
                  {session.his_target}
                </h3>
                <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
                  {session.status.toUpperCase()}
                </span>
              </div>
              
              <div className="aspect-video bg-muted rounded-md border overflow-hidden relative flex items-center justify-center">
                <span className="text-muted-foreground text-sm">Live Screenshot Feed</span>
              </div>

              <div className="text-sm space-y-1">
                <p><span className="font-medium">URL:</span> {session.url}</p>
                <p><span className="font-medium">Supervisor:</span> {session.user}</p>
                <p><span className="font-medium">Actions Executed:</span> {session.action_count}</p>
              </div>

              <div className="flex gap-2 pt-2">
                <button className="flex-1 inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 bg-secondary text-secondary-foreground shadow-sm hover:bg-secondary/80 h-9 px-4 py-2">
                  <Pause className="w-4 h-4 mr-2" /> Pause
                </button>
                <button className="flex-1 inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 bg-destructive text-destructive-foreground shadow-sm hover:bg-destructive/90 h-9 px-4 py-2">
                  <Square className="w-4 h-4 mr-2" /> Terminate
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
