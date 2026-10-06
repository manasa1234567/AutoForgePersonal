import React, { useState } from 'react';
import { TrainingProgram, SessionAttendance, AttendanceRecord } from '../types/types';
import '../styles/attendanceList.css';

interface Props {
  programs: TrainingProgram[];
  onAttendancesUpdated: () => void;
}

export default function AttendanceList({ programs, onAttendancesUpdated }: Props) {
  const [selectedProgramId, setSelectedProgramId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [attendanceData, setAttendanceData] = useState<SessionAttendance | null>(null);

  const loadAttendance = async (programId: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`/api/programs/${programId}/attendance`);
      if (!response.ok) throw new Error('Failed to load attendance data');
      const data = await response.json();
      setAttendanceData(data);
      setSelectedProgramId(programId);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const toggleAttendance = async (recordId: string, currentStatus: boolean) => {
    if (!selectedProgramId) return;
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `/api/programs/${selectedProgramId}/attendance/${recordId}`,
        { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ present: !currentStatus }) }
      );
      if (!response.ok) throw new Error('Failed to update attendance');
      await loadAttendance(selectedProgramId);
      onAttendancesUpdated();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section aria-label="Attendance management" className="attendance-list">
      <h2>Mark Attendance</h2>
      <select
        aria-label="Select program to manage attendance"
        value={selectedProgramId ?? ''}
        onChange={e => loadAttendance(e.target.value)}
      >
        <option value="">Select a program</option>
        {programs.map(p => (
          <option key={p.id} value={p.id}>{p.title}</option>
        ))}
      </select>

      {loading && <p>Loading attendance data...</p>}
      {error && <p role="alert">Error: {error}</p>}

      {attendanceData && (
        <table className="attendance-table">
          <caption>Attendance for session: {attendanceData.sessionTitle}</caption>
          <thead>
            <tr>
              <th>Participant</th>
              <th>Present</th>
            </tr>
          </thead>
          <tbody>
            {attendanceData.records.map(record => (
              <tr key={record.id}>
                <td>{record.participantName}</td>
                <td>
                  <input
                    type="checkbox"
                    checked={record.present}
                    onChange={() => toggleAttendance(record.id, record.present)}
                    aria-label={`Mark attendance for ${record.participantName}`}
                  />
                </td>
              </tr>
            ))}
            {attendanceData.records.length === 0 && <tr><td colSpan={2}>No participants found</td></tr>}
          </tbody>
        </table>
      )}
    </section>
  );
}
