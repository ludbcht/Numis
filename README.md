# Numis - Collection de Pièces de 2€ Commémoratives

Application web pour gérer votre collection de pièces de 2 euros commémoratives.

## 🌟 Fonctionnalités

- **Catalogue complet** : 468 pièces de 2€ commémoratives (2004-2024)
- **Web scraping automatique** : Données depuis la Banque Centrale Européenne
- **Images officielles** : Photos haute qualité de la BCE
- **Filtres avancés** : Par pays, année, recherche textuelle
- **Gestion de collection** : Ajoutez/retirez des pièces de votre collection
- **Valeurs estimées** : Prix selon l'état (FDC, BU, BE)
- **Statistiques** : Suivi de votre progression et valeur totale
- **Mode sombre** : Interface adaptative clair/sombre
- **Design moderne** : Interface minimaliste et épurée

## 🔐 Identifiants par défaut

- **Nom d'utilisateur** : Ludivine
- **Mot de passe** : Ludivine67

## 🚀 Déploiement

Consultez le fichier [DEPLOYMENT.md](./DEPLOYMENT.md) pour les instructions détaillées de déploiement sur GitHub Pages.

## 🛠️ Technologies

- **Frontend** : React, Tailwind CSS, Framer Motion, Shadcn UI
- **Backend** : FastAPI, Python
- **Base de données** : MongoDB
- **Web scraping** : BeautifulSoup4, httpx

## 📁 Structure du Projet

```
/app/
├── frontend/
│   ├── build/          # Build de production (prêt pour GitHub Pages)
│   ├── src/
│   │   ├── pages/      # Pages React
│   │   ├── components/ # Composants réutilisables
│   │   └── App.js
│   ├── package.json
│   └── .env
├── backend/
│   ├── server.py       # API FastAPI
│   ├── scraper.py      # Web scraper BCE
│   ├── requirements.txt
│   └── .env
└── DEPLOYMENT.md       # Guide de déploiement

```

## 🎯 Utilisation

### Développement local

1. **Backend** :
```bash
cd backend
pip install -r requirements.txt
uvicorn server:app --reload
```

2. **Frontend** :
```bash
cd frontend
yarn install
yarn start
```

### Production

Le dossier `/frontend/build/` contient la version optimisée prête à être déployée.

## 📊 Web Scraping

L'application scrape automatiquement les données depuis :
- **Source principale** : [BCE - Pièces commémoratives](https://www.ecb.europa.eu/euro/coins/comm/html/index.fr.html)
- **Fréquence** : Manuel via endpoint `/api/admin/refresh-coins`
- **Données** : Pays, année, description, tirage, images officielles

## 🌐 API Endpoints

- `POST /api/auth/login` - Authentification
- `GET /api/coins` - Liste des pièces (avec filtres)
- `GET /api/coins/:id` - Détail d'une pièce
- `GET /api/collection` - Collection de l'utilisateur
- `POST /api/collection/add` - Ajouter à la collection
- `DELETE /api/collection/:id` - Retirer de la collection
- `GET /api/collection/stats` - Statistiques
- `POST /api/admin/refresh-coins` - Rafraîchir les données (admin)

## 🎨 Design

- **Palette de couleurs** : Tons neutres avec accent orange
- **Typographie** : Syne (titres), Manrope (corps)
- **Mode sombre** : Palette anthracite élégante
- **Responsive** : Adapté mobile, tablette, desktop

## 📝 Licence

Application créée pour la gestion personnelle de collections numismatiques.

## 🔗 Liens Utiles

- [Banque Centrale Européenne - Pièces commémoratives](https://www.ecb.europa.eu/euro/coins/comm/html/index.fr.html)
- [MongoDB Atlas (gratuit)](https://www.mongodb.com/cloud/atlas)
- [Render (déploiement backend gratuit)](https://render.com)
- [GitHub Pages (déploiement frontend gratuit)](https://pages.github.com)
