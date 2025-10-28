# Tests pour l'API High School Management System

Ce répertoire contient une suite complète de tests pour l'API FastAPI de gestion des activités scolaires.

## Structure des tests

```
tests/
├── __init__.py                 # Fichier d'initialisation du package
├── conftest.py                 # Configuration et fixtures partagées
├── test_api.py                 # Tests des endpoints API principaux
├── test_integration.py         # Tests d'intégration et workflows
├── test_business.py           # Tests de logique métier
└── test_performance.py        # Tests de performance et de charge
```

## Types de tests

### 1. Tests API (`test_api.py`)
- **TestRootEndpoint** : Tests de l'endpoint racine et redirections
- **TestActivitiesEndpoint** : Tests de récupération des activités
- **TestSignupEndpoint** : Tests d'inscription aux activités
- **TestRemoveParticipantEndpoint** : Tests de suppression de participants
- **TestDataIntegrity** : Tests d'intégrité des données

### 2. Tests d'intégration (`test_integration.py`)
- **TestIntegrationWorkflows** : Tests de workflows complets
- **TestErrorHandling** : Tests de gestion d'erreurs
- **TestDataValidation** : Tests de validation des données

### 3. Tests métier (`test_business.py`)
- **TestBusinessRules** : Tests des règles métier
- **TestStudentExperience** : Tests du parcours étudiant
- **TestTeacherAdministration** : Tests d'administration
- **TestSystemReliability** : Tests de fiabilité système

### 4. Tests de performance (`test_performance.py`)
- **TestPerformance** : Tests de temps de réponse
- **TestScalability** : Tests de montée en charge
- **TestMemoryUsage** : Tests d'utilisation mémoire
- **TestErrorRecovery** : Tests de récupération d'erreur

## Configuration

### Fixtures principales (`conftest.py`)
- `client` : Client de test FastAPI
- `sample_activity` : Données d'activité d'exemple
- `test_email` : Email de test pour les opérations

## Exécution des tests

### Option 1 : Script personnalisé
```bash
# Exécution simple
./run_tests.sh

# Avec couverture de code
./run_tests.sh --coverage

# Mode rapide (arrêt au premier échec)
./run_tests.sh --fast

# Mode verbose
./run_tests.sh --verbose

# Mode silencieux
./run_tests.sh --quiet
```

### Option 2 : pytest direct
```bash
# Tous les tests
python -m pytest tests/ -v

# Tests spécifiques
python -m pytest tests/test_api.py -v

# Avec couverture
python -m pytest tests/ --cov=src --cov-report=html

# Arrêt au premier échec
python -m pytest tests/ -x

# Tests parallèles (si pytest-xdist installé)
python -m pytest tests/ -n auto
```

### Option 3 : Exécution par catégorie
```bash
# Tests API uniquement
python -m pytest tests/test_api.py -v

# Tests d'intégration uniquement
python -m pytest tests/test_integration.py -v

# Tests métier uniquement
python -m pytest tests/test_business.py -v

# Tests de performance uniquement
python -m pytest tests/test_performance.py -v
```

## Couverture de code

Pour générer un rapport de couverture :

```bash
python -m pytest tests/ --cov=src --cov-report=html --cov-report=term
```

Le rapport HTML sera généré dans `htmlcov/index.html`.

## Dépendances

Les tests nécessitent les packages suivants (listés dans `requirements.txt`) :
- `pytest` : Framework de test
- `httpx` : Client HTTP pour tester FastAPI
- `fastapi` : Framework web
- `uvicorn` : Serveur ASGI

## Résultats attendus

Les tests vérifient :

1. **Fonctionnalité** : Tous les endpoints fonctionnent correctement
2. **Validation** : Les données sont validées et les erreurs gérées
3. **Intégrité** : L'état des données reste cohérent
4. **Performance** : L'API répond dans des délais acceptables
5. **Fiabilité** : Le système récupère correctement après les erreurs
6. **Logique métier** : Les règles métier sont respectées

## Ajout de nouveaux tests

### Conventions de nommage
- Fichiers de test : `test_*.py`
- Classes de test : `Test*`
- Méthodes de test : `test_*`

### Structure recommandée
```python
class TestNewFeature:
    """Tests for new feature"""
    
    def test_positive_case(self, client):
        """Test successful operation"""
        # Arrange
        # Act
        # Assert
    
    def test_negative_case(self, client):
        """Test error handling"""
        # Arrange
        # Act
        # Assert
```

### Bonnes pratiques
1. Utiliser des noms de test descriptifs
2. Inclure des docstrings
3. Suivre le pattern Arrange-Act-Assert
4. Tester les cas positifs et négatifs
5. Nettoyer après les tests si nécessaire

## Debugging

Pour déboguer les tests :

```bash
# Mode verbose avec traceback complet
python -m pytest tests/ -vv --tb=long

# Arrêt au premier échec avec debugger
python -m pytest tests/ -x --pdb

# Affichage des print statements
python -m pytest tests/ -s
```

## CI/CD Integration

Ces tests sont conçus pour être intégrés dans un pipeline CI/CD :

```yaml
# Exemple GitHub Actions
- name: Run tests
  run: |
    python -m pytest tests/ --cov=src --cov-report=xml
    
- name: Upload coverage
  uses: codecov/codecov-action@v1
```