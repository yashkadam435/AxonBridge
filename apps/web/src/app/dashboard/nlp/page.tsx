"use client";

import React, { useState } from 'react';
import VoiceInput from '@/components/VoiceInput';
import SOAPNoteViewer from '@/components/SOAPNoteViewer';
import { AlertTriangle, Sparkles, Bot, Stethoscope } from 'lucide-react';

export default function NLPStudioPage() {
  const [soapData, setSoapData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleTranscriptComplete = async (transcript: string) => {
    setIsLoading(true);
    setError('');
    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';
      const response = await fetch(`${baseUrl}/api/v1/clinical/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ transcript })
      });
      
      if (!response.ok) {
        throw new Error(`Failed to generate clinical logic: ${response.statusText}`);
      }
      
      const data = await response.json();
      setSoapData(data);
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'An error occurred connecting to the LLM engine.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans selection:bg-blue-200">
      <div className="max-w-7xl mx-auto px-6 py-12 space-y-12">
        
        {/* Header Section */}
        <div className="flex flex-col items-center text-center space-y-4">
          <div className="inline-flex items-center justify-center p-4 bg-blue-100 rounded-2xl shadow-sm border border-blue-200/50 mb-2">
            <Stethoscope className="w-10 h-10 text-blue-600" />
          </div>
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-slate-900 flex items-center justify-center gap-3">
            Clinical Logic Engine
            <Sparkles className="w-6 h-6 text-blue-500 animate-pulse" />
          </h1>
          <p className="text-slate-500 text-lg md:text-xl font-light tracking-wide max-w-2xl mx-auto">
            AI-powered voice dictation. Speak naturally to generate structured SOAP notes instantly.
          </p>
        </div>
        
        {error && (
          <div className="p-5 bg-red-50 text-red-700 rounded-2xl flex items-center gap-4 border border-red-200 shadow-sm animate-shake">
            <AlertTriangle className="w-6 h-6 flex-shrink-0 text-red-500" />
            <p className="font-medium text-lg">{error}</p>
          </div>
        )}

        {/* Main Content: Vertical Stack */}
        <div className="flex flex-col gap-10">
          
          {/* Top: Voice Input spanning full width */}
          <div className="w-full">
            <VoiceInput onTranscriptComplete={handleTranscriptComplete} isLoading={isLoading} />
          </div>
          
          {/* Bottom: SOAP Notes & Extracted Variables */}
          <div className="w-full space-y-10 animate-fadeInUp">
            
            {/* Extracted Variables Panel (only if data exists) */}
            {soapData?.extracted_parameters && (
              <div className="p-8 border border-slate-200 rounded-3xl bg-white shadow-xl shadow-slate-200/50">
                <h3 className="text-xl font-bold mb-6 flex items-center gap-3 text-slate-800">
                  <div className="p-2 bg-indigo-100 rounded-lg">
                    <Bot className="w-6 h-6 text-indigo-600" />
                  </div>
                  Extracted Automation Variables
                </h3>
                <div className="bg-slate-50 p-6 rounded-2xl border border-slate-100 overflow-auto max-h-[300px] custom-scrollbar shadow-inner">
                  <pre className="text-sm font-mono text-slate-700 leading-relaxed">
                    {JSON.stringify(soapData.extracted_parameters, null, 2)}
                  </pre>
                </div>
              </div>
            )}

            {/* SOAP Note Viewer */}
            <div className="w-full">
              <SOAPNoteViewer 
                subjective={soapData?.subjective || "Awaiting input..."}
                objective={soapData?.objective || ""}
                assessment={soapData?.assessment || ""}
                plan={soapData?.plan || ""}
              />
            </div>
            
          </div>
        </div>
      </div>
    </div>
  );
}
