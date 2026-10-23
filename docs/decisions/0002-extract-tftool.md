# 0002. Extract TFTOOL into a Standalone Project

## Status

Accepted

## Context

TFTOOL has grown beyond a small playground experiment and needs to live alongside Playground and TF Traits as an independent project.

## Decision

Move its launcher, package, configuration, requirements, and product documentation into sibling `../tftool/`. Give it its own setup instructions, agent guidance, and virtual environment. Preserve application behavior and user settings.

## Consequences

Playground no longer owns TFTOOL or its dependencies. Earlier TFTOOL source history remains in this repository's Git history. Future work belongs in the standalone project.
