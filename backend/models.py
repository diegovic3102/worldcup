from datetime import datetime

from database import db


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50), nullable=False, unique=True, index=True)
    contrasena_hash = db.Column(db.Text, nullable=False)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100))
    es_administrador = db.Column(db.Boolean, default=False)
    fecha_creacion = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    apuestas = db.relationship(
        "Apuesta",
        back_populates="usuario",
        cascade="all, delete-orphan",
    )

    predicciones_grupo_ranking = db.relationship(
        "PrediccionGrupoRanking",
        back_populates="usuario",
        cascade="all, delete-orphan",
    )

    predicciones_marcador_partido = db.relationship(
        "PrediccionMarcadorPartido",
        back_populates="usuario",
        cascade="all, delete-orphan",
    )

    predicciones_top4_mundial = db.relationship(
        "PrediccionTop4Mundial",
        back_populates="usuario",
        cascade="all, delete-orphan",
    )


class Equipo(db.Model):
    __tablename__ = "equipos"

    id = db.Column(db.Integer, primary_key=True)
    codigo_fifa = db.Column(db.String(3), nullable=False, unique=True, index=True)
    nombre = db.Column(db.String(100), nullable=False)
    grupo = db.Column(db.String(2))

    partidos_local = db.relationship(
        "Partido",
        back_populates="equipo_local",
        foreign_keys="Partido.equipo_local_id",
    )
    partidos_visitante = db.relationship(
        "Partido",
        back_populates="equipo_visitante",
        foreign_keys="Partido.equipo_visitante_id",
    )


class Partido(db.Model):
    __tablename__ = "partidos"

    id = db.Column(db.Integer, primary_key=True)
    fase = db.Column(db.String(30), nullable=False)
    grupo = db.Column(db.String(2))
    equipo_local_id = db.Column(db.Integer, db.ForeignKey("equipos.id"), nullable=False)
    equipo_visitante_id = db.Column(db.Integer, db.ForeignKey("equipos.id"), nullable=False)
    fecha_hora = db.Column(db.DateTime, nullable=False)
    goles_local = db.Column(db.SmallInteger)
    goles_visitante = db.Column(db.SmallInteger)
    cerrado = db.Column(db.Boolean, default=False)
    fecha_creacion = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    equipo_local = db.relationship(
        "Equipo",
        back_populates="partidos_local",
        foreign_keys=[equipo_local_id],
    )
    equipo_visitante = db.relationship(
        "Equipo",
        back_populates="partidos_visitante",
        foreign_keys=[equipo_visitante_id],
    )
    apuestas = db.relationship(
        "Apuesta",
        back_populates="partido",
        cascade="all, delete-orphan",
    )


class PrediccionGrupoRanking(db.Model):
    __tablename__ = "prediccion_grupo_ranking"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    grupo = db.Column(db.String(2), nullable=False, index=True)

    pos1_codigo_fifa = db.Column(db.String(3), nullable=False)
    pos2_codigo_fifa = db.Column(db.String(3), nullable=False)
    pos3_codigo_fifa = db.Column(db.String(3), nullable=False)
    pos4_codigo_fifa = db.Column(db.String(3), nullable=False)

    puntos_obtenidos = db.Column(db.Numeric(5, 2), nullable=True)
    fecha_guardado = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    usuario = db.relationship("Usuario", back_populates="predicciones_grupo_ranking")

    __table_args__ = (
        db.UniqueConstraint(
            "usuario_id",
            "grupo",
            name="uq_prediccion_grupo_usuario_grupo",
        ),
    )


class GrupoResultadoOficial(db.Model):
    __tablename__ = "grupo_resultado_oficial"

    id = db.Column(db.Integer, primary_key=True)
    grupo = db.Column(db.String(2), nullable=False, unique=True, index=True)

    pos1_codigo_fifa = db.Column(db.String(3), nullable=False)
    pos2_codigo_fifa = db.Column(db.String(3), nullable=False)
    pos3_codigo_fifa = db.Column(db.String(3), nullable=False)
    pos4_codigo_fifa = db.Column(db.String(3), nullable=False)

    fecha_definicion = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class PrediccionMarcadorPartido(db.Model):
    __tablename__ = "prediccion_marcador_partido"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    partido_id = db.Column(db.Integer, db.ForeignKey("partidos.id"), nullable=False)

    goles_local = db.Column(db.SmallInteger, nullable=False)
    goles_visitante = db.Column(db.SmallInteger, nullable=False)

    puntos_obtenidos = db.Column(db.Numeric(5, 2), nullable=True)
    fecha_guardado = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    usuario = db.relationship("Usuario", back_populates="predicciones_marcador_partido")
    partido = db.relationship("Partido")

    __table_args__ = (
        db.UniqueConstraint(
            "usuario_id",
            "partido_id",
            name="uq_prediccion_marcador_usuario_partido",
        ),
    )


class PrediccionTop4Mundial(db.Model):
    __tablename__ = "prediccion_top4_mundial"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)

    pos1_codigo_fifa = db.Column(db.String(3), nullable=False)
    pos2_codigo_fifa = db.Column(db.String(3), nullable=False)
    pos3_codigo_fifa = db.Column(db.String(3), nullable=False)
    pos4_codigo_fifa = db.Column(db.String(3), nullable=False)

    puntos_obtenidos = db.Column(db.Numeric(5, 2), nullable=True)
    fecha_guardado = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    usuario = db.relationship("Usuario", back_populates="predicciones_top4_mundial")

    __table_args__ = (
        db.UniqueConstraint(
            "usuario_id",
            name="uq_prediccion_top4_usuario",
        ),
    )


class Top4ResultadoOficial(db.Model):
    __tablename__ = "top4_resultado_oficial"

    id = db.Column(db.Integer, primary_key=True)

    pos1_codigo_fifa = db.Column(db.String(3), nullable=False)
    pos2_codigo_fifa = db.Column(db.String(3), nullable=False)
    pos3_codigo_fifa = db.Column(db.String(3), nullable=False)
    pos4_codigo_fifa = db.Column(db.String(3), nullable=False)

    fecha_definicion = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class PrediccionSegundaFaseEcuadorMarcadores(db.Model):
    __tablename__ = "prediccion_segunda_fase_ecuador_marcadores"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(
        db.Integer, db.ForeignKey("usuarios.id"), nullable=False, unique=True
    )

    ecu_cur_local_goles = db.Column(db.SmallInteger, nullable=True)
    ecu_cur_visitante_goles = db.Column(db.SmallInteger, nullable=True)

    ecu_ger_local_goles = db.Column(db.SmallInteger, nullable=True)
    ecu_ger_visitante_goles = db.Column(db.SmallInteger, nullable=True)

    ecu_civ_local_goles = db.Column(db.SmallInteger, nullable=True)
    ecu_civ_visitante_goles = db.Column(db.SmallInteger, nullable=True)

    fecha_guardado = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    usuario = db.relationship(
        "Usuario",
        backref="prediccion_segunda_fase_ecuador_marcadores",
        uselist=False,
    )


class Apuesta(db.Model):
    __tablename__ = "apuestas"
    __table_args__ = (
        db.UniqueConstraint("usuario_id", "partido_id", name="uq_apuesta_usuario_partido"),
    )

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    partido_id = db.Column(db.Integer, db.ForeignKey("partidos.id"), nullable=False)
    pronostico_local = db.Column(db.SmallInteger, nullable=False)
    pronostico_visitante = db.Column(db.SmallInteger, nullable=False)
    monto = db.Column(db.Numeric(10, 2))
    fecha_apuesta = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    usuario = db.relationship("Usuario", back_populates="apuestas")
    partido = db.relationship("Partido", back_populates="apuestas")


