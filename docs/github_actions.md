# Running GitHub Actions on a Fork or Custom Branch

This guide explains how to trigger and monitor GitHub Actions CI workflows when working on a personal fork or a custom feature branch in Lute.

---

## 1. Understanding the Workflow Configuration

The Lute CI workflow (`.github/workflows/ci.yml`) is configured to run tests and linters only on specific target branches to optimize resource usage. By default, the workflow is defined as:

```yaml
on:
  push:
    branches: [ "develop", "master", "github-ci", "windows" ]
  pull_request:
    branches: [ "develop", "master" ]
```

### The CI Branch List
* **`develop` / `master`**: Standard development branches.
* **`github-ci`**: A dedicated branch name reserved for running custom CI runs, experiments, and feature-branch testing.
* **Custom Branches**: If you push to a custom feature branch (e.g., `feature-my-cool-idea`), the GitHub Action **will not** trigger automatically.

---

## 2. Triggering CI on a Feature Branch

To execute the GitHub Action on your custom feature branch without merging into `develop` or `master`, you can push your local branch directly to the remote `github-ci` branch:

```bash
git push origin <your-local-branch>:github-ci --force
```

### Example
If your local feature branch is named `feature-full-text-search`:
```bash
git push origin feature-full-text-search:github-ci --force
```

This commands maps your local branch to the remote `github-ci` branch on GitHub, immediately triggering the workflow run.

---

## 3. Monitoring Runs via the GitHub CLI (`gh`)

You can view, track, and watch the status of the runs directly from your terminal using the official GitHub CLI.

### Set Your Default Repository
If you haven't set the default remote repository, configure it:
```bash
gh repo set-default
```

### List Active Runs
To list the most recent workflow runs on the `github-ci` branch:
```bash
gh run list --branch github-ci -L 5
```

### Watch Progress
To watch the build process in real-time as it executes:
```bash
gh run watch <run-id>
```
*(Replace `<run-id>` with the run ID returned by the `gh run list` command.)*
