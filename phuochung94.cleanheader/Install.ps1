param([string]$GamePath = 'C:\Program Files (x86)\Steam\steamapps\common\World of Tanks\asia')
$ErrorActionPreference = 'Stop'
[xml]$info = Get-Content -LiteralPath (Join-Path $GamePath 'version.xml')
if ([string]$info.'version.xml'.version -notmatch 'v\.(\S+)\s+#(\d+)') { throw 'Cannot read game version.' }
$gameVersion = $Matches[1]
$gameBuild = $Matches[2]
$realm = ([string]$info.'version.xml'.meta.realm).Trim()
$packageName = 'phuochung94.cleanheader-{0} {1} #{2}.wotmod' -f $realm,$gameVersion,$gameBuild
$source = Join-Path (Join-Path $PSScriptRoot 'dist') $packageName
if (!(Test-Path -LiteralPath $source -PathType Leaf)) { throw "Build this client package first: $packageName" }
$destination = Join-Path (Join-Path $GamePath 'mods') $gameVersion
New-Item -ItemType Directory -Path $destination -Force | Out-Null
Copy-Item -LiteralPath $source -Destination $destination -Force
$legacyNames = @(
    ('phuochung94.showtanks-{0} {1} #{2}.wotmod' -f $realm,$gameVersion,$gameBuild),
    ('phuochung94.showvehicle-{0} {1} #{2}.wotmod' -f $realm,$gameVersion,$gameBuild),
    ('phuochung94.Show vehicle not release-{0} {1} #{2}.wotmod' -f $realm,$gameVersion,$gameBuild),
    ('phuochung94.dreamgarage-{0} {1} #{2}.wotmod' -f $realm,$gameVersion,$gameBuild),
    'phuochung94.dream_garage_0.1.0.wotmod', 'phuochung94.hero_vehicle_0.1.0.wotmod'
)
foreach ($name in $legacyNames) {
    $old = Join-Path $destination $name
    if (Test-Path -LiteralPath $old -PathType Leaf) {
        $disabled = Join-Path $GamePath 'mods\disabled\cleanheader'
        New-Item -ItemType Directory -Path $disabled -Force | Out-Null
        Move-Item -LiteralPath $old -Destination (Join-Path $disabled ($name + '.' + [guid]::NewGuid().ToString('N') + '.disabled'))
    }
}
Write-Output "Installed Clean Garage Header: $packageName"
