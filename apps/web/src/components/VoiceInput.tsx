"use client";

import React, { useState, useEffect, useRef } from 'react';
import { Mic, Square, Globe, Activity, ChevronDown, Check } from 'lucide-react';

interface VoiceInputProps {
  onTranscriptComplete?: (transcript: string) => void;
  isLoading?: boolean;
}

const SUPPORTED_LANGUAGES = [
  { code: 'en-US', label: 'English (US)' },
  { code: 'hi-IN', label: 'Hindi (India)' },
  { code: 'es-ES', label: 'Spanish' },
  { code: 'fr-FR', label: 'French' },
  { code: 'ar-SA', label: 'Arabic' },
  { code: 'zh-CN', label: 'Chinese (Mandarin)' },
  { code: 'ta-IN', label: 'Tamil' },
  { code: 'te-IN', label: 'Telugu' },
];

export default function VoiceInput({ onTranscriptComplete, isLoading = false }: VoiceInputProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [language, setLanguage] = useState('en-US');
  const [isLangMenuOpen, setIsLangMenuOpen] = useState(false);
  
  const recognitionRef = useRef<any>(null);
  const transcriptRef = useRef('');
  
  const initSpeechRecognition = (langCode: string) => {
    if (typeof window !== 'undefined' && ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window)) {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = langCode;
      
      recognition.onresult = (event: any) => {
        let currentTranscript = '';
        for (let i = 0; i < event.results.length; i++) {
          currentTranscript += event.results[i][0].transcript + ' ';
        }
        setTranscript(currentTranscript);
        transcriptRef.current = currentTranscript;
      };

      recognition.onerror = (event: any) => {
        console.error('Speech recognition error', event.error);
        setIsRecording(false);
      };

      recognitionRef.current = recognition;
    }
  };

  useEffect(() => {
    initSpeechRecognition(language);

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.code === 'Space' && e.ctrlKey) {
        // Prevent default scrolling
        e.preventDefault();
        setIsRecording(prev => {
          if (!prev) {
            handleStart();
            return true;
          } else {
            handleStop(transcriptRef.current);
            return false;
          }
        });
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [language]);

  const handleStart = () => {
    setIsRecording(true);
    setTranscript('');
    transcriptRef.current = '';
    if (recognitionRef.current) {
      try {
        recognitionRef.current.start();
      } catch (e) {
        console.error(e);
      }
    } else {
      setTranscript('Speech recognition not supported in this browser.');
    }
  };

  const handleStop = (currentText: string = transcriptRef.current) => {
    setIsRecording(false);
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    
    if (onTranscriptComplete && currentText) {
      onTranscriptComplete(currentText);
    }
  };

  const currentLangLabel = SUPPORTED_LANGUAGES.find(l => l.code === language)?.label;

  return (
    <div className="w-full flex flex-col items-center justify-center p-12 md:p-16 border border-slate-200/60 rounded-[2.5rem] bg-white shadow-[0_8px_30px_rgb(0,0,0,0.04)] relative">
      
      {/* Recording Pulse Background */}
      {isRecording && <div className="absolute inset-0 bg-red-50/50 animate-pulse pointer-events-none rounded-[2.5rem]" />}
      
      {/* Microphone Button Container */}
      <div className="relative z-10 mb-8 mt-4 flex justify-center items-center">
        {/* Decorative subtle animated rings */}
        {!isRecording && (
          <>
            <div className="absolute w-32 h-32 bg-blue-100/50 rounded-full animate-ping" style={{ animationDuration: '3s' }}></div>
            <div className="absolute w-40 h-40 bg-blue-50/50 rounded-full animate-pulse" style={{ animationDuration: '4s' }}></div>
          </>
        )}
        
        {isRecording && (
          <>
            <div className="absolute w-32 h-32 bg-red-100 rounded-full animate-ping" style={{ animationDuration: '1.5s' }}></div>
            <div className="absolute w-48 h-48 border border-red-200 rounded-full animate-pulse"></div>
            <div className="absolute w-64 h-64 border border-red-100 rounded-full animate-pulse" style={{ animationDelay: '0.5s' }}></div>
          </>
        )}

        <button 
          onClick={() => isRecording ? handleStop(transcriptRef.current) : handleStart()}
          className={`relative z-20 flex items-center justify-center w-24 h-24 rounded-full transition-all duration-300 shadow-xl ${
            isRecording 
              ? 'bg-gradient-to-b from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white scale-110 shadow-red-500/30' 
              : 'bg-gradient-to-b from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 text-white hover:scale-105 shadow-blue-500/20 hover:shadow-blue-500/40'
          }`}
        >
          {isRecording ? <Square className="w-8 h-8 fill-current" /> : <Mic className="w-10 h-10" />}
        </button>
      </div>
      
      {/* Controls: Language Dropdown & Keyboard Shortcut */}
      <div className="flex flex-col sm:flex-row items-center gap-4 z-50 mb-8 relative">
        <div className="relative">
          <button 
            onClick={() => setIsLangMenuOpen(!isLangMenuOpen)}
            className="flex items-center gap-2 bg-white hover:bg-slate-50 px-5 py-2.5 rounded-xl border border-slate-200 transition-all text-sm text-slate-700 font-semibold shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20"
          >
            <Globe className="w-4 h-4 text-blue-500" />
            {currentLangLabel}
            <ChevronDown className={`w-4 h-4 text-slate-400 transition-transform ${isLangMenuOpen ? 'rotate-180' : ''}`} />
          </button>
          
          {/* 
            Z-INDEX FIX: 
            Added z-[9999] so it floats above everything.
            Used fixed width and absolute positioning.
          */}
          {isLangMenuOpen && (
            <>
              <div 
                className="fixed inset-0 z-[9998]" 
                onClick={() => setIsLangMenuOpen(false)}
              />
              <div className="absolute top-full left-1/2 -translate-x-1/2 sm:left-0 sm:translate-x-0 mt-2 w-56 bg-white border border-slate-200 rounded-xl shadow-[0_20px_60px_-15px_rgba(0,0,0,0.1)] overflow-hidden z-[9999] py-2">
                <div className="px-3 py-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">Select Language</div>
                {SUPPORTED_LANGUAGES.map((lang) => (
                  <button
                    key={lang.code}
                    onClick={() => {
                      setLanguage(lang.code);
                      setIsLangMenuOpen(false);
                    }}
                    className="w-full flex items-center justify-between px-4 py-2.5 text-sm font-medium transition-colors text-slate-700 hover:bg-slate-50"
                  >
                    <span>{lang.label}</span>
                    {language === lang.code && <Check className="w-4 h-4 text-blue-600" />}
                  </button>
                ))}
              </div>
            </>
          )}
        </div>
        
        <div className="hidden sm:flex px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-500 items-center gap-2 shadow-sm">
          <span>Keyboard</span>
          <span className="bg-white px-2 py-1 rounded shadow-sm border border-slate-200 font-mono text-slate-700">Ctrl</span>
          <span>+</span>
          <span className="bg-white px-2 py-1 rounded shadow-sm border border-slate-200 font-mono text-slate-700">Space</span>
        </div>
      </div>

      {/* Transcript Box */}
      <div className={`w-full p-8 md:p-10 min-h-[160px] rounded-[2rem] transition-all duration-300 relative z-10 ${
        isRecording 
          ? 'bg-white border-2 border-blue-200 shadow-[0_0_40px_-10px_rgba(59,130,246,0.15)]' 
          : 'bg-slate-50 border border-slate-200/60 shadow-inner'
      }`}>
        {isLoading ? (
          <div className="flex flex-col items-center justify-center h-full text-blue-600 gap-5">
            <Activity className="w-10 h-10 animate-spin" />
            <p className="text-base font-semibold tracking-wide animate-pulse text-blue-700">Analyzing clinical context & generating prescriptions...</p>
          </div>
        ) : transcript ? (
          <p className="text-xl md:text-2xl text-slate-800 leading-relaxed font-medium text-center">{transcript}</p>
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-slate-400 gap-3">
            <Mic className="w-8 h-8 opacity-20" />
            <p className="text-lg italic font-light tracking-wide text-center">Ready for clinical dictation. Press the mic to start.</p>
          </div>
        )}
      </div>
    </div>
  );
}
