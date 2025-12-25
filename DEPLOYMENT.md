# Numis - Gestionnaire de Collection de Pièces de 2€ Commémoratives

Application web pour gérer votre collection de pièces de 2 euros commémoratives.

## 🚀 Déploiement sur GitHub Pages

### Prérequis

Cette application nécessite un backend FastAPI + MongoDB. Le frontend peut être hébergé sur GitHub Pages, mais vous devez déployer le backend séparément.

### Structure

- **Frontend** : React (dans `/frontend/build/`)
- **Backend** : FastAPI + MongoDB (à déployer sur Render, Railway, ou autre)

### Étapes de déploiement

#### 1. Déployer le Backend

Le backend doit être déployé sur un service cloud :

**Option A : Render (Recommandé)**
1. Créez un compte sur [Render.com](https://render.com)
2. Créez un nouveau "Web Service"
3. Connectez votre dépôt GitHub
4. Configurez :
   - Build Command : `pip install -r backend/requirements.txt`
   - Start Command : `cd backend && uvicorn server:app --host 0.0.0.0 --port $PORT`
5. Ajoutez les variables d'environnement :
   - `MONGO_URL` : Votre URL MongoDB (MongoDB Atlas gratuit)
   - `DB_NAME` : numis_db
6. Notez l'URL de votre backend (ex: `https://votre-app.onrender.com`)

**Option B : Railway**
1. Créez un compte sur [Railway.app](https://railway.app)
2. Créez un nouveau projet depuis GitHub
3. Ajoutez un service MongoDB
4. Configurez les variables d'environnement

#### 2. Configurer le Frontend

Avant de déployer sur GitHub Pages, mettez à jour l'URL du backend :

1. Éditez `/frontend/.env` :
```bash
REACT_APP_BACKEND_URL=https://votre-backend-url.onrender.com
```

2. Reconstruisez le frontend :
```bash
cd frontend
yarn build
```

#### 3. Déployer sur GitHub Pages

1. Créez un dépôt GitHub
2. Copiez le contenu de `/frontend/build/` dans la racine de votre dépôt
3. Ajoutez un fichier `.nojekyll` (déjà créé)
4. Commitez et poussez :
```bash
git add .
git commit -m "Deploy to GitHub Pages"
git push origin main
```

5. Dans les paramètres du dépôt GitHub :
   - Allez dans **Settings** > **Pages**
   - Source : Deploy from a branch
   - Branch : `main` / `root`
   - Cliquez sur **Save**

Votre site sera disponible à : `https://votre-username.github.io/votre-repo/`

### Alternative : Déploiement tout-en-un

Pour un déploiement plus simple, vous pouvez utiliser :

**Vercel** (Gratuit)
- Deploy frontend + backend ensemble
- Supporte FastAPI via Serverless Functions
- Un seul déploiement pour tout

**Netlify** (Gratuit)
- Frontend sur Netlify
- Backend sur Netlify Functions (nécessite adaptation)

## 📦 Contenu du Build

Le dossier `/frontend/build/` contient :
- `index.html` - Page principale
- `static/` - CSS, JS, et autres assets
- `.nojekyll` - Fichier pour GitHub Pages

## 🔧 Variables d'Environnement Backend

```
MONGO_URL=mongodb+srv://...
DB_NAME=numis_db
CORS_ORIGINS=https://votre-username.github.io
```

## 📚 Base de Données

L'application utilise MongoDB avec web scraping automatique depuis la BCE :
- 468 pièces de 2€ commémoratives (2004-2024)
- Images officielles de la Banque Centrale Européenne
- Descriptions en français

Pour initialiser les données, appelez l'endpoint :
```
POST https://votre-backend/api/admin/refresh-coins
```

## 🎨 Fonctionnalités

- ✅ Authentification (Ludivine/Ludivine67)
- ✅ Catalogue complet avec filtres
- ✅ Gestion de collection personnelle
- ✅ Statistiques en temps réel
- ✅ Mode sombre/clair
- ✅ Design minimaliste et moderne

## 📝 Note Importante

**GitHub Pages = Fichiers statiques uniquement**

Le frontend fonctionnera sur GitHub Pages, mais il aura besoin de se connecter à votre backend déployé ailleurs pour :
- Authentification
- Chargement des pièces
- Gestion de la collection
- Statistiques

Sans backend, l'application affichera des erreurs de connexion.

## 🆘 Support

Pour toute question sur le déploiement, consultez :
- [Documentation GitHub Pages](https://pages.github.com/)
- [Documentation Render](https://render.com/docs)
- [Documentation MongoDB Atlas](https://www.mongodb.com/docs/atlas/)
