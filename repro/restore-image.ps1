# Restore the scaffold static image from the Loco 1.3.1 source commit.
# Run this yourself from the repository root. Starting the app does not download it.
# The public saas_app tree does not contain this file until you place it and commit it.
$ErrorActionPreference = 'Stop'
$expected = 'fe474f23e270bf582fd8f60a87daf77e08767e5d5b60d9b618005d5d5effe279'
$url = 'https://raw.githubusercontent.com/loco-rs/loco/3ddc279740ebf0516403ca8f7028ce481d616a02/loco-new/base_template/assets/static/image.png'
$dest = Join-Path (Get-Location) 'saas_app/assets/static/image.png'
$tmp = Join-Path $env:TEMP 'loco-saas-app-image.png'
Invoke-WebRequest -Uri $url -OutFile $tmp
$hash = (Get-FileHash -Algorithm SHA256 -Path $tmp).Hash.ToLower()
if ($hash -ne $expected) {
    Remove-Item -Force $tmp
    throw "SHA256 mismatch. Expected $expected but got $hash. Destination was not changed."
}
New-Item -ItemType Directory -Force -Path (Split-Path $dest) | Out-Null
Move-Item -Force $tmp $dest
Write-Output "Placed saas_app/assets/static/image.png after SHA256 matched."
