# Run from the repository after committing and pushing course changes to main.
$ErrorActionPreference = 'Stop'
Push-Location (Split-Path $PSScriptRoot -Parent)
try {
    $branch = & git branch --show-current
    if ($LASTEXITCODE -ne 0 -or $branch -ne 'main') { throw 'Switch to main before publishing.' }
    $changes = & git status --porcelain
    if ($LASTEXITCODE -ne 0 -or $changes) { throw 'Commit all changes before publishing.' }
    $pagesCommit = & git subtree split --prefix=course-site/dist HEAD
    if ($LASTEXITCODE -ne 0) { throw 'Failed to prepare the Pages branch.' }
    & git push origin "${pagesCommit}:refs/heads/gh-pages"
    if ($LASTEXITCODE -ne 0) { throw 'Failed to publish. Check the remote branch; do not force push.' }
    Write-Host 'Pages source updated. GitHub will deploy it automatically.'
}
finally { Pop-Location }
