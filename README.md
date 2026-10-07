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
