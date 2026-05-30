import json
import logging
from typing import Type, TypeVar, Dict
from pydantic import BaseModel, ValidationError

from utils.gemini_client import call_gemini

T = TypeVar("T", bound=BaseModel)

logger = logging.getLogger(__name__)

# Simple in-memory stats tracker for debug purposes
validation_stats: Dict[str, Dict[str, int]] = {
    "ingestion": {"success": 0, "retry_1": 0, "retry_2": 0, "failed": 0},
    "analysis": {"success": 0, "retry_1": 0, "retry_2": 0, "failed": 0},
    "decision": {"success": 0, "retry_1": 0, "retry_2": 0, "failed": 0},
    "research": {"success": 0, "retry_1": 0, "retry_2": 0, "failed": 0},
}

class AgentValidationError(Exception):
    def __init__(self, agent: str, raw_response: str, validation_errors: str):
        self.agent = agent
        self.raw_response = raw_response
        self.validation_errors = validation_errors
        super().__init__(f"Agent {agent} failed validation after all retries. Errors: {validation_errors}")

def _record_stat(agent_name: str, outcome: str):
    if agent_name in validation_stats:
        validation_stats[agent_name][outcome] += 1

async def call_gemini_validated(
    system_prompt: str,
    user_message: str,
    output_model: Type[T],
    model: str = None,
    max_retries: int = 3,
    session_id: str = None,
    agent_name: str = "unknown",
) -> T:
    # Attempt 1: Normal call
    raw_response = await call_gemini(
        system_prompt=system_prompt,
        user_message=user_message,
        model=model,
        expect_json=True
    )
    
    try:
        if isinstance(raw_response, str):
            parsed = output_model.model_validate_json(raw_response)
        else:
            parsed = output_model.model_validate(raw_response)
        _record_stat(agent_name, "success")
        return parsed
    except ValidationError as e1:
        logger.warning(f"Agent {agent_name} validation error on attempt 1: {e1}")
        
    # Attempt 2: Retry with amended prompt
    amended_prompt = user_message + f"\n\nYour previous response had these validation errors: {e1.json()}\n" \
                                    f"Please fix ONLY the fields mentioned and return corrected JSON matching the schema."
                                    
    raw_response_2 = await call_gemini(
        system_prompt=system_prompt,
        user_message=amended_prompt,
        model=model,
        expect_json=True
    )
    
    try:
        if isinstance(raw_response_2, str):
            parsed = output_model.model_validate_json(raw_response_2)
        else:
            parsed = output_model.model_validate(raw_response_2)
        _record_stat(agent_name, "retry_1")
        return parsed
    except ValidationError as e2:
        logger.warning(f"Agent {agent_name} validation error on attempt 2: {e2}")

    # Attempt 3 (or fallback): model_construct lenient mode for partial data
    try:
        raw_dict = raw_response_2 if isinstance(raw_response_2, dict) else json.loads(raw_response_2)
        parsed_lenient = output_model.model_construct(**raw_dict)
        logger.info(f"Agent {agent_name} used lenient parsing on session {session_id}")
        _record_stat(agent_name, "retry_2")
        return parsed_lenient
    except Exception as fallback_e:
        logger.error(f"Agent {agent_name} lenient parsing failed: {fallback_e}")
    
    _record_stat(agent_name, "failed")
    raise AgentValidationError(
        agent=agent_name,
        raw_response=str(raw_response_2),
        validation_errors=str(e2)
    )
