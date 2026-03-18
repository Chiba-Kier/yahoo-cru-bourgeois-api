param (
    [Parameter(Mandatory=$true)]
    [string]$BucketName
)

# Project Root: ../../data
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$DataDir = Join-Path $ScriptDir "../../data"

if (!(Test-Path $DataDir)) {
    Write-Error "Data directory not found at $DataDir"
    exit 1
}

Write-Host "Syncing master data to s3://$BUCKET_NAME/master/ ..." -ForegroundColor Cyan
aws s3 sync "$DataDir" "s3://$BUCKET_NAME/master/" --exclude "*" --include "*.csv"

Write-Host "Sync completed successfully." -ForegroundColor Green
