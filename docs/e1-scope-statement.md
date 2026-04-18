# E1 Scope Statement — Telco NOC Incident Management

**Date:** 2026-04-18
**Status:** Ratified
**Role:** Primary knowledge contribution for E1 Problem 
Definition first Direction Capture.

---

## Domain
Telco Network Operations Centre (NOC) — Incident Management

## Problem
When an incident ticket is logged, NOC operators must 
diagnose the fault, correlate it with related tickets, 
consult SOPs, and determine whether the issue can be 
resolved remotely or requires field engineer dispatch. 
This process is manual, knowledge-intensive, and 
time-critical.

## Solution
A multi-agent system comprising four agents — Diagnosis 
Agent, Ticket Correlation Agent, SOP Agent, and Agent 
Orchestrator — that jointly analyse an incoming incident 
ticket and produce a structured recommendation: remote 
resolution with suggested remediation steps, or field 
engineer dispatch with justification.

## Decision output
Remote resolution recommendation OR dispatch decision, 
presented to a NOC operator who reviews and approves 
before any action is taken.

## Human oversight model
Human-in-the-loop review of AI recommendation before 
action. The system recommends; the human decides.

## Integration surface
Ticketing system (incident intake and output) + SOP / 
knowledge base (resolution guidance). No field engineer 
dispatch system integration in scope.

## Volume
Low (tens of incidents per day).

## Estimate scope
Core agent logic only (163 person-days). Integrations, 
infrastructure, and deployment pipeline are out of scope 
for this estimate.

## Deployment context
Production deployment.

## Regulatory surface
MAS TRM-bound. Audit trail, change management, and SDLC 
controls apply.

## Baseline for proof
This 163-pd conventional estimate is the ungoverned 
baseline. 4WRD MVGH-β will deliver the same core agent 
logic under full governance — governed, audited, 
adversarially-challenged — and compare effort, role 
compression, rework visibility, and compliance readiness 
against this baseline.
