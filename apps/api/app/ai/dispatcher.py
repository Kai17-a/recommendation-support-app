from typing import Protocol
from uuid import UUID


class ProjectAnalysisDispatcher(Protocol):
    def enqueue_project_analysis(self, job_id: UUID) -> None: ...


class RecommendationGenerationDispatcher(Protocol):
    def enqueue_recommendation_generation(self, job_id: UUID) -> None: ...


class MarkdownImportDispatcher(Protocol):
    def enqueue_markdown_import(self, job_id: UUID) -> None: ...


class DramatiqAiJobDispatcher:
    def enqueue_project_analysis(self, job_id: UUID) -> None:
        from app.ai.tasks import run_project_analysis

        run_project_analysis.send(str(job_id))

    def enqueue_recommendation_generation(self, job_id: UUID) -> None:
        from app.ai.tasks import run_recommendation_generation

        run_recommendation_generation.send(str(job_id))

    def enqueue_markdown_import(self, job_id: UUID) -> None:
        from app.markdown_imports.tasks import run_markdown_import

        run_markdown_import.send(str(job_id))
