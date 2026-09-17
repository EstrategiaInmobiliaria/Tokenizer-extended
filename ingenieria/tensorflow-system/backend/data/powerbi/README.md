# Power BI Data Store

SQLite local por defecto (`predicciones.db`) cuando no hay `DATABASE_URL` de Postgres.

En producción usa PostgreSQL vía Docker Compose o `DATABASE_URL`.

Tabla: `predicciones_tensorflow`
