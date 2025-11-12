# Raw Idea

## Feature Description

When it comes to reporting on templates, we should exclude any templates outside of the project where the command has been run. This means any templates that aren't prefixed with the `BASE_DIR` value from Django settings.

Second, when reporting on unreferenced templates we should cater for those referenced by 'include' or 'extends' statements and not just referenced by views.

Finally we don't need to report on the includes/extends by default.
