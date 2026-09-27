# ADR-010: Rider app as a progressive web app first

- **Status:** Accepted
- **Date:** [project start]
- **Related:** SDD §2.2, §9; Implementation Plan M7

## Context

Riders need a mobile app, but building and publishing native apps adds tooling, store review and a separate codebase. The pilot has a small number of riders.

## Decision

Build the rider app as a PWA in the same React workspace. Location is sent while the app is open and the rider is online. Plan React Native (Expo) after the pilot if background location proves necessary.

## Consequences

- Positive: one codebase and design system; instant updates; no app-store delay.
- Negative: browsers limit background location and some push features, especially on iOS.
- Follow-up: test on 3 low-end Android devices in week 9; riders keep the app open during active jobs.

## Alternatives considered

| Option | Why not chosen |
| --- | --- |
| React Native from the start | Extra toolchain and store publishing during the semester |
| SMS/USSD-only rider flow | Cannot show maps or enter codes comfortably |
