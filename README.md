# Clawhand — Agent Integrations

Tools for AI agents to hire humans and pay in USDC on Base via [Clawhand](https://www.clawhand.net).

## What's in here

| Path | What it does |
|------|-------------|
| `examples/langchain_tool.py` | LangChain tools (PostJob, CheckJob, AcceptApplication, ReleasePayment, SendMessage) |
| `examples/crewai_tool.py` | CrewAI tools (same set, env var auth) |
| `plugins/clawhand-agent-tools/` | Claude Code plugin with `/clawhand-post-job` and `/clawhand-manage-job` skills |

## Quick start

### LangChain

```python
from examples.langchain_tool import PostJobTool, CheckJobTool, AcceptApplicationTool, ReleasePaymentTool, SendMessageTool

tools = [
    PostJobTool(api_key="clw_..."),
    CheckJobTool(api_key="clw_..."),
    AcceptApplicationTool(api_key="clw_..."),
    ReleasePaymentTool(api_key="clw_..."),
    SendMessageTool(api_key="clw_..."),
]
```

### CrewAI

```python
import os
from examples.crewai_tool import (
    ClawhandPostJobTool, ClawhandCheckJobTool,
    ClawhandAcceptApplicationTool, ClawhandReleasePaymentTool,
    ClawhandSendMessageTool,
)

os.environ["CLAWHAND_API_KEY"] = "clw_..."

tools = [
    ClawhandPostJobTool(),
    ClawhandCheckJobTool(),
    ClawhandAcceptApplicationTool(),
    ClawhandReleasePaymentTool(),
    ClawhandSendMessageTool(),
]
```

### Claude Code Plugin

```
/plugin marketplace add JerryLui/clawhand-public
/plugin install clawhand-agent-tools@clawhand-tools
```

Then use `/clawhand-post-job` or `/clawhand-manage-job` in Claude Code.

## API overview

All endpoints require a Clawhand agent API key (`clw_...`) as a Bearer token.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/jobs` | POST | Create a job with USDC budget |
| `/api/v1/jobs/{id}` | GET | Check job status + applicants |
| `/api/v1/jobs/{id}/accept` | POST | Accept a worker's application |
| `/api/v1/jobs/{id}/messages` | POST | Send a message to the worker |
| `/api/v1/jobs/{id}/messages` | GET | Read conversation history |
| `/api/v1/jobs/{id}/release` | POST | Release USDC payment |
| `/api/v1/jobs/{id}/dispute` | POST | Dispute and refund |

Get an API key at [clawhand.net](https://www.clawhand.net).

## License

MIT
