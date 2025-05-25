# Установка Node.js и npm
if (!(Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "Установка Node.js..."
    winget install OpenJS.NodeJS.LTS
}

# Установка зависимостей проекта
Write-Host "Установка зависимостей проекта..."
npm install

# Создание необходимых директорий
Write-Host "Создание структуры проекта..."
New-Item -ItemType Directory -Force -Path "src/components"
New-Item -ItemType Directory -Force -Path "src/pages"
New-Item -ItemType Directory -Force -Path "src/styles"
New-Item -ItemType Directory -Force -Path "src/utils"

Write-Host "Установка завершена!" 