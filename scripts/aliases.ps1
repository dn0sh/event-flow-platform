Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-TaskCommand {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(ValueFromRemainingArguments = $true)][string[]]$Args
    )
    & "$PSScriptRoot/task.ps1" $Name @Args
}

function up         { param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Args) Invoke-TaskCommand "up" @Args }
function down       { param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Args) Invoke-TaskCommand "down" @Args }
function logs       { param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Args) Invoke-TaskCommand "logs" @Args }
function test       { param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Args) Invoke-TaskCommand "test" @Args }
function test-cov   { param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Args) Invoke-TaskCommand "test-cov" @Args }
function migrate    { param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Args) Invoke-TaskCommand "migrate" @Args }
function seed       { param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Args) Invoke-TaskCommand "seed" @Args }
function Start-LoadTest { param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Args) Invoke-TaskCommand "load-test" @Args }
function benchmark  { param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Args) Invoke-TaskCommand "benchmark" @Args }

Set-Alias -Name load-test -Value Start-LoadTest

Write-Host "PowerShell aliases loaded: up, down, logs, test, test-cov, migrate, seed, load-test, benchmark"
