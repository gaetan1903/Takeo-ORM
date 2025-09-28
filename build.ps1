# Script de build pour la nouvelle architecture optimisée
# Génère les bindings Go avec gopy pour l'API haut niveau

# Vérification de la compilation Go
Write-Host "🚀 Vérification de la compilation Go..."
Set-Location core
go build -v .
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erreur de compilation Go"
    exit 1
}
Write-Host "✅ Compilation Go réussie"

# Génération des bindings Python avec gopy
Write-Host "🔗 Génération des bindings Python avec gopy..."
Set-Location ..
gopy build -output=takeo/core -vm=python3 ./core
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erreur génération bindings"
    exit 1
}
Write-Host "✅ Bindings Python générés dans takeo/core"

# Installation des dépendances Python si nécessaire
Write-Host "📦 Vérification des dépendances Python..."
python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erreur installation dépendances"
    exit 1
}
Write-Host "✅ Dépendances Python installées"

Write-Host ""
Write-Host "🎉 BUILD TERMINÉ AVEC SUCCÈS!"
Write-Host "   - API Go haut niveau compilée"
Write-Host "   - Bindings Python générés" 
Write-Host "   - Prêt pour utilisation optimisée"
Write-Host ""
Write-Host "Pour tester:"
Write-Host "   python example_optimized.py"