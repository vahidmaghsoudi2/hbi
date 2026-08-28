$ErrorActionPreference = "Continue"
Set-Location E:\hbi

Write-Host "===== HBI Sync ====="
git fetch origin

$local = git rev-parse HEAD
$origin = git rev-parse origin/master
$dirty = git status --short

Write-Host "Local : $local"
Write-Host "Origin: $origin"
Write-Host "Status:"
Write-Host $dirty

if ($dirty) {
    Write-Host "⚠️ تغییرات محلی داری؛ همگام‌سازی انجام نشد."
} else {
    if ($local -eq $origin) {
        Write-Host "✅ از قبل همگام است."
    } else {
        Write-Host "در حال pull --rebase..."
        git pull --rebase origin master
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ همگام شد."
        } else {
            Write-Host "❌ خطا در pull. تعارض را بررسی کن."
        }
    }
}
Write-Host "===== END ====="
