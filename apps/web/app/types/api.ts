export interface Member {
  id: string;
  department_id: string;
  manager_user_id: string;
  name: string;
  status: string;
}

export interface Project {
  id: string;
  member_id: string;
  project_name: string;
  customer_name: string | null;
  status: string;
  overview: string | null;
}

export interface AiJob {
  id: string;
  status: string;
  job_type: string;
  error_message: string | null;
}

export interface MarkdownImport {
  import_id: string;
  job_id: string;
  status: string;
  project_report_id: string | null;
  warning_count: number;
  extracted_skill_count: number;
}

export interface Recommendation {
  id: string;
  member_id: string;
  purpose: string;
  target_name: string | null;
  status: string;
  finalized_at: string | null;
}

export interface RecommendationVersion {
  id: string;
  recommendation_id: string;
  version_no: number;
  version_type: string;
  content: string;
  created_at: string;
}
