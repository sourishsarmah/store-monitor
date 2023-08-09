from app.core.celery_app import celery_app
from app.services.report import ReportGenerator


@celery_app.task(acks_late=True)
def test_celery(word: str) -> str:
    return f"test task return {word}"


@celery_app.task(name="generate_report")
def generate_report():
    result = ReportGenerator.process()
    return result
