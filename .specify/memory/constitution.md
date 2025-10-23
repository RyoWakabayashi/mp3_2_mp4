<!--
SYNC IMPACT REPORT:
Version: 1.0.0 (Initial constitution)
Modified principles: N/A (new constitution)
Added sections: All sections (initial creation)
Removed sections: N/A
Templates requiring updates: ✅ updated plan-template.md, spec-template.md, tasks-template.md
Follow-up TODOs: None
-->

# MP3 to MP4 Converter Constitution

## Core Principles

### I. User-First Design

MUST prioritize non-engineer usability over technical sophistication. Every feature MUST be testable by a non-technical user within 30 seconds of first interaction. GUI interfaces are preferred over command-line for end-user features. Error messages MUST be in plain language with suggested fixes.

**Rationale**: The primary users are non-engineers who need intuitive, immediate functionality without technical learning curves.

### II. Cross-Platform Compatibility

MUST support both Windows (primary deployment) and macOS (development/testing). Core conversion logic MUST be platform-agnostic. Platform-specific code MUST be isolated in adapter layers. Automated testing MUST run on both platforms.

**Rationale**: Windows is the target deployment platform, but macOS is the development environment, requiring seamless cross-platform operation.

### III. Self-Contained Distribution

MUST package all dependencies for single-file or single-folder distribution. No separate installation of codecs, frameworks, or system dependencies required. MUST work on fresh Windows installations without additional software.

**Rationale**: Non-technical users cannot be expected to manage complex dependency installations or system configurations.

### IV. Robust Error Handling

MUST gracefully handle corrupted files, unsupported formats, and insufficient system resources. All operations MUST be recoverable or cleanly abortable. Progress indicators MUST be accurate and responsive during long operations.

**Rationale**: Audio file processing involves many potential failure points that must not crash the application or lose user progress.

### V. Performance Transparency

MUST provide clear progress feedback for operations longer than 2 seconds. Batch operations MUST be resumable after interruption. MUST respect system resources and allow background operation without blocking the UI.

**Rationale**: Audio conversion can be time-consuming; users need clear feedback and control over resource usage.

## Quality Standards

### Testing Requirements

All user-facing features MUST have automated GUI tests simulating real user workflows. Core conversion logic MUST have unit tests with sample audio files. Performance tests MUST verify conversion speed benchmarks on both platforms.

### Documentation Standards

User documentation MUST be visual (screenshots) with step-by-step workflows. Technical documentation MUST include platform-specific build and deployment instructions. All error messages MUST be documented with resolution steps.

## Development Workflow

### Platform Development Cycle

Development and testing MUST occur on macOS. Windows compatibility MUST be verified before each release. Platform-specific issues MUST be addressed within the same development cycle, not deferred.

### Release Process

All releases MUST be tested on clean Windows and macOS systems. Distribution packages MUST be verified on systems without development tools. User acceptance testing MUST include non-technical users.

## Governance

This constitution supersedes all other development practices. All feature decisions and code reviews MUST verify compliance with user-first design principles. Technical complexity MUST be justified against user value. Platform compatibility cannot be compromised for development convenience.

**Version**: 1.0.0 | **Ratified**: 2025-10-23 | **Last Amended**: 2025-10-23
