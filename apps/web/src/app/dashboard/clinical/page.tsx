'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Activity, AlertTriangle, CheckCircle, ChevronDown, ChevronUp,
  ClipboardList, Edit3, FileText, Heart, ListOrdered, Percent,
  Pill, Plus, Save, Search, Shield, Stethoscope, User, X, XCircle,
  RefreshCw, Eye, Clock, AlertOctagon, ChevronRight, Info, Trash2, Mic, MicOff, Volume2
} from 'lucide-react';

const API = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8004'}/api/v1/clinical`;

/* ════════════════════════════════════════════════════════════════
   AxonBridge — Clinical Documentation (Phase 4) — Voice AI Scribe
   ════════════════════════════════════════════════════════════════ */

export default function ClinicalPage() {
  const [mounted, setMounted] = useState(false);
  useEffect(() => { setMounted(true); }, []);

  // ── View State ──
  const [activeView, setActiveView] = useState<'list' | 'create' | 'detail'>('list');
  const [encounters, setEncounters] = useState<any[]>([]);
  const [selectedEnc, setSelectedEnc] = useState<any>(null);
  const [loading, setLoading] = useState('');
  const [toast, setToast] = useState('');

  const showToast = (msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(''), 3000);
  };

  // ── Create/Edit Encounter Form ──
  const defaultForm = {
    patient_name: '', age: '', gender: 'Male', encounter_type: 'outpatient',
    department: 'General', clinician: '', chief_complaint: '',
    symptoms: '', history: '', vital_systolic: '', vital_diastolic: '',
    vital_hr: '', vital_spo2: '', vital_temp: '', vital_rr: '',
    current_medications: '', allergies: ''
  };
  const [form, setForm] = useState(defaultForm);
  const [isEditingDetails, setIsEditingDetails] = useState(false);

  // ── Voice Scribe State ──
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [ttsMessage, setTtsMessage] = useState('');
  const recognitionRef = useRef<any>(null);

  // ── SOAP Editor ──
  const [soapEditing, setSoapEditing] = useState(false);
  const [soapDraft, setSoapDraft] = useState({ subjective: '', objective: '', assessment: '', plan: '' });

  // ── CDS Overlay ──
  const [cdsData, setCdsData] = useState<any>(null);
  const [cdsOpen, setCdsOpen] = useState(false);
  const [anomalies, setAnomalies] = useState<any[]>([]);
  const [anomalyExpanded, setAnomalyExpanded] = useState(false);

  // ── Prescription ──
  const [rxData, setRxData] = useState<any>(null);

  // ── Confirmation Dialog ──
  const [confirmDialog, setConfirmDialog] = useState<any>(null);

  // ── Fetch encounters ──
  const fetchEncounters = useCallback(async () => {
    try {
      const res = await fetch(`${API}/encounters/encounters?_t=${Date.now()}`, { cache: 'no-store' });
      const data = await res.json();
      setEncounters(Array.isArray(data) ? data : []);
    } catch { setEncounters([]); }
  }, []);

  useEffect(() => { if (mounted) fetchEncounters(); }, [mounted, fetchEncounters]);

  // ── Voice Scribe Logic ──
  const startDictation = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) { alert("Speech Recognition not supported in this browser."); return; }
    
    if (recognitionRef.current) {
        recognitionRef.current.stop();
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    
    recognition.onresult = (event: any) => {
        let finalTrans = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
            if (event.results[i].isFinal) {
                finalTrans += event.results[i][0].transcript + ' ';
            }
        }
        if (finalTrans) {
             setTranscript(prev => (prev + ' ' + finalTrans).trim());
        }
    };

    recognition.onerror = (e: any) => {
        console.error("Speech recognition error", e);
        setIsListening(false);
    };

    recognition.onend = () => {
        setIsListening(false);
    };

    recognition.start();
    setIsListening(true);
    recognitionRef.current = recognition;
  };

  const stopAndParseDictation = async () => {
    if (recognitionRef.current) {
        recognitionRef.current.stop();
    }
    setIsListening(false);
    setLoading('parsing');
    
    try {
        const res = await fetch(`${API}/encounters/scribe/parse`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ transcript, current_form_state: form })
        });
        const data = await res.json();
        
        if (data.form_updates) {
            setForm(prev => ({ ...prev, ...data.form_updates }));
        }
        
        if (data.tts_question) {
            setTtsMessage(data.tts_question);
            const utterance = new SpeechSynthesisUtterance(data.tts_question);
            window.speechSynthesis.speak(utterance);
        }
    } catch (e: any) {
        alert("Error parsing dictation: " + e.message);
    }
    setLoading('');
    setTranscript('');
  };

  // ── Create Encounter ──
  const handleCreate = async () => {
    setLoading('creating');
    const vitals: any = {};
    if (form.vital_systolic) vitals.systolic_bp = Number(form.vital_systolic);
    if (form.vital_diastolic) vitals.diastolic_bp = Number(form.vital_diastolic);
    if (form.vital_hr) vitals.heart_rate = Number(form.vital_hr);
    if (form.vital_spo2) vitals.spo2 = Number(form.vital_spo2);
    if (form.vital_temp) vitals.temperature = Number(form.vital_temp);
    if (form.vital_rr) vitals.respiratory_rate = Number(form.vital_rr);

    try {
      const res = await fetch(`${API}/encounters/encounters`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patient_name: form.patient_name,
          age: Number(form.age) || 0,
          gender: form.gender,
          encounter_type: form.encounter_type,
          department: form.department,
          clinician: form.clinician,
          chief_complaint: form.chief_complaint,
          symptoms: typeof form.symptoms === 'string' ? form.symptoms.split(',').map(s => s.trim()).filter(Boolean) : form.symptoms,
          history: form.history,
          vital_signs: Object.keys(vitals).length > 0 ? vitals : undefined,
          current_medications: typeof form.current_medications === 'string' ? form.current_medications.split(',').map(s => s.trim()).filter(Boolean) : form.current_medications,
          allergies: typeof form.allergies === 'string' ? form.allergies.split(',').map(s => s.trim()).filter(Boolean) : form.allergies,
        })
      });
      const enc = await res.json();
      setSelectedEnc(enc);
      setActiveView('detail');
      showToast('Encounter Created Successfully!');
      await fetchEncounters();
    } catch (e: any) { alert('Error creating encounter: ' + e.message); }
    setLoading('');
  };

  // ── Update Encounter Details ──
  const handleUpdate = async () => {
    if (!selectedEnc) return;
    setLoading('updating');
    const vitals: any = {};
    if (form.vital_systolic) vitals.systolic_bp = Number(form.vital_systolic);
    if (form.vital_diastolic) vitals.diastolic_bp = Number(form.vital_diastolic);
    if (form.vital_hr) vitals.heart_rate = Number(form.vital_hr);
    if (form.vital_spo2) vitals.spo2 = Number(form.vital_spo2);
    if (form.vital_temp) vitals.temperature = Number(form.vital_temp);
    if (form.vital_rr) vitals.respiratory_rate = Number(form.vital_rr);

    try {
      const res = await fetch(`${API}/encounters/encounters/${selectedEnc.id}`, {
        method: 'PUT', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patient_name: form.patient_name,
          age: Number(form.age) || 0,
          gender: form.gender,
          encounter_type: form.encounter_type,
          department: form.department,
          clinician: form.clinician,
          chief_complaint: form.chief_complaint,
          symptoms: typeof form.symptoms === 'string' ? form.symptoms.split(',').map(s => s.trim()).filter(Boolean) : form.symptoms,
          history: form.history,
          vital_signs: Object.keys(vitals).length > 0 ? vitals : undefined,
          current_medications: typeof form.current_medications === 'string' ? form.current_medications.split(',').map(s => s.trim()).filter(Boolean) : form.current_medications,
          allergies: typeof form.allergies === 'string' ? form.allergies.split(',').map(s => s.trim()).filter(Boolean) : form.allergies,
        })
      });
      const enc = await res.json();
      setSelectedEnc(enc);
      setIsEditingDetails(false);
      showToast('Encounter Updated Successfully!');
      await fetchEncounters();
    } catch (e: any) { alert('Error updating encounter: ' + e.message); }
    setLoading('');
  };

  // ── Generate SOAP ──
  const handleGenerateSOAP = async () => {
    if (!selectedEnc) return;
    setLoading('soap');
    try {
      const res = await fetch(`${API}/encounters/soap/generate`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          encounter_id: selectedEnc.id,
          symptoms: selectedEnc.symptoms || [],
          vital_signs: selectedEnc.vital_signs,
          patient_context: { age: selectedEnc.age, gender: selectedEnc.gender, history: selectedEnc.history }
        })
      });
      const data = await res.json();
      if (data.soap) {
        setSelectedEnc({ ...selectedEnc, soap: data.soap, soap_status: 'pending_review', icd_codes: data.soap.icd_codes || [], ai_confidence: data.soap.confidence || 0 });
        setSoapDraft({ subjective: data.soap.subjective || '', objective: data.soap.objective || '', assessment: data.soap.assessment || '', plan: data.soap.plan || '' });
        showToast('SOAP Note Generated!');
        await fetchEncounters();
      }
    } catch (e: any) { alert('Error generating SOAP: ' + e.message); }
    setLoading('');
  };

  // ── Save SOAP ──
  const handleSaveSOAP = async () => {
    if (!selectedEnc) return;
    setLoading('saving');
    try {
      await fetch(`${API}/encounters/soap/save`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          encounter_id: selectedEnc.id,
          ...soapDraft,
          icd_codes: selectedEnc.icd_codes || []
        })
      });
      setSelectedEnc({ ...selectedEnc, soap: soapDraft, soap_status: 'approved' });
      setSoapEditing(false);
      setConfirmDialog(null);
      showToast('SOAP Note Approved & Saved!');
      await fetchEncounters();
    } catch (e: any) { alert('Error saving SOAP: ' + e.message); }
    setLoading('');
  };

  // ── Run CDS ──
  const handleRunCDS = async () => {
    if (!selectedEnc) return;
    setLoading('cds');
    setCdsData(null); setAnomalies([]);
    try {
      const res = await fetch(`${API}/cds/evaluate`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          specialty: 'auto',
          patient_context: { age: selectedEnc.age, gender: selectedEnc.gender, history: selectedEnc.history },
          symptoms: selectedEnc.symptoms || [],
          vital_signs: selectedEnc.vital_signs,
          department: selectedEnc.department,
          current_diagnosis: selectedEnc.soap?.assessment || ''
        })
      });
      const data = await res.json();
      setCdsData(data);
      setCdsOpen(true);
      setAnomalies((data.alerts || []).filter((a: any) => a.category === 'anomaly'));
    } catch (e: any) { alert('CDS Error: ' + e.message); }
    setLoading('');
  };

  // ── Generate Prescription ──
  const handleGenerateRx = async () => {
    if (!selectedEnc?.soap?.assessment) { alert('Generate SOAP first to get a diagnosis.'); return; }
    setLoading('rx');
    try {
      const res = await fetch(`${API}/encounters/prescriptions/generate`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          encounter_id: selectedEnc.id,
          diagnosis: selectedEnc.soap.assessment,
          patient_context: { age: selectedEnc.age, gender: selectedEnc.gender },
          allergies: selectedEnc.allergies || [],
          current_medications: selectedEnc.current_medications || []
        })
      });
      const data = await res.json();
      setRxData(data.prescription_data || data);
      showToast('Prescription Generated!');
    } catch (e: any) { alert('Rx Error: ' + e.message); }
    setLoading('');
  };

  // ── Safety Confirmation ──
  const openSafetyConfirm = () => {
    setConfirmDialog({
      confidence: selectedEnc?.ai_confidence || 0.85,
      fields: {
        'Diagnosis': selectedEnc?.soap?.assessment || 'N/A',
        'Plan': selectedEnc?.soap?.plan?.substring(0, 100) + '...' || 'N/A',
        'ICD Codes': (selectedEnc?.icd_codes || []).join(', ') || 'None'
      }
    });
  };
  
  const startEditingEncounter = () => {
      setForm({
          patient_name: selectedEnc.patient_name || '',
          age: selectedEnc.age?.toString() || '',
          gender: selectedEnc.gender || 'Male',
          encounter_type: selectedEnc.encounter_type || 'outpatient',
          department: selectedEnc.department || 'General',
          clinician: selectedEnc.clinician || '',
          chief_complaint: selectedEnc.chief_complaint || '',
          symptoms: (selectedEnc.symptoms || []).join(', '),
          history: selectedEnc.history || '',
          vital_systolic: selectedEnc.vital_signs?.systolic_bp?.toString() || '',
          vital_diastolic: selectedEnc.vital_signs?.diastolic_bp?.toString() || '',
          vital_hr: selectedEnc.vital_signs?.heart_rate?.toString() || '',
          vital_spo2: selectedEnc.vital_signs?.spo2?.toString() || '',
          vital_temp: selectedEnc.vital_signs?.temperature?.toString() || '',
          vital_rr: selectedEnc.vital_signs?.respiratory_rate?.toString() || '',
          current_medications: (selectedEnc.current_medications || []).join(', '),
          allergies: (selectedEnc.allergies || []).join(', ')
      });
      setIsEditingDetails(true);
  }

  if (!mounted) return null;

  // ═══════════════════════════════════
  //  RENDER: Encounter List View
  // ═══════════════════════════════════
  const renderList = () => (
    <div>
      <div style={s.pageHeader}>
        <div>
          <h1 style={s.pageTitle}>Clinical Documentation</h1>
          <p style={s.pageSub}>Patient encounters, SOAP notes, AI-powered CDS & prescriptions</p>
        </div>
        <button onClick={() => { setForm(defaultForm); setActiveView('create'); }} style={s.primaryBtn}><Plus size={16}/> New Encounter</button>
      </div>

      {/* Summary Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
        {[
          { label: 'Total Encounters', value: encounters.length, color: '#3B82F6', icon: <ClipboardList size={20}/> },
          { label: 'Active', value: encounters.filter(e => e.status === 'active').length, color: '#22C55E', icon: <Activity size={20}/> },
          { label: 'Pending Review', value: encounters.filter(e => e.soap_status === 'pending_review').length, color: '#F59E0B', icon: <Clock size={20}/> },
          { label: 'Approved', value: encounters.filter(e => e.soap_status === 'approved').length, color: '#8B5CF6', icon: <CheckCircle size={20}/> },
        ].map((c, i) => (
          <div key={i} style={{ background: 'white', borderRadius: '0.75rem', padding: '1.25rem', border: '1px solid #E2E8F0', position: 'relative', overflow: 'hidden' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#0F172A' }}>{c.value}</div>
                <div style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{c.label}</div>
              </div>
              <div style={{ color: c.color, opacity: 0.6 }}>{c.icon}</div>
            </div>
            <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, height: '3px', background: c.color }} />
          </div>
        ))}
      </div>

      {/* Encounters Table */}
      {encounters.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '4rem 2rem', background: 'white', borderRadius: '0.75rem', border: '1px solid #E2E8F0' }}>
          <Stethoscope size={48} style={{ color: '#CBD5E1', margin: '0 auto 1rem' }}/>
          <h3 style={{ color: '#64748B', margin: '0 0 0.5rem' }}>No Encounters Yet</h3>
          <p style={{ color: '#94A3B8', fontSize: '0.9rem', marginBottom: '1rem' }}>Click "New Encounter" to create your first clinical encounter or dictate via voice.</p>
          <button onClick={() => { setForm(defaultForm); setActiveView('create'); }} style={s.primaryBtn}><Plus size={16}/> Create Encounter</button>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          {encounters.map((enc, i) => {
            const typeColors: any = { outpatient: '#3B82F6', inpatient: '#8B5CF6', emergency: '#EF4444', telehealth: '#06B6D4' };
            const soapColors: any = { approved: { bg: '#DCFCE7', text: '#22C55E' }, pending_review: { bg: '#FEF9C3', text: '#F59E0B' }, pending: { bg: '#F1F5F9', text: '#94A3B8' } };
            const sc = soapColors[enc.soap_status] || soapColors.pending;
            return (
              <div key={enc.id} onClick={() => { setSelectedEnc(enc); setSoapDraft(enc.soap || { subjective: '', objective: '', assessment: '', plan: '' }); setSoapEditing(false); setCdsData(null); setRxData(null); setAnomalies([]); setIsEditingDetails(false); setActiveView('detail'); }}
                style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '1rem 1.25rem', borderRadius: '0.75rem', background: 'white', border: '1px solid #E2E8F0', cursor: 'pointer', transition: 'all 0.2s' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flex: 1 }}>
                  <div style={{ width: 40, height: 40, borderRadius: '50%', background: `${typeColors[enc.encounter_type] || '#94A3B8'}15`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <User size={18} style={{ color: typeColors[enc.encounter_type] || '#94A3B8' }}/>
                  </div>
                  <div>
                    <div style={{ fontWeight: 700, color: '#0F172A' }}>{enc.patient_name}</div>
                    <div style={{ fontSize: '0.8rem', color: '#64748B' }}>{enc.department} · {enc.clinician} · {enc.encounter_type}</div>
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  {enc.icd_codes?.length > 0 && (
                    <div style={{ display: 'flex', gap: '0.25rem' }}>
                      {enc.icd_codes.map((c: string) => <span key={c} style={{ fontSize: '0.65rem', fontWeight: 600, padding: '0.1rem 0.4rem', borderRadius: '0.25rem', background: '#F1F5F9', color: '#475569', fontFamily: 'monospace' }}>{c}</span>)}
                    </div>
                  )}
                  <span style={{ fontSize: '0.7rem', fontWeight: 600, padding: '0.2rem 0.6rem', borderRadius: '9999px', background: sc.bg, color: sc.text }}>{(enc.soap_status || 'pending').replace('_', ' ')}</span>
                  <ChevronRight size={16} style={{ color: '#94A3B8' }}/>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );

  // ═══════════════════════════════════
  //  RENDER: Create/Edit Encounter Form
  // ═══════════════════════════════════
  const renderCreateOrEdit = () => {
    const isEdit = isEditingDetails && selectedEnc;
    return (
    <div>
      <div style={s.pageHeader}>
        <div>
          <h1 style={s.pageTitle}>{isEdit ? `Edit Encounter: ${selectedEnc.patient_name}` : 'New Clinical Encounter'}</h1>
          <p style={s.pageSub}>{isEdit ? 'Update patient details' : 'Fill in details or dictate using the Voice Scribe'}</p>
        </div>
        <button onClick={() => isEdit ? setIsEditingDetails(false) : setActiveView('list')} style={{ ...s.secondaryBtn }}><X size={16}/> Cancel</button>
      </div>

      {/* Voice Dictation Panel (Only on Create) */}
      {!isEdit && (
        <div style={{ background: '#F8FAFC', borderRadius: '0.75rem', border: '1px solid #E2E8F0', padding: '1.5rem', marginBottom: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h3 style={{ margin: 0, color: '#0F172A', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Volume2 size={20} color="#8B5CF6"/> AI Voice Scribe
                </h3>
                {!isListening ? (
                    <button onClick={startDictation} style={{ ...s.primaryBtn, background: 'linear-gradient(135deg, #8B5CF6, #7C3AED)' }}>
                        <Mic size={16}/> Start Dictation
                    </button>
                ) : (
                    <button onClick={stopAndParseDictation} style={{ ...s.primaryBtn, background: '#DC2626' }}>
                        {loading === 'parsing' ? <RefreshCw size={16} className="spin" /> : <MicOff size={16}/>} 
                        {loading === 'parsing' ? 'Parsing AI...' : 'Stop & Parse'}
                    </button>
                )}
            </div>
            {(isListening || transcript) && (
                <div style={{ background: 'white', padding: '1rem', borderRadius: '0.5rem', border: '1px dashed #CBD5E1', minHeight: '60px', fontStyle: 'italic', color: '#475569' }}>
                    {transcript || "Listening... please speak."}
                </div>
            )}
            {ttsMessage && (
                <div style={{ background: '#FEF9C3', padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid #FDE047', color: '#854D0E', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Info size={16} /> <strong>AI Agent:</strong> {ttsMessage}
                </div>
            )}
        </div>
      )}

      <div style={{ background: 'white', borderRadius: '0.75rem', border: '1px solid #E2E8F0', padding: '2rem' }}>
        {/* Patient Info */}
        <h3 style={{ margin: '0 0 1rem', color: '#0F172A', display: 'flex', alignItems: 'center', gap: '0.5rem' }}><User size={18} color="#3B82F6"/> Patient Information</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
          <Input label="Patient Name *" value={form.patient_name} onChange={(v: any) => setForm({ ...form, patient_name: v })} placeholder="John Doe" />
          <Input label="Age" value={form.age} onChange={(v: any) => setForm({ ...form, age: v })} placeholder="45" type="number" />
          <Select label="Gender" value={form.gender} onChange={(v: any) => setForm({ ...form, gender: v })} options={['Male', 'Female', 'Other']} />
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
          <Select label="Encounter Type" value={form.encounter_type} onChange={(v: any) => setForm({ ...form, encounter_type: v })} options={['outpatient', 'inpatient', 'emergency', 'telehealth']} />
          <Select label="Department" value={form.department} onChange={(v: any) => setForm({ ...form, department: v })} options={['General', 'Cardiology', 'Neurology', 'Orthopedics', 'Emergency', 'Pediatrics', 'Dermatology', 'Internal Medicine']} />
          <Input label="Clinician" value={form.clinician} onChange={(v: any) => setForm({ ...form, clinician: v })} placeholder="Dr. Sharma" />
        </div>

        {/* Clinical */}
        <h3 style={{ margin: '1.5rem 0 1rem', color: '#0F172A', display: 'flex', alignItems: 'center', gap: '0.5rem' }}><Stethoscope size={18} color="#3B82F6"/> Clinical Details</h3>
        <Input label="Chief Complaint *" value={form.chief_complaint} onChange={(v: any) => setForm({ ...form, chief_complaint: v })} placeholder="Severe chest pain radiating to left arm" full />
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginTop: '1rem' }}>
          <Input label="Symptoms (comma-separated)" value={form.symptoms} onChange={(v: any) => setForm({ ...form, symptoms: v })} placeholder="chest pain, shortness of breath, diaphoresis" />
          <Input label="Medical History" value={form.history} onChange={(v: any) => setForm({ ...form, history: v })} placeholder="Hypertension, Type 2 Diabetes" />
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginTop: '1rem' }}>
          <Input label="Current Medications (comma-separated)" value={form.current_medications} onChange={(v: any) => setForm({ ...form, current_medications: v })} placeholder="Metformin, Lisinopril" />
          <Input label="Allergies (comma-separated)" value={form.allergies} onChange={(v: any) => setForm({ ...form, allergies: v })} placeholder="Penicillin, Sulfa" />
        </div>

        {/* Vitals */}
        <h3 style={{ margin: '1.5rem 0 1rem', color: '#0F172A', display: 'flex', alignItems: 'center', gap: '0.5rem' }}><Heart size={18} color="#EF4444"/> Vital Signs</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
          <Input label="Systolic BP (mmHg)" value={form.vital_systolic} onChange={(v: any) => setForm({ ...form, vital_systolic: v })} placeholder="120" type="number" />
          <Input label="Diastolic BP (mmHg)" value={form.vital_diastolic} onChange={(v: any) => setForm({ ...form, vital_diastolic: v })} placeholder="80" type="number" />
          <Input label="Heart Rate (bpm)" value={form.vital_hr} onChange={(v: any) => setForm({ ...form, vital_hr: v })} placeholder="72" type="number" />
          <Input label="SpO2 (%)" value={form.vital_spo2} onChange={(v: any) => setForm({ ...form, vital_spo2: v })} placeholder="98" type="number" />
          <Input label="Temperature (°F)" value={form.vital_temp} onChange={(v: any) => setForm({ ...form, vital_temp: v })} placeholder="98.6" type="number" />
          <Input label="Respiratory Rate" value={form.vital_rr} onChange={(v: any) => setForm({ ...form, vital_rr: v })} placeholder="16" type="number" />
        </div>

        <div style={{ marginTop: '2rem', display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
          <button onClick={() => isEdit ? setIsEditingDetails(false) : setActiveView('list')} style={s.secondaryBtn}>Cancel</button>
          
          {isEdit ? (
              <button onClick={handleUpdate} disabled={!form.patient_name || loading === 'updating'} style={{ ...s.primaryBtn, opacity: !form.patient_name ? 0.5 : 1 }}>
                {loading === 'updating' ? <><RefreshCw size={16} className="spin"/> Saving...</> : <><Save size={16}/> Save Changes</>}
              </button>
          ) : (
              <button onClick={handleCreate} disabled={!form.patient_name || loading === 'creating'} style={{ ...s.primaryBtn, opacity: !form.patient_name ? 0.5 : 1 }}>
                {loading === 'creating' ? <><RefreshCw size={16} className="spin"/> Creating...</> : <><Plus size={16}/> Create Encounter</>}
              </button>
          )}
        </div>
      </div>
    </div>
    );
  };

  // ═══════════════════════════════════
  //  RENDER: Encounter Detail View
  // ═══════════════════════════════════
  const renderDetail = () => {
    if (!selectedEnc) return null;
    if (isEditingDetails) return renderCreateOrEdit();

    const enc = selectedEnc;
    const hasSoap = enc.soap && enc.soap.subjective;
    const confPct = Math.round((enc.ai_confidence || 0) * 100);
    const confColor = confPct >= 85 ? '#22C55E' : confPct >= 70 ? '#F59E0B' : '#EF4444';

    return (
      <div style={{ paddingBottom: '3rem' }}>
        {/* Anomaly Banner */}
        {anomalies.length > 0 && (
          <div style={{ background: '#FEF2F2', borderBottom: '1px solid #FCA5A5', padding: '0.75rem 1.5rem', marginBottom: '1rem', borderRadius: '0.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <AlertOctagon size={20} color="#DC2626"/>
                <span style={{ fontWeight: 600, color: '#991B1B' }}>{anomalies.length} clinical anomal{anomalies.length === 1 ? 'y' : 'ies'} detected</span>
              </div>
              <button onClick={() => setAnomalyExpanded(!anomalyExpanded)} style={{ background: 'transparent', border: 'none', cursor: 'pointer' }}>
                {anomalyExpanded ? <ChevronUp size={18}/> : <ChevronDown size={18}/>}
              </button>
            </div>
            {anomalyExpanded && <div style={{ marginTop: '0.75rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {anomalies.map((a: any, i: number) => (
                <div key={i} style={{ background: 'white', padding: '0.75rem', borderRadius: '0.5rem', border: '1px solid #E2E8F0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div><strong>{a.title}</strong><br/><span style={{ fontSize: '0.85rem', color: '#64748B' }}>{a.description}</span></div>
                  <button style={{ ...s.secondaryBtn, fontSize: '0.8rem' }}><CheckCircle size={14}/> Acknowledge</button>
                </div>
              ))}
            </div>}
          </div>
        )}

        {/* Header */}
        <div style={s.pageHeader}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <button onClick={() => { setActiveView('list'); setCdsData(null); setCdsOpen(false); setRxData(null); setAnomalies([]); }} style={{ ...s.secondaryBtn, padding: '0.4rem 0.6rem' }}>← Back</button>
            <div>
              <h1 style={s.pageTitle}>{enc.patient_name} <span style={{ fontSize: '0.9rem', color: '#64748B', fontWeight: 500 }}>({enc.id})</span></h1>
              <p style={s.pageSub}>{enc.age}yo {enc.gender} · {enc.department} · {enc.clinician}</p>
            </div>
          </div>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            <button onClick={handleRunCDS} disabled={loading === 'cds'} style={s.secondaryBtn}>
              {loading === 'cds' ? <><RefreshCw size={14}/> Running...</> : <><Activity size={14}/> Run CDS</>}
            </button>
            {!hasSoap && <button onClick={handleGenerateSOAP} disabled={loading === 'soap'} style={s.primaryBtn}>
              {loading === 'soap' ? <><RefreshCw size={14}/> Generating...</> : <><FileText size={14}/> Generate SOAP</>}
            </button>}
            {hasSoap && <button onClick={handleGenerateRx} disabled={loading === 'rx'} style={{ ...s.primaryBtn, background: 'linear-gradient(135deg, #8B5CF6, #7C3AED)' }}>
              {loading === 'rx' ? <><RefreshCw size={14}/> Generating...</> : <><Pill size={14}/> Generate Prescription</>}
            </button>}
            {hasSoap && enc.soap_status !== 'approved' && <button onClick={openSafetyConfirm} style={{ ...s.primaryBtn, background: 'linear-gradient(135deg, #22C55E, #16A34A)' }}>
              <Shield size={14}/> Approve SOAP
            </button>}
          </div>
        </div>

        {/* Two column layout */}
        <div style={{ display: 'grid', gridTemplateColumns: cdsOpen ? '1fr 340px' : '1fr', gap: '1.5rem' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {/* Patient Context Card */}
            <div style={s.card}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h3 style={{ margin: 0, fontSize: '1.05rem', color: '#0F172A', display: 'flex', alignItems: 'center', gap: '0.5rem' }}><User size={18} color="#3B82F6"/> Patient Context</h3>
                <button onClick={startEditingEncounter} style={{ ...s.secondaryBtn, padding: '0.3rem 0.6rem', fontSize: '0.8rem' }}><Edit3 size={14}/> Edit Details</button>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', fontSize: '0.9rem' }}>
                <div>
                  <p style={{ margin: '0.25rem 0' }}><strong>Chief Complaint:</strong> {enc.chief_complaint || 'N/A'}</p>
                  <p style={{ margin: '0.25rem 0' }}><strong>Symptoms:</strong> {(enc.symptoms || []).join(', ') || 'None'}</p>
                  <p style={{ margin: '0.25rem 0' }}><strong>History:</strong> {enc.history || 'None'}</p>
                  <p style={{ margin: '0.25rem 0' }}><strong>Allergies:</strong> {(enc.allergies || []).join(', ') || 'None'}</p>
                  <p style={{ margin: '0.25rem 0' }}><strong>Medications:</strong> {(enc.current_medications || []).join(', ') || 'None'}</p>
                </div>
                {enc.vital_signs && Object.keys(enc.vital_signs).length > 0 && (
                  <div style={{ background: '#F8FAFC', padding: '1rem', borderRadius: '0.5rem', border: '1px solid #E2E8F0' }}>
                    <strong style={{ display: 'block', marginBottom: '0.5rem' }}>Vital Signs</strong>
                    {enc.vital_signs.systolic_bp && <p style={{ margin: '0.15rem 0' }}>BP: {enc.vital_signs.systolic_bp}/{enc.vital_signs.diastolic_bp} mmHg
                      {enc.vital_signs.systolic_bp > 140 && <span style={{ color: '#DC2626', fontWeight: 'bold' }}> ⚠ HIGH</span>}
                    </p>}
                    {enc.vital_signs.heart_rate && <p style={{ margin: '0.15rem 0' }}>HR: {enc.vital_signs.heart_rate} bpm</p>}
                    {enc.vital_signs.spo2 && <p style={{ margin: '0.15rem 0' }}>SpO2: {enc.vital_signs.spo2}%
                      {enc.vital_signs.spo2 < 95 && <span style={{ color: '#D97706', fontWeight: 'bold' }}> ⚠ LOW</span>}
                    </p>}
                    {enc.vital_signs.temperature && <p style={{ margin: '0.15rem 0' }}>Temp: {enc.vital_signs.temperature}°F</p>}
                    {enc.vital_signs.respiratory_rate && <p style={{ margin: '0.15rem 0' }}>RR: {enc.vital_signs.respiratory_rate}</p>}
                  </div>
                )}
              </div>
            </div>

            {/* SOAP Note */}
            {hasSoap ? (
              <div style={{ ...s.card, border: soapEditing ? '2px solid #3B82F6' : '1px solid #E2E8F0', transition: 'border 0.2s' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                  <h3 style={s.cardTitle}>
                      <FileText size={18} color="#3B82F6"/> 
                      SOAP Note 
                      {soapEditing && <span style={{ fontSize: '0.75rem', background: '#DBEAFE', color: '#1D4ED8', padding: '0.2rem 0.5rem', borderRadius: '4px', marginLeft: '0.5rem' }}>EDIT MODE</span>}
                  </h3>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    {confPct > 0 && <span style={{ fontSize: '0.75rem', fontWeight: 700, color: confColor }}>AI Confidence: {confPct}%</span>}
                    <span style={{ fontSize: '0.7rem', fontWeight: 600, padding: '0.2rem 0.6rem', borderRadius: '9999px', background: enc.soap_status === 'approved' ? '#DCFCE7' : '#FEF9C3', color: enc.soap_status === 'approved' ? '#22C55E' : '#F59E0B' }}>{(enc.soap_status || '').replace('_', ' ')}</span>
                    {!soapEditing && <button onClick={() => setSoapEditing(true)} style={s.secondaryBtn}><Edit3 size={14}/> Edit</button>}
                    {soapEditing && <button onClick={handleSaveSOAP} disabled={loading === 'saving'} style={s.primaryBtn}><Save size={14}/> {loading === 'saving' ? 'Saving...' : 'Save Changes'}</button>}
                    {soapEditing && <button onClick={() => setSoapEditing(false)} style={s.secondaryBtn}><X size={14}/> Cancel</button>}
                  </div>
                </div>
                {['subjective', 'objective', 'assessment', 'plan'].map(section => (
                  <div key={section} style={{ marginBottom: '1rem' }}>
                    <label style={{ fontSize: '0.75rem', fontWeight: 700, color: '#3B82F6', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{section.charAt(0).toUpperCase() + section.slice(1)}</label>
                    {soapEditing ? (
                      <textarea value={(soapDraft as any)[section]} onChange={(e: any) => setSoapDraft({ ...soapDraft, [section]: e.target.value })}
                        style={{ width: '100%', minHeight: '80px', padding: '0.75rem', border: '1px solid #93C5FD', borderRadius: '0.5rem', fontSize: '0.9rem', resize: 'vertical', marginTop: '0.25rem', outline: 'none', background: '#FAFAFA' }} />
                    ) : (
                      <p style={{ margin: '0.25rem 0 0', fontSize: '0.9rem', color: '#334155', lineHeight: 1.6, whiteSpace: 'pre-wrap' }}>{(enc.soap as any)[section] || 'N/A'}</p>
                    )}
                  </div>
                ))}
                {enc.icd_codes?.length > 0 && (
                  <div style={{ marginTop: '0.5rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap', alignItems: 'center' }}>
                    <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#64748B' }}>ICD Codes:</span>
                    {enc.icd_codes.map((c: string) => <span key={c} style={{ fontSize: '0.75rem', fontWeight: 600, padding: '0.15rem 0.5rem', borderRadius: '0.25rem', background: '#EFF6FF', color: '#2563EB', fontFamily: 'monospace' }}>{c}</span>)}
                  </div>
                )}
              </div>
            ) : (
              <div style={{ ...s.card, textAlign: 'center', padding: '3rem' }}>
                <FileText size={40} style={{ color: '#CBD5E1', margin: '0 auto 1rem' }}/>
                <h3 style={{ color: '#64748B', margin: '0 0 0.5rem' }}>No SOAP Note Generated</h3>
                <p style={{ color: '#94A3B8', fontSize: '0.9rem', marginBottom: '1.5rem' }}>Click "Generate SOAP" to use AI to create a structured clinical note.</p>
                <button onClick={handleGenerateSOAP} disabled={loading === 'soap'} style={s.primaryBtn}>
                  {loading === 'soap' ? 'Generating...' : <><FileText size={14}/> Generate SOAP Note</>}
                </button>
              </div>
            )}

            {/* Prescriptions */}
            {rxData && rxData.prescriptions && (
              <div style={s.card}>
                <h3 style={s.cardTitle}><Pill size={18} color="#8B5CF6"/> AI-Generated Prescriptions</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {rxData.prescriptions.map((rx: any, i: number) => (
                    <div key={i} style={{ padding: '1rem', border: '1px solid #E2E8F0', borderRadius: '0.5rem', background: '#FAFBFC' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <strong style={{ color: '#0F172A' }}>{rx.medication}</strong>
                        <span style={{ fontSize: '0.75rem', background: '#EDE9FE', color: '#7C3AED', padding: '0.15rem 0.5rem', borderRadius: '0.25rem', fontWeight: 600 }}>{rx.route}</span>
                      </div>
                      <p style={{ margin: '0.5rem 0 0', fontSize: '0.85rem', color: '#475569' }}>
                        {rx.dosage} · {rx.frequency} · {rx.duration}
                      </p>
                      {rx.notes && <p style={{ margin: '0.25rem 0 0', fontSize: '0.8rem', color: '#94A3B8', fontStyle: 'italic' }}>{rx.notes}</p>}
                    </div>
                  ))}
                </div>
                {rxData.contraindications?.length > 0 && (
                  <div style={{ marginTop: '1rem', padding: '0.75rem', background: '#FEF2F2', borderRadius: '0.5rem', border: '1px solid #FECACA' }}>
                    <strong style={{ color: '#DC2626', fontSize: '0.85rem' }}>⚠ Contraindications:</strong>
                    <ul style={{ margin: '0.5rem 0 0', paddingLeft: '1.25rem' }}>
                      {rxData.contraindications.map((c: string, i: number) => <li key={i} style={{ fontSize: '0.85rem', color: '#991B1B' }}>{c}</li>)}
                    </ul>
                  </div>
                )}
                {rxData.drug_interactions?.length > 0 && (
                  <div style={{ marginTop: '0.75rem', padding: '0.75rem', background: '#FFFBEB', borderRadius: '0.5rem', border: '1px solid #FCD34D' }}>
                    <strong style={{ color: '#D97706', fontSize: '0.85rem' }}>⚠ Drug Interactions:</strong>
                    <ul style={{ margin: '0.5rem 0 0', paddingLeft: '1.25rem' }}>
                      {rxData.drug_interactions.map((d: string, i: number) => <li key={i} style={{ fontSize: '0.85rem', color: '#92400E' }}>{d}</li>)}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* CDS Advisory Panel */}
          {cdsOpen && cdsData && (
            <div style={{ background: 'white', borderRadius: '0.75rem', border: '1px solid #E2E8F0', overflow: 'hidden', height: 'fit-content', position: 'sticky', top: '1rem' }}>
              <div style={{ padding: '1rem', borderBottom: '1px solid #E2E8F0', display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#F8FAFC' }}>
                <h3 style={{ margin: 0, fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}><Info size={18} color="#3B82F6"/> Clinical Advisory</h3>
                <button onClick={() => setCdsOpen(false)} style={{ background: 'none', border: 'none', cursor: 'pointer' }}><X size={18} color="#94A3B8"/></button>
              </div>
              <div style={{ padding: '0.75rem', display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: '70vh', overflowY: 'auto' }}>
                {(cdsData.alerts || []).map((alert: any, i: number) => {
                  const isEmergency = alert.priority === 'emergency';
                  return (
                    <div key={i} style={{ padding: '0.75rem', borderRadius: '0.5rem', borderLeft: `3px solid ${isEmergency ? '#DC2626' : alert.category === 'guideline' ? '#22C55E' : '#3B82F6'}`, background: '#FAFBFC' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.25rem' }}>
                        <strong style={{ fontSize: '0.85rem', color: isEmergency ? '#DC2626' : '#0F172A' }}>{alert.title}</strong>
                        <span style={{ fontSize: '0.6rem', background: '#F1F5F9', padding: '0.1rem 0.35rem', borderRadius: '0.25rem', color: '#64748B', whiteSpace: 'nowrap' }}>{alert.source}</span>
                      </div>
                      <p style={{ fontSize: '0.8rem', color: '#475569', margin: '0.25rem 0 0.5rem', lineHeight: 1.5 }}>{alert.description}</p>
                      {alert.actions?.map((action: any, j: number) => (
                        <button key={j} style={{ width: '100%', padding: '0.4rem', background: '#EFF6FF', color: '#1D4ED8', border: '1px solid #BFDBFE', borderRadius: '0.25rem', fontWeight: 500, cursor: 'pointer', fontSize: '0.8rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.25rem' }}>
                          <CheckCircle size={14}/> {action.label}
                        </button>
                      ))}
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* Safety Confirmation Dialog */}
        {confirmDialog && (
          <div style={{ position: 'fixed', inset: 0, background: 'rgba(15,23,42,0.7)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div style={{ background: 'white', borderRadius: '1rem', width: '100%', maxWidth: '550px', overflow: 'hidden', boxShadow: '0 25px 50px -12px rgba(0,0,0,0.25)' }}>
              <div style={{ padding: '1.25rem', borderBottom: '1px solid #E2E8F0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h2 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1.15rem' }}><Shield size={20} color="#3B82F6"/> Review & Approve Clinical Data</h2>
                <ConfRing score={confirmDialog.confidence}/>
              </div>
              <div style={{ padding: '1.25rem', background: '#F8FAFC' }}>
                <div style={{ background: 'white', border: '1px solid #E2E8F0', borderRadius: '0.5rem', padding: '1rem' }}>
                  {Object.entries(confirmDialog.fields || {}).map(([k, v]: any) => (
                    <div key={k} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem 0', borderBottom: '1px solid #F1F5F9' }}>
                      <span style={{ fontWeight: 600, color: '#475569' }}>{k}</span>
                      <span style={{ color: '#0F172A', maxWidth: '60%', textAlign: 'right' }}>{v}</span>
                    </div>
                  ))}
                </div>
              </div>
              <div style={{ padding: '1.25rem', display: 'flex', gap: '0.75rem', justifyContent: 'flex-end' }}>
                <button onClick={() => { setConfirmDialog(null); showToast('Approval Rejected'); }} style={{ ...s.secondaryBtn, color: '#DC2626' }}><XCircle size={16}/> Reject</button>
                <button onClick={() => { setSoapEditing(true); setConfirmDialog(null); showToast('Switched to Edit Mode'); }} style={s.secondaryBtn}><Edit3 size={16}/> Modify</button>
                <button onClick={handleSaveSOAP} style={{ ...s.primaryBtn, background: 'linear-gradient(135deg, #22C55E, #16A34A)' }}><CheckCircle size={16}/> Approve & Save</button>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div style={{ opacity: mounted ? 1 : 0, transition: 'opacity 0.4s', position: 'relative' }}>
      {/* Toast Notification */}
      {toast && (
          <div style={{ position: 'fixed', top: '1.5rem', left: '50%', transform: 'translateX(-50%)', background: '#10B981', color: 'white', padding: '0.75rem 1.5rem', borderRadius: '9999px', fontWeight: 600, boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)', zIndex: 9999, display: 'flex', alignItems: 'center', gap: '0.5rem', animation: 'fadeInDown 0.3s' }}>
              <CheckCircle size={18} /> {toast}
          </div>
      )}

      {activeView === 'list' && renderList()}
      {activeView === 'create' && renderCreateOrEdit()}
      {activeView === 'detail' && renderDetail()}
    </div>
  );
}

// ── Reusable Components ──

function Input({ label, value, onChange, placeholder, type, full }: any) {
  return (
    <div style={full ? { gridColumn: '1 / -1' } : {}}>
      <label style={{ fontSize: '0.75rem', fontWeight: 600, color: '#475569', display: 'block', marginBottom: '0.25rem' }}>{label}</label>
      <input type={type || 'text'} value={value} onChange={(e: any) => onChange(e.target.value)} placeholder={placeholder}
        style={{ width: '100%', padding: '0.6rem 0.75rem', border: '1px solid #CBD5E1', borderRadius: '0.5rem', fontSize: '0.9rem', outline: 'none', transition: 'border 0.2s', boxSizing: 'border-box' }} />
    </div>
  );
}

function Select({ label, value, onChange, options }: any) {
  return (
    <div>
      <label style={{ fontSize: '0.75rem', fontWeight: 600, color: '#475569', display: 'block', marginBottom: '0.25rem' }}>{label}</label>
      <select value={value} onChange={(e: any) => onChange(e.target.value)}
        style={{ width: '100%', padding: '0.6rem 0.75rem', border: '1px solid #CBD5E1', borderRadius: '0.5rem', fontSize: '0.9rem', background: 'white', cursor: 'pointer', boxSizing: 'border-box' }}>
        {options.map((o: string) => <option key={o} value={o}>{o}</option>)}
      </select>
    </div>
  );
}

function ConfRing({ score }: { score: number }) {
  const pct = Math.round(score * 100);
  const color = score >= 0.85 ? '#22C55E' : score >= 0.7 ? '#F59E0B' : '#EF4444';
  const r = 16; const c = r * 2 * Math.PI; const off = c - score * c;
  return (
    <div style={{ position: 'relative', width: 40, height: 40 }} title={`AI Confidence: ${pct}%`}>
      <svg width={40} height={40} style={{ transform: 'rotate(-90deg)' }}>
        <circle cx={20} cy={20} r={r} fill="none" stroke="#e2e8f0" strokeWidth={3}/>
        <circle cx={20} cy={20} r={r} fill="none" stroke={color} strokeWidth={3} strokeDasharray={c} strokeDashoffset={off} strokeLinecap="round" style={{ transition: 'stroke-dashoffset 1s' }}/>
      </svg>
      <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.65rem', fontWeight: 700, color: '#475569' }}>{pct}%</div>
    </div>
  );
}

const s: Record<string, React.CSSProperties> = {
  pageHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' },
  pageTitle: { fontSize: '1.6rem', fontWeight: 800, color: '#0F172A', letterSpacing: '-0.03em', margin: 0 },
  pageSub: { fontSize: '0.85rem', color: '#64748B', marginTop: '0.2rem' },
  primaryBtn: { display: 'flex', alignItems: 'center', gap: '0.4rem', padding: '0.55rem 1.1rem', borderRadius: '0.5rem', border: 'none', background: 'linear-gradient(135deg, #3B82F6, #2563EB)', color: 'white', fontSize: '0.85rem', fontWeight: 600, cursor: 'pointer', whiteSpace: 'nowrap' as const },
  secondaryBtn: { display: 'flex', alignItems: 'center', gap: '0.4rem', padding: '0.55rem 1.1rem', borderRadius: '0.5rem', border: '1px solid #CBD5E1', background: '#F8FAFC', color: '#334155', fontSize: '0.85rem', fontWeight: 600, cursor: 'pointer', whiteSpace: 'nowrap' as const },
  card: { background: 'white', borderRadius: '0.75rem', border: '1px solid #E2E8F0', padding: '1.5rem' },
  cardTitle: { margin: '0 0 1rem', fontSize: '1.05rem', color: '#0F172A', display: 'flex', alignItems: 'center', gap: '0.5rem' },
};
