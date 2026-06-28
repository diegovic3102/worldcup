import click
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import check_password_hash, generate_password_hash

from config import Config
from database import db
from models import (
    Apuesta,
    Equipo,
    GrupoResultadoOficial,
    Partido,
    PrediccionGrupoRanking,
    PrediccionMarcadorPartido,
    PrediccionSegundaFaseEcuadorMarcadores,
    PrediccionTop4Mundial,
    Top4ResultadoOficial,
    Usuario,
)



def serialize_usuario(usuario):
    return {
        "id": usuario.id,
        "usuario": usuario.usuario,
        "nombres": usuario.nombres,
        "apellidos": usuario.apellidos,
        "es_administrador": usuario.es_administrador,
    }


def password_matches(usuario, password):
    try:
        if check_password_hash(usuario.contrasena_hash, password):
            return True
    except ValueError:
        pass

    if usuario.contrasena_hash == password:
        usuario.contrasena_hash = generate_password_hash(password)
        db.session.commit()
        return True

    return False


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)

    @app.route("/")
    def home():
        return render_template("home.html")

    @app.route("/about")
    def about():
        return render_template("about.html")

    @app.get("/api/health")
    def api_health():
        try:
            counts = {
                "usuarios": db.session.query(Usuario).count(),
                "equipos": db.session.query(Equipo).count(),
                "partidos": db.session.query(Partido).count(),
                "apuestas": db.session.query(Apuesta).count(),
            }
            return jsonify(
                {
                    "status": "ok",
                    "database": "connected",
                    "tables": counts,
                }
            )
        except SQLAlchemyError as error:
            return (
                jsonify(
                    {
                        "status": "error",
                        "database": "disconnected",
                        "detail": str(error.orig) if hasattr(error, "orig") else str(error),
                    }
                ),
                503,
            )

    @app.post("/api/auth/login")
    def login():
        payload = request.get_json(silent=True) or {}
        username = (payload.get("usuario") or "").strip()
        password = payload.get("contrasena") or ""

        if not username or not password:
            return jsonify({"message": "Usuario y contrasena son obligatorios."}), 400

        usuario = Usuario.query.filter_by(usuario=username).first()

        if not usuario or not password_matches(usuario, password):
            return jsonify({"message": "Usuario o contrasena incorrectos."}), 401

        return jsonify({"usuario": serialize_usuario(usuario)})

    @app.post("/api/auth/register")
    def register():
        payload = request.get_json(silent=True) or {}
        username = (payload.get("usuario") or "").strip()
        password = payload.get("contrasena") or ""
        nombres = (payload.get("nombres") or "").strip()
        apellidos = (payload.get("apellidos") or "").strip() or None

        if not username or not password or not nombres:
            return jsonify({"message": "Usuario, nombre y contrasena son obligatorios."}), 400

        if len(username) > 50:
            return jsonify({"message": "El usuario no puede superar 50 caracteres."}), 400

        if len(password) < 6:
            return jsonify({"message": "La contrasena debe tener al menos 6 caracteres."}), 400

        if Usuario.query.filter_by(usuario=username).first():
            return jsonify({"message": "Ese usuario ya existe."}), 409

        usuario = Usuario(
            usuario=username,
            contrasena_hash=generate_password_hash(password),
            nombres=nombres,
            apellidos=apellidos,
            es_administrador=False,
        )
        db.session.add(usuario)
        db.session.commit()

        return jsonify({"usuario": serialize_usuario(usuario)}), 201

    @app.get("/api/equipos")
    def list_equipos():
        equipos = Equipo.query.order_by(Equipo.grupo, Equipo.nombre).all()
        return jsonify(
            [
                {
                    "id": equipo.id,
                    "codigo_fifa": equipo.codigo_fifa,
                    "nombre": equipo.nombre,
                    "grupo": equipo.grupo,
                }
                for equipo in equipos
            ]
        )

    @app.get("/api/partidos")
    def list_partidos():
        partidos = (
            Partido.query.join(Equipo, Partido.equipo_local_id == Equipo.id)
            .order_by(Partido.fecha_hora, Partido.id)
            .all()
        )
        return jsonify(
            [
                {
                    "id": partido.id,
                    "fase": partido.fase,
                    "grupo": partido.grupo,
                    "fecha_hora": partido.fecha_hora.isoformat(),
                    "goles_local": partido.goles_local,
                    "goles_visitante": partido.goles_visitante,
                    "cerrado": partido.cerrado,
                    "equipo_local": {
                        "id": partido.equipo_local.id,
                        "codigo_fifa": partido.equipo_local.codigo_fifa,
                        "nombre": partido.equipo_local.nombre,
                        "grupo": partido.equipo_local.grupo,
                    },
                    "equipo_visitante": {
                        "id": partido.equipo_visitante.id,
                        "codigo_fifa": partido.equipo_visitante.codigo_fifa,
                        "nombre": partido.equipo_visitante.nombre,
                        "grupo": partido.equipo_visitante.grupo,
                    },
                }
                for partido in partidos
            ]
        )

    @app.cli.command("db-check")
    def db_check_command():
        try:
            db.session.execute(text("select 1"))
            table_counts = {
                "usuarios": db.session.query(Usuario).count(),
                "equipos": db.session.query(Equipo).count(),
                "partidos": db.session.query(Partido).count(),
                "apuestas": db.session.query(Apuesta).count(),
                "prediccion_grupo_ranking": db.session.query(PrediccionGrupoRanking).count(),
                "grupo_resultado_oficial": db.session.query(GrupoResultadoOficial).count(),
                "prediccion_marcador_partido": db.session.query(PrediccionMarcadorPartido).count(),
                "prediccion_top4_mundial": db.session.query(PrediccionTop4Mundial).count(),
                "top4_resultado_oficial": db.session.query(Top4ResultadoOficial).count(),
            }

        except SQLAlchemyError as error:
            detail = str(error.orig) if hasattr(error, "orig") else str(error)
            raise click.ClickException(f"Database connection failed: {detail}") from error

        print("Database connection ok.")
        for table_name, count in table_counts.items():
            print(f"{table_name}: {count}")

    def is_admin(user: Usuario) -> bool:
        return bool(getattr(user, "es_administrador", False))

    def points_for_ranking_positions(pred: dict, official: dict) -> float:
        # 1º=1, 2º=0.75, 3º=0.50, 4º=0.25
        weights = {"pos1": 1.0, "pos2": 0.75, "pos3": 0.50, "pos4": 0.25}
        total = 0.0
        for pos_key, weight in weights.items():
            pred_code = pred.get(f"{pos_key}_codigo_fifa")
            official_code = official.get(f"{pos_key}_codigo_fifa")
            if pred_code and official_code and pred_code == official_code:
                total += weight
        return total
    
    def points_for_top4(pred, official):
        weights = {
            "pos1": 1.0,
            "pos2": 0.75,
            "pos3": 0.50,
            "pos4": 0.25
        }

        total = 0.0

        for k, w in weights.items():
            if pred.get(f"{k}_codigo_fifa") == official.get(f"{k}_codigo_fifa"):
                total += w

        return total

    @app.post("/api/apuestas/tipo1/grupo-ranking/me")
    def tipo1_me_save():
        payload = request.get_json(silent=True) or {}
        grupo = (payload.get("grupo") or "").strip()  # esperado 'E'
        pos1 = (payload.get("pos1_codigo_fifa") or "").strip()
        pos2 = (payload.get("pos2_codigo_fifa") or "").strip()
        pos3 = (payload.get("pos3_codigo_fifa") or "").strip()
        pos4 = (payload.get("pos4_codigo_fifa") or "").strip()

        if not grupo or not pos1 or not pos2 or not pos3 or not pos4:
            return jsonify({"message": "Completa grupo y las 4 posiciones."}), 400

        # bloqueo por fecha: antes de iniciar el primer partido del grupo
        first_match = (
            Partido.query.filter_by(grupo=grupo)
            .order_by(Partido.fecha_hora)
            .first()
        )
        if first_match and first_match.fecha_hora:
            from datetime import datetime, timezone
            now = datetime.now(first_match.fecha_hora.tzinfo) if first_match.fecha_hora.tzinfo else datetime.now()
            if now >= first_match.fecha_hora:
                return jsonify({"message": "Ya no puedes apostar para este grupo."}), 403

        user = Usuario.query.filter_by(usuario=(payload.get("usuario") or ""))
        user_id = payload.get("usuario_id")

        # El frontend manda usuarioId en query para este endpoint; si no, intentamos fallbacks.
        if not user_id:
            user_id = request.args.get("usuarioId")
        try:
            user_id = int(user_id)
        except Exception:
            user_id = None

        if not user_id:
            return jsonify({"message": "Usuario no identificado."}), 400

        user = Usuario.query.filter_by(id=user_id).first()
        if not user:
            return jsonify({"message": "Usuario no existe."}), 404

        # upsert prediccion
        pred = PrediccionGrupoRanking.query.filter_by(usuario_id=user.id, grupo=grupo).first()
        if not pred:
            pred = PrediccionGrupoRanking(
                usuario_id=user.id,
                grupo=grupo,
                pos1_codigo_fifa=pos1,
                pos2_codigo_fifa=pos2,
                pos3_codigo_fifa=pos3,
                pos4_codigo_fifa=pos4,
            )
            db.session.add(pred)
        else:
            pred.pos1_codigo_fifa = pos1
            pred.pos2_codigo_fifa = pos2
            pred.pos3_codigo_fifa = pos3
            pred.pos4_codigo_fifa = pos4

        db.session.commit()
        return jsonify({"ok": True}), 200

    @app.post("/api/apuestas/tipo1/grupo-ranking/define-official")
    def tipo1_define_official():
        try:
            payload = request.get_json(silent=True) or {}
            grupo = (payload.get("grupo") or "").strip()
            if not grupo:
                return jsonify({"message": "Grupo requerido."}), 400

            # El backend usa usuarioId desde query.
            user = None
            if request.args.get("usuarioId"):
                try:
                    user_id = int(request.args.get("usuarioId"))
                    user = Usuario.query.filter_by(id=user_id).first()
                except Exception:
                    user = None

            # Fallback: permitir usuario_id en body si viene.
            if not user:
                user_id = payload.get("usuario_id") or request.args.get("usuarioId")
                try:
                    user_id = int(user_id) if user_id is not None else None
                except Exception:
                    user_id = None
                if user_id:
                    user = Usuario.query.filter_by(id=user_id).first()

            if not user or not is_admin(user):
                return jsonify({"message": "No autorizado."}), 403

            pos1 = (payload.get("pos1_codigo_fifa") or "").strip()
            pos2 = (payload.get("pos2_codigo_fifa") or "").strip()
            pos3 = (payload.get("pos3_codigo_fifa") or "").strip()
            pos4 = (payload.get("pos4_codigo_fifa") or "").strip()

            if not pos1 or not pos2 or not pos3 or not pos4:
                return jsonify({"message": "Completa las 4 posiciones oficiales."}), 400

            oficial = GrupoResultadoOficial.query.filter_by(grupo=grupo).first()
            if not oficial:
                oficial = GrupoResultadoOficial(
                    grupo=grupo,
                    pos1_codigo_fifa=pos1,
                    pos2_codigo_fifa=pos2,
                    pos3_codigo_fifa=pos3,
                    pos4_codigo_fifa=pos4,
                )
                db.session.add(oficial)
            else:
                oficial.pos1_codigo_fifa = pos1
                oficial.pos2_codigo_fifa = pos2
                oficial.pos3_codigo_fifa = pos3
                oficial.pos4_codigo_fifa = pos4

            db.session.commit()

            # recalcular puntos
            preds = PrediccionGrupoRanking.query.filter_by(grupo=grupo).all()
            official_dict = {
                "pos1_codigo_fifa": oficial.pos1_codigo_fifa,
                "pos2_codigo_fifa": oficial.pos2_codigo_fifa,
                "pos3_codigo_fifa": oficial.pos3_codigo_fifa,
                "pos4_codigo_fifa": oficial.pos4_codigo_fifa,
            }
            for p in preds:
                pred_dict = {
                    "pos1_codigo_fifa": p.pos1_codigo_fifa,
                    "pos2_codigo_fifa": p.pos2_codigo_fifa,
                    "pos3_codigo_fifa": p.pos3_codigo_fifa,
                    "pos4_codigo_fifa": p.pos4_codigo_fifa,
                }
                pts = points_for_ranking_positions(pred_dict, official_dict)
                p.puntos_obtenidos = pts


            db.session.commit()
            return jsonify({"ok": True, "grupo": grupo}), 200
        except Exception as e:
            # Evita que el frontend reciba HTML y rompa el parseo a JSON.
            return jsonify({"message": "Error al definir resultados oficiales.", "detail": str(e)}), 500


    @app.get("/api/apuestas/tipo1/grupo-ranking/leaderboard")
    def tipo1_leaderboard():
        grupo = (request.args.get("grupo") or "").strip()
        if not grupo:
            return jsonify({"message": "grupo requerido"}), 400

        # Si la tabla de resultado oficial no existe (migración incompleta), devolvemos
        # igualmente las predicciones sin puntaje.
        try:
            oficial = GrupoResultadoOficial.query.filter_by(grupo=grupo).first()
        except Exception:
            oficial = None
        official_defined = bool(oficial)

        preds = PrediccionGrupoRanking.query.filter_by(grupo=grupo).all()


        rows = []
        for p in preds:
            u = Usuario.query.filter_by(id=p.usuario_id).first()
            if not u:
                continue
            score = p.puntos_obtenidos
            rows.append({
                "user_id": p.usuario_id,
                "user_name": u.nombres or u.usuario,
                "score": float(score) if score is not None else None,
            })

        # si official_defined, ordenamos por score; si no, ponemos 0/None al final
        if official_defined:
            rows.sort(key=lambda r: (r["score"] is None, -(r["score"] or 0.0)))
        else:
            rows.sort(key=lambda r: (r["score"] is None, r["user_id"]))

        return jsonify({"official_defined": official_defined, "items": rows}), 200

    @app.get("/api/apuestas/tipo1/grupo-ranking/me")
    def tipo1_me():
        grupo = (request.args.get("grupo") or "").strip()
        user_id = request.args.get("usuarioId")
        if not grupo or not user_id:
            return jsonify({"message": "grupo y usuarioId requeridos."}), 400

        try:
            user_id = int(user_id)
        except Exception:
            return jsonify({"message": "usuarioId inválido."}), 400

        pred = PrediccionGrupoRanking.query.filter_by(usuario_id=user_id, grupo=grupo).first()
        if not pred:
            return jsonify({
                "grupo": grupo,
                "puntos_obtenidos": None,
                "pos1_codigo_fifa": None,
                "pos2_codigo_fifa": None,
                "pos3_codigo_fifa": None,
                "pos4_codigo_fifa": None,
            }), 200

        return jsonify({
            "grupo": pred.grupo,
            "puntos_obtenidos": float(pred.puntos_obtenidos) if pred.puntos_obtenidos is not None else None,
            "pos1_codigo_fifa": pred.pos1_codigo_fifa,
            "pos2_codigo_fifa": pred.pos2_codigo_fifa,
            "pos3_codigo_fifa": pred.pos3_codigo_fifa,
            "pos4_codigo_fifa": pred.pos4_codigo_fifa,
        }), 200

    # ==========================
    # Tipo 2 - Segunda fase Ecuador (marcadores 3 partidos)
    # ==========================

    @app.post("/api/apuestas/tipo2/ecuador-marcadores/me")
    def tipo2_ecuador_marcadores_save():
        payload = request.get_json(silent=True) or {}

        user_id = payload.get("usuario_id") or request.args.get("usuarioId")
        try:
            user_id = int(user_id)
        except Exception:
            return jsonify({"message": "Usuario no identificado."}), 400

        user = Usuario.query.filter_by(id=user_id).first()
        if not user:
            return jsonify({"message": "Usuario no existe."}), 404

        def parse_optional_int(v):
            if v is None:
                return None
            if isinstance(v, str):
                v = v.strip()
                if v == "":
                    return None
                try:
                    return int(v)
                except Exception:
                    return None
            try:
                return int(v)
            except Exception:
                return None

        ecu_cur_local_goles = parse_optional_int(payload.get("ecu_cur_local_goles"))
        ecu_cur_visitante_goles = parse_optional_int(payload.get("ecu_cur_visitante_goles"))

        ecu_ger_local_goles = parse_optional_int(payload.get("ecu_ger_local_goles"))
        ecu_ger_visitante_goles = parse_optional_int(payload.get("ecu_ger_visitante_goles"))

        ecu_civ_local_goles = parse_optional_int(payload.get("ecu_civ_local_goles"))
        ecu_civ_visitante_goles = parse_optional_int(payload.get("ecu_civ_visitante_goles"))

        pred = PrediccionSegundaFaseEcuadorMarcadores.query.filter_by(usuario_id=user.id).first()
        if not pred:
            pred = PrediccionSegundaFaseEcuadorMarcadores(usuario_id=user.id)
            db.session.add(pred)


        # Bloqueo: si el usuario ya tiene los 6 marcadores guardados, no se permite modificar.
        if pred.ecu_cur_local_goles is not None and pred.ecu_cur_visitante_goles is not None and pred.ecu_ger_local_goles is not None and pred.ecu_ger_visitante_goles is not None and pred.ecu_civ_local_goles is not None and pred.ecu_civ_visitante_goles is not None:
            return jsonify({"message": "Ya guardaste tus marcadores en esta segunda fase."}), 403

        pred.ecu_cur_local_goles = ecu_cur_local_goles

        pred.ecu_cur_visitante_goles = ecu_cur_visitante_goles
        pred.ecu_ger_local_goles = ecu_ger_local_goles
        pred.ecu_ger_visitante_goles = ecu_ger_visitante_goles
        pred.ecu_civ_local_goles = ecu_civ_local_goles
        pred.ecu_civ_visitante_goles = ecu_civ_visitante_goles

        db.session.commit()
        return jsonify({"ok": True}), 200

    @app.get("/api/apuestas/tipo2/ecuador-marcadores/me")
    def tipo2_ecuador_marcadores_me():
        user_id = request.args.get("usuarioId")
        if not user_id:
            return jsonify({"message": "usuarioId requerido."}), 400

        try:
            user_id = int(user_id)
        except Exception:
            return jsonify({"message": "usuarioId inválido."}), 400

        pred = PrediccionSegundaFaseEcuadorMarcadores.query.filter_by(usuario_id=user_id).first()

        if not pred:
            return jsonify(
                {
                    "ecu_cur_local_goles": None,
                    "ecu_cur_visitante_goles": None,
                    "ecu_ger_local_goles": None,
                    "ecu_ger_visitante_goles": None,
                    "ecu_civ_local_goles": None,
                    "ecu_civ_visitante_goles": None,
                }
            ), 200

        return jsonify(
            {
                "ecu_cur_local_goles": pred.ecu_cur_local_goles,
                "ecu_cur_visitante_goles": pred.ecu_cur_visitante_goles,
                "ecu_ger_local_goles": pred.ecu_ger_local_goles,
                "ecu_ger_visitante_goles": pred.ecu_ger_visitante_goles,
                "ecu_civ_local_goles": pred.ecu_civ_local_goles,
                "ecu_civ_visitante_goles": pred.ecu_civ_visitante_goles,
            }
        ), 200


    @app.get("/api/apuestas/tipo2/ecuador-marcadores/contador")
    def tipo2_ecuador_marcadores_contador():
        # Admin: contar usuarios que tengan los 3 partidos completos (6 valores no NULL)
        user = None
        if request.args.get("usuarioId"):
            try:
                admin_id = int(request.args.get("usuarioId"))
                user = Usuario.query.filter_by(id=admin_id).first()
            except Exception:
                user = None

        if not user or not is_admin(user):
            return jsonify({"message": "No autorizado."}), 403

        count_completed = (
            db.session.query(db.func.count(PrediccionSegundaFaseEcuadorMarcadores.id))
            .filter(PrediccionSegundaFaseEcuadorMarcadores.ecu_cur_local_goles.isnot(None))
            .filter(PrediccionSegundaFaseEcuadorMarcadores.ecu_cur_visitante_goles.isnot(None))
            .filter(PrediccionSegundaFaseEcuadorMarcadores.ecu_ger_local_goles.isnot(None))
            .filter(PrediccionSegundaFaseEcuadorMarcadores.ecu_ger_visitante_goles.isnot(None))
            .filter(PrediccionSegundaFaseEcuadorMarcadores.ecu_civ_local_goles.isnot(None))
            .filter(PrediccionSegundaFaseEcuadorMarcadores.ecu_civ_visitante_goles.isnot(None))
            .scalar()
        )

        return jsonify({"completed_count": int(count_completed or 0)}), 200

    @app.get("/api/apuestas/top4/equipos")
    def top4_equipos():

        equipos_16avos = (
            Equipo.query
            .filter_by(clasificado_16avos=True)
            .order_by(Equipo.nombre)
            .all()
        )

        return jsonify([
            {
                "codigo_fifa": e.codigo_fifa,
                "nombre": e.nombre,
                "grupo": e.grupo
            }
            for e in equipos_16avos
        ])


    @app.post("/api/apuestas/top4/mundial/me")
    def top4_save():

        payload = request.get_json() or {}
        user_id = payload.get("usuario_id")

        if not user_id:
            return jsonify({"message": "Usuario requerido"}), 400

        pred = PrediccionTop4Mundial.query.filter_by(usuario_id=user_id).first()

        # 🚫 BLOQUEO TOTAL
        if pred and pred.pos1_codigo_fifa:
            return jsonify({
                "message": "Ya registraste tu Top 4 y no puede modificarse."
            }), 403

        if not pred:
            pred = PrediccionTop4Mundial(usuario_id=user_id)
            db.session.add(pred)

        pred.pos1_codigo_fifa = payload.get("pos1")
        pred.pos2_codigo_fifa = payload.get("pos2")
        pred.pos3_codigo_fifa = payload.get("pos3")
        pred.pos4_codigo_fifa = payload.get("pos4")

        db.session.commit()

        return jsonify({"ok": True})

    @app.get("/api/apuestas/top4/mundial/me")
    def top4_me():

        user_id = request.args.get("usuarioId")

        if not user_id:
            return jsonify({"message": "usuarioId requerido"}), 400

        try:
            user_id = int(user_id)
        except:
            return jsonify({"message": "usuarioId inválido"}), 400

        pred = PrediccionTop4Mundial.query.filter_by(usuario_id=user_id).first()

        if not pred:
            return jsonify({
                "pos1": None,
                "pos2": None,
                "pos3": None,
                "pos4": None,
                "locked": False
            })

        return jsonify({
            "pos1": pred.pos1_codigo_fifa,
            "pos2": pred.pos2_codigo_fifa,
            "pos3": pred.pos3_codigo_fifa,
            "pos4": pred.pos4_codigo_fifa,
            "locked": bool(pred.pos1_codigo_fifa),
            "puntos_obtenidos": pred.puntos_obtenidos
        })
        
    @app.post("/api/apuestas/top4/mundial/define-official")
    def top4_define_official():

        payload = request.get_json(silent=True) or {}

        user_id = payload.get("usuario_id")
        if not user_id:
            return jsonify({"message": "No autorizado"}), 403

        user = Usuario.query.filter_by(id=user_id).first()

        if not user or not is_admin(user):
            return jsonify({"message": "No autorizado"}), 403

        pos1 = payload.get("pos1")
        pos2 = payload.get("pos2")
        pos3 = payload.get("pos3")
        pos4 = payload.get("pos4")

        if not pos1 or not pos2 or not pos3 or not pos4:
            return jsonify({"message": "Completar Top 4 oficial"}), 400

        oficial = Top4ResultadoOficial.query.first()

        if not oficial:
            oficial = Top4ResultadoOficial()
            db.session.add(oficial)

        oficial.pos1_codigo_fifa = pos1
        oficial.pos2_codigo_fifa = pos2
        oficial.pos3_codigo_fifa = pos3
        oficial.pos4_codigo_fifa = pos4

        db.session.commit()

        # 🔥 CALCULAR PUNTOS (IMPORTANTE)
        preds = PrediccionTop4Mundial.query.all()

        official_dict = {
            "pos1": oficial.pos1_codigo_fifa,
            "pos2": oficial.pos2_codigo_fifa,
            "pos3": oficial.pos3_codigo_fifa,
            "pos4": oficial.pos4_codigo_fifa,
        }

        for p in preds:
            pred_dict = {
                "pos1_codigo_fifa": p.pos1_codigo_fifa,
                "pos2_codigo_fifa": p.pos2_codigo_fifa,
                "pos3_codigo_fifa": p.pos3_codigo_fifa,
                "pos4_codigo_fifa": p.pos4_codigo_fifa,
            }

            p.puntos_obtenidos = points_for_top4(pred_dict, official_dict)

        db.session.commit()

        return jsonify({"ok": True}) 


    return app



app = create_app()
