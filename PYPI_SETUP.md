# PyPI Publishing Setup

This document explains how to set up automated PyPI publishing for django-deadcode using GitHub Actions and PyPI's Trusted Publishers feature.

## Overview

The repository uses GitHub Actions to automatically publish releases to PyPI when a new GitHub Release is created. This uses PyPI's **Trusted Publishers** mechanism, which provides secure, token-free publishing.

## Setup Steps

### 1. Configure PyPI Trusted Publisher

Before the first release, you need to register this repository as a trusted publisher on PyPI:

1. **Go to PyPI** and sign in: https://pypi.org/

2. **Navigate to Publishing** (for existing projects) or **Create pending publisher** (for new projects):
   - For existing projects: Go to your project → Manage → Publishing
   - For new projects: Go to https://pypi.org/manage/account/publishing/

3. **Add GitHub as a trusted publisher** with these details:
   - **Owner:** `nanorepublica`
   - **Repository:** `django-deadcode`
   - **Workflow name:** `publish.yml`
   - **Environment name:** `pypi` (optional but recommended)

4. Click **Add** to save the configuration

### 2. Configure GitHub Environment (Optional but Recommended)

For additional security, configure a PyPI environment in GitHub:

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Environments**
3. Click **New environment**
4. Name it: `pypi`
5. Optionally add protection rules:
   - Required reviewers (recommended for production)
   - Wait timer
   - Deployment branches (e.g., only `main`)

### 3. Prepare for Release

Before creating a release:

1. **Update version** in `pyproject.toml`:
   ```toml
   version = "0.2.0"  # Update this
   ```

2. **Update CHANGELOG.md** with release notes

3. **Commit changes**:
   ```bash
   git add pyproject.toml CHANGELOG.md
   git commit -m "Bump version to 0.2.0"
   git push
   ```

4. **Ensure CI passes**: Wait for all CI checks to pass on the main branch

### 4. Create a GitHub Release

1. Go to your repository on GitHub
2. Navigate to **Releases** → **Draft a new release**
3. Click **Choose a tag** and create a new tag (e.g., `v0.2.0`)
4. Set the release title (e.g., "v0.2.0 - Reverse/Redirect Detection")
5. Add release notes (copy from CHANGELOG.md)
6. Click **Publish release**

### 5. Automated Publishing

Once you publish the release, the GitHub Action will automatically:

1. ✅ Build the distribution packages (wheel and sdist)
2. ✅ Publish to PyPI using Trusted Publishers
3. ✅ Sign the packages with Sigstore
4. ✅ Upload signed packages to the GitHub Release

You can monitor progress in the **Actions** tab of your repository.

## Workflows

### CI Workflow (`.github/workflows/ci.yml`)

Runs on every push and pull request:
- Lints code with Ruff
- Tests on Python 3.8-3.12
- Tests with Django 3.2-5.0
- Builds distribution packages
- Uploads coverage to Codecov (if configured)

### Publish Workflow (`.github/workflows/publish.yml`)

Runs when a GitHub Release is published:
- Builds distribution packages
- Publishes to PyPI (using Trusted Publishers)
- Signs packages with Sigstore
- Uploads to GitHub Release

## Manual Publishing (Emergency Only)

If you need to publish manually (not recommended):

```bash
# Build the distribution
python -m build

# Upload to PyPI (requires API token)
python -m twine upload dist/*
```

For manual publishing, you'll need to:
1. Create a PyPI API token
2. Store it as a GitHub secret: `PYPI_API_TOKEN`
3. Update the workflow to use the token instead of Trusted Publishers

## Versioning Strategy

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** version (e.g., 1.0.0 → 2.0.0): Breaking changes
- **MINOR** version (e.g., 0.1.0 → 0.2.0): New features, backward compatible
- **PATCH** version (e.g., 0.1.0 → 0.1.1): Bug fixes, backward compatible

## Testing Releases

To test the release process without publishing to PyPI:

1. Use TestPyPI instead:
   - Configure Trusted Publisher on https://test.pypi.org/
   - Update workflow to publish to TestPyPI first

2. Or trigger the workflow manually:
   - Go to Actions → Publish to PyPI → Run workflow
   - Select the branch and run

## Troubleshooting

### "Trusted publisher mismatch" error

- Verify the repository, workflow name, and environment name in PyPI settings
- Ensure you're publishing from the correct branch (usually `main`)

### "Permission denied" error

- Check that `id-token: write` permission is set in the workflow
- Verify the PyPI environment is configured in GitHub (if using one)

### Build fails

- Ensure `pyproject.toml` has correct metadata
- Check that all dependencies are properly specified
- Verify Python version compatibility

### Tests fail in CI

- Run tests locally: `pytest`
- Check that all dependencies are installed: `pip install -e ".[dev]"`
- Ensure Django compatibility with the matrix versions

## Security

- ✅ Uses OIDC (OpenID Connect) for authentication (no tokens stored)
- ✅ Packages are signed with Sigstore for supply chain security
- ✅ GitHub environment protection (optional) requires manual approval
- ✅ Minimal permissions (principle of least privilege)

## Resources

- [PyPI Trusted Publishers Documentation](https://docs.pypi.org/trusted-publishers/)
- [GitHub Actions for PyPI Publishing](https://packaging.python.org/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)
- [Sigstore for Supply Chain Security](https://www.sigstore.dev/)
