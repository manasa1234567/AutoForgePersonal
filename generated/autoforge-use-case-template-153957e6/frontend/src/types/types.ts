export interface TrainingProgram {
  id: string;
  title: string;
  description?: string;
  completionPercentage: number; // 0-100
}

export interface Session {
  sessionId: string;
  programId: string;
  title: string;
  start: string; // ISO date
  capacity: number;
  registeredCount: number;
}

export interface SessionAttendance {
  sessionId: string;
  sessionTitle: string;
  records: AttendanceRecord[];
}

export interface AttendanceRecord {
  id: string;
  participantId: string;
  participantName: string;
  present: boolean;
}

export interface FeedbackSubmission {
  rating: number;
  comments?: string;
}

export interface LearnerAnalytics {
  id: string;
  name: string;
  completionRate: number;
}

export interface AnalyticsData {
  totalLearners: number;
  activePrograms: number;
  completionRate: number;
  upcomingSessions: Session[];
  attendanceTrend: { label: string; value: number }[];
  feedbackRatings: { label: string; value: number }[];
  recentActivities: string[];
  topPerformers: LearnerAnalytics[];
  notifications: string[];
}
