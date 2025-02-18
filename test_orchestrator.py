# test_orchestrator.py
import pytest
from agents.orchestrator import Orchestrator

def test_workflow():
    orchestrator = Orchestrator()
    result = orchestrator.create_workflow("fitness tech")
    assert "content_plan" in result
    assert len(result["content_plan"]) > 0


test_workflow()