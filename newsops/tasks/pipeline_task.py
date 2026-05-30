import asyncio
import logging

from celery_app import celery

logger = logging.getLogger(__name__)


@celery.task(bind=True, name="run_pipeline", max_retries=1)
def run_pipeline_task(self, parsed_input: dict, input_type: str, session_id: str):
    """
    Celery task that runs the NewsOps async pipeline synchronously.

    Args:
        parsed_input: Dict with keys like 'content', 'domain', 'file_bytes' etc.
        input_type:   One of 'text', 'url', 'pdf', 'docx', 'csv', 'excel',
                      'multi_document'.
        session_id:   UUID string that links this job to the AnalysisSession row.

    Returns:
        The serialisable result dict produced by Orchestrator.run().
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        from agents.orchestrator import Orchestrator
        orchestrator = Orchestrator()
        result = loop.run_until_complete(
            orchestrator.run(parsed_input, input_type, session_id)
        )
        return result
    except Exception as exc:
        logger.exception("Pipeline task failed for session %s: %s", session_id, exc)
        try:
            loop.close()
        except Exception:
            pass
        # Retry once after 5 seconds
        raise self.retry(exc=exc, countdown=5)
    finally:
        try:
            loop.close()
        except Exception:
            pass
