param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateSet(
        "up",
        "down",
        "logs",
        "test",
        "test-cov",
        "migrate",
        "seed",
        "load-test",
        "benchmark"
    )]
    [string]$Task,

    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ExtraArgs
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)][string]$Command
    )
    Write-Host ">> $Command"
    Invoke-Expression $Command
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code $LASTEXITCODE"
    }
}

$composeFile = "docker/docker-compose.yml"
$argsList = @($ExtraArgs)
$extra = if ($argsList.Count -gt 0) { " " + ($argsList -join " ") } else { "" }

switch ($Task) {
    "up"        { Invoke-Checked "docker compose -f $composeFile up -d --build$extra" }
    "down"      { Invoke-Checked "docker compose -f $composeFile down$extra" }
    "logs"      { Invoke-Checked "docker compose -f $composeFile logs -f --tail=200$extra" }
    "test"      { Invoke-Checked "pytest -q$extra" }
    "test-cov"  { Invoke-Checked "pytest --cov=src --cov-report=term-missing --cov-fail-under=85$extra" }
    "migrate"   { Invoke-Checked "python scripts/migrate.py$extra" }
    "seed"      { Invoke-Checked "python scripts/seed_data.py$extra" }
    "load-test" {
        if ($argsList.Count -eq 0) {
            Invoke-Checked "locust -f scripts/load_test.py --headless -u 50 -r 10 -t 2m --host http://localhost:8060"
        } else {
            Invoke-Checked "locust -f scripts/load_test.py$extra"
        }
    }
    "benchmark" { Invoke-Checked "python scripts/benchmark.py$extra" }
}
