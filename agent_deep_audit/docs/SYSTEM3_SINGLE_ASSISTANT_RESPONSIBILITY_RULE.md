# System3 Single Assistant Responsibility Rule

## Purpose

This document records the user's operating requirement for System3 work.

## Rule

The assistant must remain the primary worker for System3 analysis, planning, GitHub inspection, architecture comparison, repo documentation, and tool-accessible changes.

The assistant must not default to telling the user to use another agent as the main worker while the core System3 trading-performance goal remains unfinished.

## Core Goal Reminder

System3 must become capable of finding the best valid daily market opportunity before the move, safely paper-trading it, and proving prediction accuracy and paper profitability against real market results every trading day.

## When Manual User Action Is Allowed

The assistant may request manual user action only when required by limits outside assistant access, such as:

- Local Windows command execution.
- Private secrets or environment variables.
- Broker login or OTP/TOTP access.
- OpenAlgo or Dhan session access.
- Live market feed access from the user's machine.
- Permissions unavailable through available tools.

Any manual action request must be specific, minimal, and tied to a proof output.

## Record-Keeping Rule

Online records should be kept in GitHub docs, branches, pull requests, or issues where tool access allows.

Offline/local proof should be stored in repository proof folders when local execution is available.

The assistant must keep the goal and current evidence updated and must not drift into deployment-only, UI-only, or generic cleanup work unless that work directly supports the core trading-performance goal.
