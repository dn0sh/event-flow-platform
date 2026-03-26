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
    [string[]]$ExtraArgs = @()
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
# Compose-файл лежит в docker/ — без --env-file подстановка ${RABBITMQ_*} из корневого .env не выполняется (брокер и приложения получают разные пароли).
$envFile = ".env"
$composeBase = "docker compose --env-file $envFile -f $composeFile"
$argsList = @($ExtraArgs)
$extra = if ($argsList.Count -gt 0) { " " + ($argsList -join " ") } else { "" }

switch ($Task) {
    "up"        { Invoke-Checked "$composeBase up -d --build$extra" }
    "down"      { Invoke-Checked "$composeBase down$extra" }
    "logs"      { Invoke-Checked "$composeBase logs -f --tail=200$extra" }
    "test"      { Invoke-Checked "pytest -q$extra" }
    "test-cov"  { Invoke-Checked "pytest --cov=src --cov-report=term-missing --cov-fail-under=85$extra" }
    "migrate"   { Invoke-Checked "python scripts/migrate.py$extra" }
    "seed"      { Invoke-Checked "python scripts/seed_data.py$extra" }
    "load-test" {
        # Latin-only: Cyrillic breaks in default Windows PowerShell encoding unless file is UTF-8 with BOM.
        Write-Host "Tip: set RATE_LIMIT_PER_MINUTE=0 in .env and restart the api container to avoid HTTP 429 during Locust."
        if ($argsList.Count -eq 0) {
            Invoke-Checked "locust -f scripts/load_test.py --headless -u 50 -r 10 -t 2m --host http://localhost:8060"
        } else {
            Invoke-Checked "locust -f scripts/load_test.py$extra"
        }
    }
    "benchmark" { Invoke-Checked "python scripts/benchmark.py$extra" }
}
