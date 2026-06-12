# TODO - Segunda fase Ecuador marcadores

- [x] Backend: agregar nueva tabla SQLAlchemy en `backend/models.py`.
- [x] Backend: agregar endpoints en `backend/app.py` para guardar/leer la predicción de la segunda fase (por usuario) y endpoint de contador admin.
- [x] Backend: lógica del contador admin = +1 si los 6 marcadores están completos (no NULL).



- [ ] Frontend: crear componente `frontend/src/components/Apuestas/ApuestasTipo2SegundaFaseEcuadorMarcadores.vue` con formulario (local/visitante) para ECU-CUW, ECU-GER, ECU-CIV.
- [ ] Frontend: en componente nuevo, usuarios normales pueden guardar y ver sus marcadores; admin solo muestra contador.
- [ ] Frontend: conectar el componente nuevo debajo de `ApuestasTipo1GrupoRanking` en `frontend/src/App.vue`.

- [ ] Validar manualmente: compila/levanta frontend y hacer prueba rápida contra backend (guardar y contador admin).

