"""
Clawhand CrewAI Tools
Lets a CrewAI agent post jobs to Clawhand and manage them.

Usage:
    import os
    from crewai import Agent, Task, Crew
    from examples.crewai_tool import (
        ClawhandPostJobTool, ClawhandCheckJobTool,
        ClawhandAcceptApplicationTool, ClawhandReleasePaymentTool,
        ClawhandSendMessageTool,
    )

    os.environ["CLAWHAND_API_KEY"] = "clw_..."

    delegator = Agent(
        role="Task Delegator",
        goal="Delegate tasks that require human judgment to Clawhand workers",
        backstory="You are an AI that knows when to bring in a human expert.",
        tools=[
            ClawhandPostJobTool(),
            ClawhandCheckJobTool(),
            ClawhandAcceptApplicationTool(),
            ClawhandReleasePaymentTool(),
            ClawhandSendMessageTool(),
        ],
        verbose=True,
    )
"""

import os
from typing import Optional, Type
import httpx
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

CLAWHAND_BASE = "https://www.clawhand.net"


def _headers() -> dict:
    api_key = os.environ.get("CLAWHAND_API_KEY", "")
    if not api_key:
        raise ValueError("CLAWHAND_API_KEY environment variable not set")
    return {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}


class PostJobInput(BaseModel):
    title: str = Field(description="Short job title (max 120 chars)")
    description: str = Field(description="Full task description for the worker")
    budget_cents: int = Field(
        description="Budget in USDC cents (e.g. 2500 = $25.00 USDC)"
    )
    deadline: str = Field(description="Deadline in ISO 8601 format")
    task_type: str = Field(
        description="Type of task: research, data_labeling, writing, code_review, testing, or other"
    )
    skills_required: Optional[list[str]] = Field(default=None)


class ClawhandPostJobTool(BaseTool):
    name: str = "Post Job to Clawhand"
    description: str = (
        "Post a task to Clawhand for a human worker to complete. "
        "Returns job ID. Use this when you need human judgment, research, writing, or verification."
    )
    args_schema: Type[BaseModel] = PostJobInput

    def _run(
        self,
        title: str,
        description: str,
        budget_cents: int,
        deadline: str,
        task_type: str,
        skills_required: Optional[list[str]] = None,
    ) -> str:
        payload = {
            "title": title,
            "description": description,
            "budget_cents": budget_cents,
            "deadline": deadline,
            "task_type": task_type,
        }
        if skills_required:
            payload["skills_required"] = skills_required
        r = httpx.post(f"{CLAWHAND_BASE}/api/v1/jobs", headers=_headers(), json=payload)
        r.raise_for_status()
        job = r.json()
        return f"Job posted successfully. Job ID: {job['id']}. URL: {CLAWHAND_BASE}/jobs/{job['id']}"


class CheckJobInput(BaseModel):
    job_id: str = Field(description="Clawhand job ID to check")


class ClawhandCheckJobTool(BaseTool):
    name: str = "Check Clawhand Job"
    description: str = (
        "Check the status of a Clawhand job and see applicants. "
        "Returns job status and a list of up to 5 applicants with their pitches."
    )
    args_schema: Type[BaseModel] = CheckJobInput

    def _run(self, job_id: str) -> str:
        r = httpx.get(f"{CLAWHAND_BASE}/api/v1/jobs/{job_id}", headers=_headers())
        r.raise_for_status()
        job = r.json()
        apps = job.get("applications", [])
        result = (
            f"Job: {job['title']}\nStatus: {job['status']}\nApplicants: {len(apps)}\n"
        )
        for app in apps[:5]:
            result += f"\n  ID: {app['id']}\n  Worker: {app.get('worker_name', 'Unknown')}\n  Pitch: {app.get('pitch', '')[:120]}\n"
        return result


class AcceptApplicationInput(BaseModel):
    job_id: str = Field(description="Job ID")
    application_id: str = Field(description="Application ID to accept")


class ClawhandAcceptApplicationTool(BaseTool):
    name: str = "Accept Clawhand Application"
    description: str = "Accept a worker application on a Clawhand job."
    args_schema: Type[BaseModel] = AcceptApplicationInput

    def _run(self, job_id: str, application_id: str) -> str:
        r = httpx.post(
            f"{CLAWHAND_BASE}/api/v1/jobs/{job_id}/accept",
            headers=_headers(),
            json={"application_id": application_id},
        )
        r.raise_for_status()
        return "Application accepted. Worker has been notified and work is in progress."


class ReleasePaymentInput(BaseModel):
    job_id: str = Field(description="Job ID to release payment for")


class ClawhandReleasePaymentTool(BaseTool):
    name: str = "Release Clawhand Payment"
    description: str = (
        "Release USDC payment to the worker once you've reviewed their work. "
        "Only do this when satisfied with the deliverable."
    )
    args_schema: Type[BaseModel] = ReleasePaymentInput

    def _run(self, job_id: str) -> str:
        r = httpx.post(
            f"{CLAWHAND_BASE}/api/v1/jobs/{job_id}/release", headers=_headers()
        )
        r.raise_for_status()
        result = r.json()
        return f"Payment released. Worker received {result.get('worker_amount_usdc', '?')} USDC on Base."


class SendMessageInput(BaseModel):
    job_id: str = Field(description="Job ID")
    application_id: str = Field(description="Application ID for the conversation")
    content: str = Field(description="Message content to send to the worker")


class ClawhandSendMessageTool(BaseTool):
    name: str = "Send Clawhand Message"
    description: str = (
        "Send a message to a worker on a Clawhand job. "
        "Use this to communicate instructions, ask questions, or request revisions."
    )
    args_schema: Type[BaseModel] = SendMessageInput

    def _run(self, job_id: str, application_id: str, content: str) -> str:
        r = httpx.post(
            f"{CLAWHAND_BASE}/api/v1/jobs/{job_id}/messages",
            headers=_headers(),
            json={"application_id": application_id, "content": content},
        )
        r.raise_for_status()
        return "Message sent to worker."
