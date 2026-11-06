$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$java = Get-ChildItem -LiteralPath (Join-Path $PSScriptRoot 'queue-tooling/jre') -Recurse -Filter java.exe | Select-Object -First 1
if ($null -eq $java) { throw 'Portable Java runtime is missing from tools/queue-tooling/jre' }
$inputFile = Join-Path $PSScriptRoot 'queue-analysis/battleQueue.swf'
$outputFile = Join-Path $PSScriptRoot 'queue-analysis/battleQueue-compact.swf'
& $java.FullName -jar (Join-Path $PSScriptRoot 'queue-tooling/ffdec/ffdec.jar') -onerror abort -importScript $inputFile $outputFile (Join-Path $root 'src/flash')
if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $outputFile)) { throw 'Queue Flash compilation failed' }
Copy-Item -LiteralPath $outputFile -Destination (Join-Path $root 'res/gui/flash/battleQueue.swf') -Force
