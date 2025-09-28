#!/bin/bash
# Script de build pour la nouvelle architecture optimisée
# Génère les bindings Go avec gopy pour l'API haut niveau

echo "🚀 Vérification de la compilation Go..."
cd core
go build -v .
if [ $? -ne 0 ]; then
    echo "❌ Erreur de compilation Go"
    exit 1
fi
echo "✅ Compilation Go réussie"

# Génération des bindings Python avec gopy
echo "🔗 Génération des bindings Python avec gopy..."
cd ..
gopy build -output=takeo/core -vm=python3 ./core
if [ $? -ne 0 ]; then
    echo "❌ Erreur génération bindings"
    exit 1
fi
echo "✅ Bindings Python générés dans takeo/core"

# Installation des dépendances Python si nécessaire
echo "📦 Vérification des dépendances Python..."
python3 -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Erreur installation dépendances"
    exit 1
fi
echo "✅ Dépendances Python installées"

echo ""
echo "🎉 BUILD TERMINÉ AVEC SUCCÈS!"
echo "   - API Go haut niveau compilée"
echo "   - Bindings Python générés" 
echo "   - Prêt pour utilisation optimisée"
echo ""
echo "Pour tester:"
echo "   python3 example_optimized.py"