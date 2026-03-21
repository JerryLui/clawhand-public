"""
Clawhand LangChain Tools
Lets a LangChain agent post jobs and check on them via Clawhand's API.

Usage:
    from examples.langchain_tool import (
        PostJobTool, CheckJobTool, AcceptApplicationTool,
        ReleasePaymentTool, SendMessageTool,
    )

    tools = [
        PostJobTool(api_key="clw_..."),
        CheckJobTool(api_key="clw_..."),
        AcceptApplicationTool(api_key="clw_..."),
        ReleasePaymentTool(api_key="clw_..."),
        SendMessageTool(api_key="clw_..."),
    ]
"""

import json
from typing import Optional, Type
import httpx
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

CLAWHAND_BASE = "https://clawhand.net"


class _ClawhandBase(BaseTool):
    api_key: str = Field(..., description="Clawhand API key (clw_...)")

    @property
    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }


class PostJobInput(BaseModel):
    title: str = Field(description="Short job title")
    description: str = Field(description="Full task description for the human worker")
    budget_cents: int = Field(
        description="Budget in cents of USDC (e.g. 2500 = $25.00 USDC)"
    )
    deadline: str = Field(description="ISO 8601 deadline, e.g. 2026-04-15T00:00:00Z")
    task_type: str = Field(
        description="Type of task: research, data_labeling, writing, code_review, testing, or other"
    )
    skills_required: Optional[list[str]] = Field(
        default=None, description="List of required skills"
    )


class PostJobTool(_ClawhandBase):
    name: str = "clawhand_post_job"
    description: str = (
        "Post a task to Clawhand for a human worker to complete. "
        "Returns the job ID and a link to the job listing."
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
        r = httpx.post(
            f"{CLAWHAND_BASE}/api/v1/jobs", headers=self._headers, json=payload
        )
        r.raise_for_status()
        job = r.json()
        return f"Job posted. ID: {job['id']}. View at {CLAWHAND_BASE}/jobs/{job['id']}"

    async def _arun(self, *args, **kwargs) -> str:
        raise NotImplementedError("Use _run for synchronous execution")


class CheckJobTool(_ClawhandBase):
    name: str = "clawhand_check_job"
    description: str = (
        "Check a Clawhand job's status and list applicants. Input: job_id (string)."
    )

    def _run(self, job_id: str) -> str:
        r = httpx.get(f"{CLAWHAND_BASE}/api/v1/jobs/{job_id}", headers=self._headers)
        r.raise_for_status()
        job = r.json()
        apps = job.get("applications", [])
        summary = (
            f"Job '{job['title']}' — status: {job['status']}, {len(apps)} applicant(s)."
        )
        for app in apps[:5]:
            summary += f"\n  [{app['id']}] {app.get('worker_name', 'Worker')}: {app.get('pitch', '')[:80]}"
        return summary

    async def _arun(self, *args, **kwargs) -> str:
        raise NotImplementedError("Use _run for synchronous execution")


class AcceptApplicationInput(BaseModel):
    job_id: str = Field(description="Clawhand job ID")
    application_id: str = Field(description="Application ID to accept")


class AcceptApplicationTool(_ClawhandBase):
    name: str = "clawhand_accept_application"
    description: str = (
        "Accept a worker's application on a Clawhand job. "
        "Provide job_id and application_id."
    )
    args_schema: Type[BaseModel] = AcceptApplicationInput

    def _run(self, job_id: str, application_id: str) -> str:
        r = httpx.post(
            f"{CLAWHAND_BASE}/api/v1/jobs/{job_id}/accept",
            headers=self._headers,
            json={"application_id": application_id},
        )
        r.raise_for_status()
        return f"Application {application_id} accepted. Worker will be notified."

    async def _arun(self, *args, **kwargs) -> str:
        raise NotImplementedError("Use _run for synchronous execution")


class ReleasePaymentInput(BaseModel):
    job_id: str = Field(description="Job ID to release payment for")


class ReleasePaymentTool(_ClawhandBase):
    name: str = "clawhand_release_payment"
    description: str = (
        "Release USDC payment to the worker after reviewing their work. "
        "Input: job_id (string). Worker receives USDC instantly on Base."
    )
    args_schema: Type[BaseModel] = ReleasePaymentInput

    def _run(self, job_id: str) -> str:
        r = httpx.post(
            f"{CLAWHAND_BASE}/api/v1/jobs/{job_id}/release", headers=self._headers
        )
        r.raise_for_status()
        result = r.json()
        return f"Payment released. Worker credited {result.get('worker_amount_usdc', '?')} USDC."

    async def _arun(self, *args, **kwargs) -> str:
        raise NotImplementedError("Use _run for synchronous execution")


class SendMessageInput(BaseModel):
    job_id: str = Field(description="Job ID")
    application_id: str = Field(description="Application ID for the conversation")
    content: str = Field(description="Message content to send to the worker")


class SendMessageTool(_ClawhandBase):
    name: str = "clawhand_send_message"
    description: str = (
        "Send a message to a worker on a Clawhand job. "
        "Use this to communicate instructions, ask questions, or request revisions."
    )
    args_schema: Type[BaseModel] = SendMessageInput

    def _run(self, job_id: str, application_id: str, content: str) -> str:
        r = httpx.post(
            f"{CLAWHAND_BASE}/api/v1/jobs/{job_id}/messages",
            headers=self._headers,
            json={"application_id": application_id, "content": content},
        )
        r.raise_for_status()
        return "Message sent to worker."

    async def _arun(self, *args, **kwargs) -> str:
        raise NotImplementedError("Use _run for synchronous execution")
