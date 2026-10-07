# Portfolio
Portfolio María del Valle 2026

## Actualización automática

El servicio `updater` consulta `origin/main` cada 5 minutos y aplica únicamente
actualizaciones `fast-forward`. Como el contenido está montado directamente en
`nginx`, los cambios quedan disponibles sin reiniciar el servidor web.

Para cambiar el intervalo:

```text
UPDATE_INTERVAL_SECONDS=60 docker compose up -d updater
```

El actualizador no sobrescribe cambios locales versionados ni resuelve ramas
divergentes. Consultar su actividad con:

```text
docker compose logs -f updater
```

## Analítica con Umami

Umami 3.4.0 y PostgreSQL 15 se ejecutan en este mismo Compose. El panel está en
<http://192.168.1.170:3003>, accesible desde la red local.

- Usuario: `admin`.
- Contraseña generada: archivo local `.env.umami-admin` (permisos `0600`).
- Credenciales de base de datos y claves de Umami: `.env.umami` (permisos `0600`).
- Ambos archivos están excluidos de Git. Conservarlos para recuperar la instalación.
- Sitio: **María del Valle · Portfolio**, ID `9bff8383-9d93-4e1e-a158-c5a337184bc4`.
- Los datos persisten en el volumen Compose `umami-db-data`.

`index.html` carga el tracker desde `/analytics/script.js` en el dominio público.
Nginx reenvía únicamente ese script y `POST /analytics/api/send` a Umami, incluyendo
la IP que Cloudflare proporciona para identificar el país del visitante. El panel
no se publica a través del túnel. La resolución dinámica de Docker permite seguir
sirviendo el portfolio aunque Umami no esté disponible.

Se registran visitas a partir de la instalación; no hay datos históricos previos.
El tracker respeta Do Not Track y excluye parámetros de búsqueda de las URLs.
No se han activado grabaciones de sesión. La prueba inicial dejó una visita en `/`.

### Instalación inicial

Desde el directorio del proyecto, con el token de Cloudflare ya configurado:

```sh
python3 setup-umami.py prepare
docker compose config --quiet
docker compose up -d --wait nginx umami
python3 setup-umami.py bootstrap
```

`prepare` genera secretos solo si no existen; `bootstrap` cambia la contraseña
predeterminada y registra el sitio. Puede repetirse mientras la contraseña del
administrador coincida con `.env.umami-admin`. Si se cambia desde el panel,
actualizar ese archivo antes de volver a usar `bootstrap`.

### Operación y copias de seguridad

```sh
docker compose ps
docker compose logs --tail=100 umami umami-db
```

Guardar las copias fuera del directorio público del portfolio:

```sh
umask 077
docker compose exec -T umami-db pg_dump -U umami -d umami --clean --if-exists > "$HOME/umami-backup.sql"
```

Respaldar también `.env.umami` y `.env.umami-admin` en una ubicación privada.
Para restaurar una copia, con la base de datos encendida (reemplaza sus datos):

```sh
docker compose stop umami
docker compose exec -T umami-db psql -v ON_ERROR_STOP=1 -U umami -d umami < "$HOME/umami-backup.sql"
docker compose up -d --wait umami
```

La imagen de Umami está fijada por digest en `docker-compose.yml`. Antes de
actualizarla, realizar una copia; cambiar el digest por el de la versión elegida
y ejecutar `docker compose up -d --wait umami`. No eliminar el volumen de datos.
