---
name: Prompt Injection Prevention
description: >
  Defend LLM-based agents against prompt injection attacks using
  CaMeL-inspired data-control separation, taint tracking,
  capability-based security, and policy enforcement.
version: 0.1.0
author: JC (Jonathan Chen)
license: MIT
tags:
  - security
  - prompt-injection
  - llm-safety
  - camel
  - agent-defense
---

# Prompt Injection Prevention

## What This Skill Does

This skill protects AI agents from **prompt injection** — the #1 security
threat to LLM-based systems. When an agent reads untrusted content (web
pages, files, API responses), that content can contain adversarial
instructions designed to hijack the agent's behavior.

This skill implements defenses from the
[CaMeL paper](https://arxiv.org/abs/2503.18813) (CApability-based
Machine Learning) to keep agents safe.

## When to Use This Skill

Use this skill whenever an agent:

- Reads **untrusted external content** (web pages, user-uploaded files,
  third-party API responses)
- Executes **tools or actions** that could cause real-world side effects
  (sending emails, writing files, running code)
- Processes **multi-step workflows** where intermediate data could be
  poisoned
- Needs to enforce the **principle of least privilege** for tool access

## Core Concepts

### 1. Data-Control Separation

Every piece of data is tagged with its **provenance** (where it came
from). Untrusted data (tool outputs, web content, file reads) is never
allowed to influence which actions the agent takes.

```python
from prompt_injection_prevention import TaintLabel, TaintTracker

tracker = TaintTracker()
user_cmd = tracker.create_trusted("Summarize the report")        # trusted
web_data = tracker.create_tainted("...", TaintLabel.WEB_CONTENT)  # untrusted
```

### 2. Capability-Based Security

The agent can only use tools it has been explicitly granted access to.
Grants are scoped to specific resources using glob patterns.

```python
from prompt_injection_prevention import Capability, CapabilityManager

caps = CapabilityManager()
caps.grant(Capability.FILE_READ, resource_pattern="/safe/*")
caps.check(Capability.FILE_READ, resource="/safe/report.txt")  # allowed
caps.check(Capability.FILE_READ, resource="/etc/passwd")        # denied
```

### 3. Input Sanitization

All text is scanned for known injection patterns before processing:

- Instruction overrides ("ignore previous instructions")
- Role/persona hijacking ("you are a new assistant")
- LLM delimiter injection (`<|im_start|>`, `[INST]`)
- Hidden instructions in HTML comments
- Encoding-based obfuscation
- High-entropy encoded payloads

```python
from prompt_injection_prevention import InputSanitizer

sanitizer = InputSanitizer()
result = sanitizer.scan("Ignore all previous instructions")
# result.threat_level == ThreatLevel.CRITICAL
# result.is_safe == False
```

### 4. Policy Engine

A configurable rule engine decides whether each action should be
**allowed**, **denied**, or **quarantined** (held for human review):

| Condition | Decision |
|---|---|
| Critical threat detected | **DENY** |
| High threat detected | **QUARANTINE** |
| Code execution with tainted input | **DENY** |
| File/DB write with tainted input | **DENY** |
| Email/message with tainted input | **QUARANTINE** |
| Trusted input, low threat | **ALLOW** |

### 5. Dual LLM Architecture

Optionally route trusted and untrusted content through separate LLM
contexts, preventing untrusted data from ever entering the privileged
decision-making path.

## Quick Start

```python
from prompt_injection_prevention import (
    CamelDefense,
    Capability,
    TaintLabel,
)

defense = CamelDefense()
defense.grant_capability(Capability.FILE_READ, resource_pattern="/safe/*")

result = defense.evaluate_action(
    action_name="read_file",
    capability=Capability.FILE_READ,
    resource="/safe/report.txt",
    inputs={"query": user_query},
    input_taint=TaintLabel.USER_INPUT,
)

if result.is_allowed:
    ...  # proceed
elif result.needs_review:
    ...  # ask human
else:
    ...  # block and log result.reason
```

## Installation

```bash
uv sync                                                # install
uv run python -m unittest discover -s tests -v         # test
```

## Components

| Module | Purpose |
|---|---|
| `TaintTracker` | Data provenance labels and taint propagation |
| `CapabilityManager` | Least-privilege, scoped tool permissions |
| `InputSanitizer` | Pattern + entropy injection detection |
| `PolicyEngine` | Rule-based allow / deny / quarantine decisions |
| `DualLLMOrchestrator` | Isolated privileged and quarantined LLM contexts |
| `CamelDefense` | Top-level facade composing all components |

## References

- Debenedetti, E., et al. (2025). _CaMeL: CApability-based Machine
  Learning — Defending Against Prompt Injection with Capability Control
  and Data-Flow Analysis._ [arXiv:2503.18813](https://arxiv.org/abs/2503.18813)
