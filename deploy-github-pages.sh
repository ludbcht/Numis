#!/bin/bash

echo "🚀 Préparation du déploiement GitHub Pages..."

# Vérifier que nous sommes dans le bon répertoire
if [ ! -d "frontend" ]; then
    echo "❌ Erreur: Dossier frontend non trouvé"
    echo "   Exécutez ce script depuis le dossier /app"
    exit 1
fi

# Demander l'URL du backend
echo ""
echo "📝 Configuration du backend"
echo "Entrez l'URL de votre backend déployé (ex: https://votre-app.onrender.com)"
read -p "URL du backend: " BACKEND_URL

if [ -z "$BACKEND_URL" ]; then
    echo "❌ URL du backend requise"
    exit 1
fi

# Mettre à jour le .env
echo "REACT_APP_BACKEND_URL=$BACKEND_URL" > frontend/.env
echo "WDS_SOCKET_PORT=443" >> frontend/.env
echo "ENABLE_HEALTH_CHECK=false" >> frontend/.env

echo "✅ Configuration mise à jour"

# Build du frontend
echo ""
echo "🔨 Build du frontend..."
cd frontend
yarn build

if [ $? -ne 0 ]; then
    echo "❌ Erreur lors du build"
    exit 1
fi

cd ..

# Créer le dossier de déploiement
echo ""
echo "📦 Préparation des fichiers pour GitHub Pages..."
rm -rf github-pages-deploy
mkdir -p github-pages-deploy

# Copier les fichiers de build
cp -r frontend/build/* github-pages-deploy/

# Créer .nojekyll
touch github-pages-deploy/.nojekyll

# Créer un README pour GitHub Pages
cat > github-pages-deploy/README.md << 'EOF'
# Numis - Collection de Pièces de 2€ Commémoratives

Application déployée sur GitHub Pages.

Pour voir le code source et les instructions complètes : [Dépôt principal](https://github.com/votre-username/votre-repo)

## Connexion

- **Nom d'utilisateur** : Ludivine
- **Mot de passe** : Ludivine67
EOF

echo ""
echo "✅ Déploiement préparé dans: /app/github-pages-deploy/"
echo ""
echo "📋 Prochaines étapes:"
echo "   1. Créez un dépôt GitHub (si ce n'est pas déjà fait)"
echo "   2. Copiez le contenu de /app/github-pages-deploy/ dans votre dépôt"
echo "   3. Commitez et poussez:"
echo "      git add ."
echo "      git commit -m 'Deploy to GitHub Pages'"
echo "      git push origin main"
echo "   4. Activez GitHub Pages dans les paramètres du dépôt"
echo ""
echo "🎉 Prêt pour le déploiement!"
