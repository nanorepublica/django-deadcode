# Raw Idea: Fix Unused Template Detection

## User's Description

The unused template detection feature is still not working as expected. I have tested this in a project and templates that I know are referenced are being picked up as unreferenced.

One possible cause might be that in code all specification of templates are relative to a `templates` directory so you never put the full path

## Context

This is about fixing/improving the existing template detection feature to correctly handle template references that are relative to a `templates` directory.

## Date Initiated

2025-11-14
