# Criar todos os __init__.py necessários
touch app/__init__.py
touch app/core/__init__.py
touch app/models/__init__.py
touch app/services/__init__.py
touch app/engines/__init__.py

# Commit e push
git add app/__init__.py app/*/\_\_init\_\_.py
git commit -m "fix: adicionar __init__.py para módulos Python"
git push origin main