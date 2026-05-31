"use client";

import React, { useState, useEffect } from 'react';
import { FileText, Edit, AlertTriangle, CheckCircle2, Save, X } from 'lucide-react';

interface SOAPProps {
  subjective: string;
  objective: string;
  assessment: string;
  plan: string;
}

export default function SOAPNoteViewer({ subjective, objective, assessment, plan }: SOAPProps) {
  const isPopulated = subjective && subjective !== "Awaiting input...";
  
  const [isEditing, setIsEditing] = useState(false);
  const [editableData, setEditableData] = useState({
    subjective: '',
    objective: '',
    assessment: '',
    plan: ''
  });

  // Sync props to state when they change from the parent
  useEffect(() => {
    setEditableData({ subjective, objective, assessment, plan });
  }, [subjective, objective, assessment, plan]);

  const handleSave = () => {
    setIsEditing(false);
    // In a real app, we would propagate this back up to the parent or API.
  };

  const handleCancel = () => {
    setEditableData({ subjective, objective, assessment, plan });
    setIsEditing(false);
  };

  return (
    <div className="border border-slate-200 rounded-3xl bg-white overflow-hidden shadow-xl shadow-slate-200/50 transition-all duration-500 flex flex-col h-full min-h-[600px] w-full">
      <div className="bg-slate-50 p-6 sm:p-8 border-b border-slate-200 flex justify-between items-center z-10 relative">
        <h3 className="font-extrabold flex items-center gap-4 text-xl tracking-wide text-slate-800">
          <div className="p-3 bg-blue-100 rounded-xl border border-blue-200 shadow-sm">
            <FileText className="w-6 h-6 text-blue-600" /> 
          </div>
          Structured SOAP Note
          {isPopulated && !isEditing && <CheckCircle2 className="w-6 h-6 text-emerald-500 ml-2 animate-pulse" />}
        </h3>
        
        {isEditing ? (
          <div className="flex items-center gap-3">
            <button 
              onClick={handleCancel}
              className="text-sm font-semibold flex items-center gap-2 px-5 py-2.5 rounded-xl bg-white hover:bg-slate-50 transition-colors border border-slate-200 text-slate-600 shadow-sm"
            >
              <X className="w-4 h-4" /> Cancel
            </button>
            <button 
              onClick={handleSave}
              className="text-sm font-semibold flex items-center gap-2 px-5 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-600 transition-colors text-white shadow-[0_4px_14px_rgba(16,185,129,0.39)]"
            >
              <Save className="w-4 h-4" /> Save Changes
            </button>
          </div>
        ) : (
          <button 
            onClick={() => setIsEditing(true)}
            disabled={!isPopulated}
            className={`text-sm font-semibold flex items-center gap-2 px-5 py-2.5 rounded-xl transition-all border shadow-sm ${
              isPopulated 
                ? 'bg-white hover:bg-blue-50 border-slate-200 hover:border-blue-200 text-slate-700 hover:text-blue-700' 
                : 'bg-slate-100 border-slate-200 text-slate-400 cursor-not-allowed'
            }`}
          >
            <Edit className="w-4 h-4" /> Edit Note
          </button>
        )}
      </div>
      
      <div className="flex-1 divide-y divide-slate-100 overflow-y-auto custom-scrollbar">
        <Section 
          title="Subjective" 
          field="subjective"
          content={editableData.subjective} 
          isEditing={isEditing}
          onChange={(val) => setEditableData(prev => ({...prev, subjective: val}))}
          colorClass="bg-white hover:bg-slate-50/50" 
          textColor="text-slate-800"
          delay="0ms" 
        />
        <Section 
          title="Objective" 
          field="objective"
          content={editableData.objective} 
          isEditing={isEditing}
          onChange={(val) => setEditableData(prev => ({...prev, objective: val}))}
          colorClass="bg-white hover:bg-slate-50/50" 
          textColor="text-slate-800"
          delay="100ms" 
        />
        <Section 
          title="Assessment" 
          field="assessment"
          content={editableData.assessment} 
          isEditing={isEditing}
          onChange={(val) => setEditableData(prev => ({...prev, assessment: val}))}
          colorClass="bg-white hover:bg-slate-50/50" 
          textColor="text-slate-800"
          hasAlert={true} 
          delay="200ms" 
        />
        <Section 
          title="Plan & Prescriptions" 
          field="plan"
          content={editableData.plan} 
          isEditing={isEditing}
          onChange={(val) => setEditableData(prev => ({...prev, plan: val}))}
          colorClass="bg-blue-50/30 hover:bg-blue-50/60" 
          textColor="text-blue-900"
          delay="300ms" 
        />
      </div>
    </div>
  );
}

function Section({ 
  title, 
  field,
  content, 
  colorClass, 
  textColor,
  hasAlert = false, 
  delay,
  isEditing,
  onChange
}: { 
  title: string, 
  field: string,
  content: string, 
  colorClass: string, 
  textColor: string,
  hasAlert?: boolean, 
  delay: string,
  isEditing: boolean,
  onChange: (val: string) => void
}) {
  const isAwaiting = content === "Awaiting input...";
  
  return (
    <div 
      className={`p-6 sm:p-10 transition-all duration-500 ease-out ${colorClass}`}
      style={{ animationFillMode: 'both', animationDuration: '500ms', animationDelay: delay, animationName: 'fadeInUp' }}
    >
      <div className="flex items-center gap-3 mb-4">
        <h4 className={`font-bold text-sm uppercase tracking-widest text-slate-500`}>{title}</h4>
        {hasAlert && !isAwaiting && content && (
          <div className="flex items-center gap-1.5 px-2.5 py-1 bg-amber-100 text-amber-700 rounded-md text-xs font-semibold">
            <AlertTriangle className="w-3.5 h-3.5" /> Important
          </div>
        )}
      </div>
      
      {isEditing ? (
        <textarea
          value={content}
          onChange={(e) => onChange(e.target.value)}
          className="w-full min-h-[140px] bg-slate-50 border border-slate-200 rounded-xl p-5 text-slate-800 text-base leading-relaxed focus:outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500 transition-all resize-y shadow-inner font-medium"
          placeholder={`Enter ${title.toLowerCase()}...`}
        />
      ) : (
        <p className={`text-lg leading-relaxed whitespace-pre-wrap ${
          !content || isAwaiting ? 'text-slate-400 italic font-light' : `${textColor} font-medium`
        }`}>
          {content || "No data recorded."}
        </p>
      )}
    </div>
  );
}
