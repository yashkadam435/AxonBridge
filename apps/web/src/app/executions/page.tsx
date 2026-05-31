"use client";

import React from 'react';
import { Activity, CheckCircle, Clock } from 'lucide-react';

export default function ExecutionsPage() {
  const executions = [
    {
      id: "exec-1049",
      workflow_name: "Patient Registration (Inpatient)",
      his_target: "eHospital",
      status: "running",
      progress: "3/8",
      start_time: "2 mins ago"
    }
  ];

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Workflow Executions</h1>
          <p className="text-muted-foreground">Monitor automated workflow execution progress.</p>
        </div>
      </div>

      <div className="border rounded-lg bg-card">
        <div className="p-0">
          <table className="w-full text-sm text-left">
            <thead className="text-xs uppercase bg-muted/50 border-b">
              <tr>
                <th className="px-6 py-3">ID</th>
                <th className="px-6 py-3">Workflow</th>
                <th className="px-6 py-3">Target</th>
                <th className="px-6 py-3">Status</th>
                <th className="px-6 py-3">Progress</th>
                <th className="px-6 py-3">Started</th>
              </tr>
            </thead>
            <tbody>
              {executions.map(exec => (
                <tr key={exec.id} className="border-b last:border-0 hover:bg-muted/30">
                  <td className="px-6 py-4 font-mono text-xs">{exec.id}</td>
                  <td className="px-6 py-4 font-medium">{exec.workflow_name}</td>
                  <td className="px-6 py-4">{exec.his_target}</td>
                  <td className="px-6 py-4">
                    <span className="flex items-center gap-1 text-blue-600 dark:text-blue-400">
                      <Activity className="w-4 h-4 animate-pulse" />
                      {exec.status}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <div className="w-full bg-muted rounded-full h-2 max-w-[100px]">
                        <div className="bg-primary h-2 rounded-full" style={{ width: '37.5%' }}></div>
                      </div>
                      <span className="text-xs text-muted-foreground">{exec.progress}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 flex items-center gap-1 text-muted-foreground">
                    <Clock className="w-3 h-3" />
                    {exec.start_time}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
