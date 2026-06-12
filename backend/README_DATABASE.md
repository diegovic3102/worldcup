# PostgreSQL

La app lee la conexion desde `.env`.

1. Copia `.env.example` como `.env`.
2. Ajusta `PGPASSWORD` con la contrasena real de PostgreSQL.
3. Valida la conexion:

```powershell
python -m flask --app app db-check
```

La base ya debe tener estas tablas creadas: `usuarios`, `equipos`, `partidos` y `apuestas`.

El login espera que `usuarios.contrasena_hash` haya sido generado con Werkzeug, por ejemplo:

```powershell
python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('tu-password'))"
```

Configuracion usada por defecto:

```env
PGHOST=127.0.0.1
PGPORT=5432
PGDATABASE=sucesores-worldcup
PGUSER=postgres
PGPASSWORD=pon-tu-password
```
