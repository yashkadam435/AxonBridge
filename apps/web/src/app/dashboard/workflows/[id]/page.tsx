'use client';

import React, { useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { Play, ArrowLeft, Bot, FileText, CheckCircle2, AlertTriangle, Loader2 } from 'lucide-react';

const WORKFLOW_METADATA: Record<string, { title: string; desc: string; placeholder: string }> = {
  'registration': {
    title: 'Patient Registration Extraction',
    desc: 'Extract patient demographics, contact details, and insurance info from unstructured notes.',
    placeholder: 'e.g., "Patient John Doe (DOB 05/12/1980) arrived at clinic. Address: 123 Main St. Insured by Aetna, policy #123456789. Emergency contact is his wife Jane 555-9876."'
  },
  'billing': {
    title: 'Billing Code Extraction',
    desc: 'Automatically extract and map ICD-10 and CPT codes from clinical documentation.',
    placeholder: 'e.g., "Patient presents with acute pharyngitis and fever. Performed rapid strep test (positive). Prescribed Amoxicillin."'
  },
  'lab-results': {
    title: 'Lab Result Parsing',
    desc: 'Parse unstructured lab reports into structured key-value data and identify abnormal flags.',
    placeholder: 'e.g., "Comprehensive Metabolic Panel: Glucose 105 mg/dL (High), BUN 15 mg/dL, Creatinine 0.9 mg/dL. CBC shows WBC 11.2 (High)."'
  },
  'discharge': {
    title: 'Discharge Summary Generation',
    desc: 'Synthesize raw physician notes into a formal, structured hospital discharge summary.',
    placeholder: 'e.g., "Admitted 10/12 for chest pain. Diagnosed with NSTEMI. Treated with Heparin and Aspirin. Discharged 10/15. Follow up with cardiology in 1 week. Continue Aspirin 81mg."'
  },
  'scheduling': {
    title: 'Appointment Scheduling',
    desc: 'Extract booking intents including doctor, date, time, and urgency.',
    placeholder: 'e.g., "Please schedule an urgent appointment for Mary Smith with Dr. Patel sometime next Tuesday morning for severe back pain."'
  }
};

export default function WorkflowExecutionPage() {
  const router = useRouter();
  const params = useParams();
  const workflowId = params.id as string;
  
  const metadata = WORKFLOW_METADATA[workflowId];

  const [inputData, setInputData] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [resultData, setResultData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  if (!metadata) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-4">
        <AlertTriangle size={48} className="text-red-500" />
        <h1 className="text-2xl font-bold">Workflow Not Found</h1>
        <button onClick={() => router.push('/dashboard/workflows')} className="text-blue-500 hover:underline">
          Return to Workflows
        </button>
      </div>
    );
  }

  const handleRunAI = async () => {
    if (!inputData.trim()) {
      setError("Please enter some text to process.");
      return;
    }
    
    setIsProcessing(true);
    setError(null);
    setResultData(null);
    
    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${baseUrl}/api/v1/workflows/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('axb_access_token') || ''}`
        },
        body: JSON.stringify({
          workflow_type: workflowId,
          text: inputData
        })
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to process workflow');
      }
      
      setResultData(data.data);
    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred connecting to the AI model.');
    } finally {
      setIsProcessing(false);
    }
  };

  const renderJsonValue = (value: any): React.ReactNode => {
    if (Array.isArray(value)) {
      if (value.length === 0) return <span className="text-slate-400 italic">None</span>;
      return (
        <ul className="list-disc list-inside space-y-1">
          {value.map((item, i) => (
            <li key={i} className="text-slate-700">
              {typeof item === 'object' ? renderJsonValue(item) : item}
            </li>
          ))}
        </ul>
      );
    } else if (typeof value === 'object' && value !== null) {
      return (
        <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 mt-2 space-y-2">
          {Object.entries(value).map(([k, v]) => (
            <div key={k} className="flex flex-col sm:flex-row sm:gap-4">
              <span className="font-semibold text-slate-600 text-sm capitalize min-w-[120px]">
                {k.replace(/_/g, ' ')}:
              </span>
              <span className="text-slate-800 text-sm">{renderJsonValue(v)}</span>
            </div>
          ))}
        </div>
      );
    }
    return <span className="text-slate-800 font-medium">{String(value) || <span className="text-slate-400 italic">N/A</span>}</span>;
  };

  return (
    <div className="max-w-6xl mx-auto pb-12">
      {/* Header */}
      <button 
        onClick={() => router.push('/dashboard/workflows')}
        className="flex items-center gap-2 text-slate-500 hover:text-blue-600 transition-colors mb-6 font-medium text-sm"
      >
        <ArrowLeft size={16} /> Back to Workflows
      </button>

      <div className="flex flex-col md:flex-row gap-8 items-start mb-8">
        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-100 to-cyan-100 text-blue-600 flex items-center justify-center shrink-0 shadow-sm border border-blue-200">
          <Bot size={32} />
        </div>
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">{metadata.title}</h1>
          <p className="text-lg text-slate-500 mt-2">{metadata.desc}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Input Section */}
        <div className="flex flex-col gap-4">
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm flex flex-col h-full">
            <div className="flex items-center gap-2 mb-4">
              <FileText size={20} className="text-blue-500" />
              <h2 className="text-lg font-bold text-slate-800">Raw Input Data</h2>
            </div>
            <textarea
              value={inputData}
              onChange={(e) => setInputData(e.target.value)}
              placeholder={metadata.placeholder}
              className="w-full flex-1 min-h-[300px] p-4 bg-slate-50 border border-slate-200 rounded-xl resize-y outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all text-slate-700 leading-relaxed"
            />
            {error && (
              <div className="mt-4 p-4 bg-red-50 text-red-600 rounded-xl border border-red-200 flex items-start gap-3">
                <AlertTriangle size={20} className="shrink-0 mt-0.5" />
                <p className="text-sm font-medium">{error}</p>
              </div>
            )}
            <button 
              onClick={handleRunAI}
              disabled={isProcessing}
              className={`mt-6 w-full py-4 rounded-xl flex items-center justify-center gap-2 text-white font-bold text-lg transition-all shadow-lg ${
                isProcessing 
                  ? 'bg-blue-400 cursor-not-allowed' 
                  : 'bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 hover:shadow-blue-500/30 hover:-translate-y-0.5'
              }`}
            >
              {isProcessing ? (
                <>
                  <Loader2 size={24} className="animate-spin" />
                  Processing with Groq LLM...
                </>
              ) : (
                <>
                  <Play size={24} fill="currentColor" />
                  Run AI Extraction
                </>
              )}
            </button>
          </div>
        </div>

        {/* Output Section */}
        <div className="flex flex-col gap-4">
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm h-full min-h-[450px]">
            <div className="flex items-center gap-2 mb-6">
              <CheckCircle2 size={20} className={resultData ? "text-green-500" : "text-slate-300"} />
              <h2 className="text-lg font-bold text-slate-800">Structured Output</h2>
            </div>
            
            {!resultData && !isProcessing && (
              <div className="flex flex-col items-center justify-center h-[300px] text-slate-400 gap-4">
                <div className="w-20 h-20 rounded-full bg-slate-50 flex items-center justify-center border-2 border-dashed border-slate-200">
                  <Bot size={32} className="text-slate-300" />
                </div>
                <p className="font-medium">Waiting for input...</p>
              </div>
            )}
            
            {isProcessing && (
              <div className="flex flex-col items-center justify-center h-[300px] text-blue-500 gap-6">
                <div className="relative">
                  <div className="w-16 h-16 border-4 border-blue-200 rounded-full animate-ping absolute inset-0"></div>
                  <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin relative z-10"></div>
                </div>
                <p className="font-bold animate-pulse">Running Clinical AI Models...</p>
              </div>
            )}
            
            {resultData && !isProcessing && (
              <div className="flex flex-col gap-4 animate-fadeInUp">
                {Object.entries(resultData).map(([key, value]) => (
                  <div key={key} className="bg-slate-50 p-4 rounded-xl border border-slate-200 hover:border-blue-200 hover:shadow-sm transition-all">
                    <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
                      {key.replace(/_/g, ' ')}
                    </h3>
                    <div className="text-slate-800 text-sm">
                      {renderJsonValue(value)}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
