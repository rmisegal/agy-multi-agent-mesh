<#
.SYNOPSIS
    One-step installer and launcher for agymesh (session-to-session mesh for Antigravity CLI).

.DESCRIPTION
    Follows docs/INSTALL.md from start to finish:
      1. checks that Python (3.10+) and the Antigravity CLI (agy) exist  (they are NOT installed here)
      2. installs Git (winget) and uv (official installer) when they are missing
      3. clones the repository, or pulls the latest version when it is already there
      4. installs agymesh with `uv sync`
      5. starts the hub and opens the art, poem and joke agy windows
         (agy runs with --dangerously-skip-permissions, see config/setup.json -> launch.agy_args)
      6. waits until the three workers have joined the mesh
      7. opens the master agy window, which runs the PING/PONG test by itself

    Run it again at any time: it pulls updates and restarts what is missing.

    (c) 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd. All rights reserved.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\install-agymesh.ps1

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\install-agymesh.ps1 -InstallDir C:\courses -NoLaunch
#>
[CmdletBinding()]
param(
    [string]$InstallDir = (Get-Location).Path,
    [string]$RepoUrl = "https://github.com/rmisegal/agy-multi-agent-mesh.git",
    [string]$RepoName = "agy-multi-agent-mesh",
    [int]$JoinTimeoutSec = 300,
    [switch]$NoLaunch
)

$ErrorActionPreference = "Continue"   # native tools write progress to stderr; we check exit codes
$Steps = 8

function Step([int]$n, [string]$text) { Write-Host ""; Write-Host "[$n/$Steps] $text" -ForegroundColor Cyan }
function Ok([string]$text) { Write-Host "      OK: $text" -ForegroundColor Green }
function Info([string]$text) { Write-Host "      $text" }
function Warn([string]$text) { Write-Host "      NOTE: $text" -ForegroundColor Yellow }
function Fail([string]$text) {
    Write-Host "      PROBLEM: $text" -ForegroundColor Red
    Write-Host "      The installer stopped. Fix the problem above and run it again." -ForegroundColor Red
    exit 1
}
function Have([string]$cmd) { return [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }
function Refresh-Path {
    $machine = [Environment]::GetEnvironmentVariable("Path", "Machine")
    $user = [Environment]::GetEnvironmentVariable("Path", "User")
    $env:Path = "$machine;$user;$env:USERPROFILE\.local\bin;$env:USERPROFILE\.cargo\bin"
}
function Is-AgymeshRepo([string]$dir) {
    $toml = Join-Path $dir "pyproject.toml"
    return (Test-Path $toml) -and ((Get-Content $toml -Raw) -match 'name\s*=\s*"agymesh"')
}

Write-Host "agymesh installer - (c) 2026 Dr. Yoram Segal, Gal Technologies Artificial Intelligence Ltd." -ForegroundColor White

# ---------------------------------------------------------------- 1. Python + agy (check only)
Step 1 "Checking Python and the Antigravity CLI (they must already be installed)"
$pyVersion = $null
foreach ($py in @("python", "py")) {
    if (Have $py) {
        $out = & $py -c "import sys; print('%d.%d' % sys.version_info[:2])" 2>$null
        if ($LASTEXITCODE -eq 0 -and $out -match '^\d+\.\d+$') { $pyVersion = $out; break }
    }
}
if (-not $pyVersion) { Fail "Python was not found. Install Python 3.10 or newer from https://www.python.org and tick 'Add python.exe to PATH'." }
$parts = $pyVersion.Split(".")
if ([int]$parts[0] -lt 3 -or ([int]$parts[0] -eq 3 -and [int]$parts[1] -lt 10)) {
    Fail "Python $pyVersion is too old. Install Python 3.10 or newer."
}
Ok "Python $pyVersion"
if (-not (Have "agy")) { Fail "The Antigravity CLI (agy) was not found. Install it, open a new terminal, run 'agy' once and sign in." }
Ok "Antigravity CLI found at $((Get-Command agy).Source)"

# ---------------------------------------------------------------- 2. Git
Step 2 "Checking Git"
if (-not (Have "git")) {
    if (-not (Have "winget")) { Fail "Git is missing and winget is not available. Install Git from https://git-scm.com and run this again." }
    Info "Git is missing - installing it with winget (this can take a minute)..."
    winget install --id Git.Git -e --source winget --accept-package-agreements --accept-source-agreements --silent
    Refresh-Path
    if (-not (Have "git")) { Fail "Git was installed but is not on PATH yet. Close this window, open a new one and run the installer again." }
}
Ok "$(git --version)"

# ---------------------------------------------------------------- 3. uv
Step 3 "Checking uv (the Python package manager)"
if (-not (Have "uv")) {
    Info "uv is missing - installing it from astral.sh..."
    powershell -NoProfile -ExecutionPolicy ByPass -Command "irm https://astral.sh/uv/install.ps1 | iex"
    Refresh-Path
    if (-not (Have "uv")) { Fail "uv was installed but is not on PATH yet. Close this window, open a new one and run the installer again." }
}
Ok "$(uv --version)"

# ---------------------------------------------------------------- 4. repository
Step 4 "Getting the agymesh repository"
$Repo = $null
if ($PSScriptRoot -and (Is-AgymeshRepo $PSScriptRoot)) { $Repo = $PSScriptRoot }
elseif (Is-AgymeshRepo $InstallDir) { $Repo = (Resolve-Path $InstallDir).Path }
elseif (Is-AgymeshRepo (Join-Path $InstallDir $RepoName)) { $Repo = (Resolve-Path (Join-Path $InstallDir $RepoName)).Path }

if ($Repo -and (Test-Path (Join-Path $Repo ".git"))) {
    Info "Found the repository in $Repo - pulling the latest version..."
    # AGY.md files are regenerated for this PC on every start; reset them so the pull never conflicts.
    $generated = git -C $Repo ls-files -m -- "*AGY.md"
    if ($generated) { git -C $Repo checkout -- $generated }
    git -C $Repo pull --ff-only
    if ($LASTEXITCODE -ne 0) { Warn "Could not pull updates (local changes or no network). Continuing with the version on disk." }
    else { Ok "Repository is up to date" }
} elseif ($Repo) {
    Warn "$Repo has the project files but is not a git clone; using it as it is (no update)."
} else {
    if (-not (Test-Path $InstallDir)) { New-Item -ItemType Directory -Path $InstallDir | Out-Null }
    $Repo = Join-Path (Resolve-Path $InstallDir).Path $RepoName
    Info "Cloning $RepoUrl into $Repo ..."
    git clone $RepoUrl $Repo
    if ($LASTEXITCODE -ne 0) { Fail "git clone failed. Check your internet connection and the address $RepoUrl." }
    Ok "Repository cloned"
}
if ($Repo -match '[^\x00-\x7F]') { Warn "The folder path contains non-English characters. If something fails, move it to a plain path such as C:\courses." }

# ---------------------------------------------------------------- 5. install
Step 5 "Installing agymesh (uv sync)"
Set-Location $Repo
uv sync
if ($LASTEXITCODE -ne 0) { Fail "uv sync failed - see the messages above." }
$version = uv run agymesh --version
if ($LASTEXITCODE -ne 0) { Fail "agymesh does not start after installation." }
Ok "$version"
if (-not ((Get-Content (Join-Path $Repo "config\setup.json") -Raw) -match "--dangerously-skip-permissions")) {
    Warn "config\setup.json -> launch.agy_args does not contain --dangerously-skip-permissions; agy will ask before every command."
}
if ($NoLaunch) {
    Write-Host ""
    Write-Host "Installed. Start the agents later with:  cd `"$Repo`"; uv run agymesh up --with-master" -ForegroundColor Green
    exit 0
}

# ---------------------------------------------------------------- 6. hub + workers
Step 6 "Starting the hub and opening the art, poem and joke agy windows"
uv run agymesh up
if ($LASTEXITCODE -ne 0) { Fail "Could not start the mesh (is port 9877 used by another program? Set AGYMESH_PORT=9878 and run again)." }
Info "Three agy windows are opening. The FIRST time only, each one asks:"
Info "    'Do you trust the contents of this project?'  ->  choose 'Yes, I trust this folder' + Enter"
Info "After that every window joins the mesh and starts listening by itself."

# ---------------------------------------------------------------- 7. wait for the workers
Step 7 "Waiting until all workers have joined (up to $JoinTimeoutSec s)"
uv run agymesh wait-peers --timeout $JoinTimeoutSec
if ($LASTEXITCODE -ne 0) {
    Warn "Not every worker joined yet. Answer any question shown in the agy windows; the master's ping test will show who is missing."
} else { Ok "All workers are listening" }

# ---------------------------------------------------------------- 8. master + ping/pong
Step 8 "Opening the master agy window - it runs the PING/PONG test by itself"
uv run agymesh launch --master-only --ping-test
if ($LASTEXITCODE -ne 0) { Fail "Could not open the master window." }
Write-Host ""
Write-Host "Done. In the MASTER window you will see a table: every worker answered PONG, from which agy pid." -ForegroundColor Green
Write-Host "Then type a goal in the master window, for example:" -ForegroundColor Green
Write-Host "    Split the topic 'Israeli winter' between the agents and show the merged result."
Write-Host "Useful commands (in this folder: $Repo):"
Write-Host "    uv run agymesh status        - who is online"
Write-Host "    uv run agymesh down          - stop the hub (close the agy windows first)"
Write-Host "Manual: docs\USER_MANUAL.md"
