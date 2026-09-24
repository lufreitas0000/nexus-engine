# Branch Scope and Development Rules

1. **Modular Isolation**: Commits must target specific independent modules (`app_spatial_compiler`, `app_vision_encoder`, etc.). Cross-module logic must be deferred to `app_orchestrator`.
2. **Dependency Management**: Dependencies must be isolated per module within their respective `requirements.in`.
3. **CI Matrix**: Features must support Python 3.11 and 3.12. Python 3.10 is deprecated and out of scope.
