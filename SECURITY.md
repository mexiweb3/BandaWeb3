# 🔐 Seguridad de Credenciales

## Archivos Protegidos (NO se suben a GitHub)

Los siguientes archivos están en `.gitignore` y **NUNCA** deben subirse al repositorio:

### 📧 Gmail API
- `credentials.json` - Credenciales OAuth de Google Cloud Console
- `token.json` - Token de acceso generado automáticamente

### 🔑 Otros Archivos Sensibles
- `.env` - Variables de entorno
- `venv/` - Entorno virtual de Python

## ✅ Verificación de Seguridad

Para verificar que tus credenciales están protegidas:

```bash
# Ver qué archivos están siendo rastreados por git
git ls-files | grep credentials
git ls-files | grep token

# Si alguno aparece, elimínalo del repositorio:
git rm --cached credentials.json
git rm --cached token.json
git commit -m "Remove sensitive files"
```

## 📝 Configuración Inicial

1. Copia `credentials.json.example` a `credentials.json`
2. Reemplaza los valores con tus credenciales reales de Google Cloud Console
3. **NUNCA** compartas `credentials.json` o `token.json`

## ⚠️ Si Accidentalmente Subiste Credenciales

Si subiste credenciales por error:

1. **Revoca las credenciales inmediatamente** en Google Cloud Console
2. Genera nuevas credenciales
3. Elimina el archivo del historial de git:
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch credentials.json" \
     --prune-empty --tag-name-filter cat -- --all
   ```
4. Fuerza el push:
   ```bash
   git push origin --force --all
   ```

## 🛡️ Mejores Prácticas

- ✅ Siempre revisa `.gitignore` antes de hacer commit
- ✅ Usa `git status` para ver qué archivos se van a subir
- ✅ Nunca hagas `git add .` sin revisar primero
- ✅ Considera usar `git-secrets` para prevención automática
