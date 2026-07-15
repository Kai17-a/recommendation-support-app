from app.main import app


def test_all_required_api_endpoints_are_exposed() -> None:
    required = {
        ("GET", "/api/v1/me"),
        ("GET", "/api/v1/members"),
        ("POST", "/api/v1/members"),
        ("GET", "/api/v1/members/{member_id}"),
        ("PATCH", "/api/v1/members/{member_id}"),
        ("DELETE", "/api/v1/members/{member_id}"),
        ("POST", "/api/v1/members/{member_id}/restore"),
        ("GET", "/api/v1/members/{member_id}/projects"),
        ("POST", "/api/v1/members/{member_id}/projects"),
        ("GET", "/api/v1/projects/{project_id}"),
        ("PATCH", "/api/v1/projects/{project_id}"),
        ("DELETE", "/api/v1/projects/{project_id}"),
        ("GET", "/api/v1/projects/{project_id}/reports"),
        ("POST", "/api/v1/projects/{project_id}/reports"),
        ("GET", "/api/v1/reports/{report_id}"),
        ("PATCH", "/api/v1/reports/{report_id}"),
        ("DELETE", "/api/v1/reports/{report_id}"),
        ("POST", "/api/v1/projects/{project_id}/markdown-imports"),
        ("GET", "/api/v1/markdown-imports/{import_id}"),
        ("GET", "/api/v1/markdown-imports/{import_id}/warnings"),
        ("PATCH", "/api/v1/markdown-import-warnings/{warning_id}"),
        ("POST", "/api/v1/projects/{project_id}/analyses"),
        ("GET", "/api/v1/ai-jobs/{job_id}"),
        ("GET", "/api/v1/ai-analyses/{analysis_id}"),
        ("PATCH", "/api/v1/ai-analyses/{analysis_id}"),
        ("GET", "/api/v1/members/{member_id}/evaluations"),
        ("POST", "/api/v1/members/{member_id}/evaluations"),
        ("PATCH", "/api/v1/evaluations/{evaluation_id}"),
        ("DELETE", "/api/v1/evaluations/{evaluation_id}"),
        ("GET", "/api/v1/members/{member_id}/skills"),
        ("POST", "/api/v1/members/{member_id}/skills"),
        ("PATCH", "/api/v1/member-skills/{id}"),
        ("DELETE", "/api/v1/member-skills/{id}"),
        ("GET", "/api/v1/member-skills/{id}/evidences"),
        ("GET", "/api/v1/recommendations"),
        ("POST", "/api/v1/recommendations"),
        ("GET", "/api/v1/recommendations/{id}"),
        ("PATCH", "/api/v1/recommendations/{id}"),
        ("DELETE", "/api/v1/recommendations/{id}"),
        ("POST", "/api/v1/recommendations/{id}/generate"),
        ("GET", "/api/v1/recommendations/{id}/versions"),
        ("GET", "/api/v1/recommendation-versions/{version_id}"),
        ("PATCH", "/api/v1/recommendation-versions/{version_id}"),
        ("POST", "/api/v1/recommendations/{id}/finalize"),
        ("GET", "/api/v1/recommendation-versions/{version_id}/evidences"),
        ("GET", "/api/v1/admin/ai-settings"),
        ("PATCH", "/api/v1/admin/ai-settings"),
        ("GET", "/api/v1/admin/retention-policies"),
        ("PATCH", "/api/v1/admin/retention-policies/{policy_id}"),
        ("GET", "/api/v1/admin/audit-logs"),
        ("GET", "/api/v1/admin/deleted-records"),
        ("POST", "/api/v1/admin/deleted-records/{target_type}/{target_id}/restore"),
        ("POST", "/api/v1/admin/deleted-records/{target_type}/{target_id}/purge"),
    }
    actual = {
        (method.upper(), path)
        for path, operations in app.openapi()["paths"].items()
        for method in operations
        if method != "parameters"
    }
    assert required <= actual
    assert len(required) == 53
