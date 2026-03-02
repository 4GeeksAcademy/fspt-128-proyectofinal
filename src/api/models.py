from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

db = SQLAlchemy()

evento_estudiantes = Table(
    "evento_estudiantes",
    db.Model.metadata,
    Column("evento_id", Integer, ForeignKey(
        "eventos.evento_id"), primary_key=True),
    Column("alumnos_id", Integer, ForeignKey(
        "estudiantes.id"), primary_key=True),
)

tutor_estudiantes = Table(
    "tutor_estudiantes",
    db.Model.metadata,
    Column("estudiantes_id", Integer, ForeignKey(
        "estudiantes.id"), primary_key=True),
    Column("tutor_id", Integer, ForeignKey(
        "tutor_legal.id"), primary_key=True),
    Column("parentesco", String(255))
)


class SuperAdmin(db.Model):
    __tablename__ = "super_admin"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    nombre_colegio: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    rol_id: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    aulas = relationship("Aula", back_populates="colegio", foreign_keys="[Aula.colegio_id]")

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "nombre_colegio": self.nombre_colegio,
            "rol_id": self.rol_id
        }

class TutorLegal(db.Model):
    __tablename__ = "tutor_legal"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=True)
    email: Mapped[str] = mapped_column(String(120), nullable=True)
    password: Mapped[str] = mapped_column(String(120), nullable=True)
    telephone: Mapped[str] = mapped_column(String(80), nullable=True)
    rol_id: Mapped[int] = mapped_column(Integer, default=3, nullable=False)

    estudiantes = relationship(
        "Estudiantes",
        secondary=tutor_estudiantes,
        back_populates="tutores"
    )

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "telephone": self.telephone,
            "rol_id": self.rol_id
        }


class Profesor(db.Model):
    __tablename__ = "profesor"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=True)
    email: Mapped[str] = mapped_column(String(120), nullable=True)
    password: Mapped[str] = mapped_column(String(120), nullable=True)
    telephone: Mapped[str] = mapped_column(String(120), nullable=True)
    rol_id: Mapped[int] = mapped_column(Integer, default=2, nullable=False)

    estudiantes = relationship("Estudiantes", back_populates="profesor")
    eventos = relationship("Eventos", back_populates="profesor")
    aulas = relationship("Aula", back_populates="profesor")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "telephone": self.telephone,
            "rol_id": self.rol_id
        }


class Aula(db.Model):
    __tablename__ = "aula"

    aula_id: Mapped[int] = mapped_column(primary_key=True)
    curso: Mapped[str] = mapped_column(String(80), nullable=True)
    clase: Mapped[str] = mapped_column(String(40), nullable=True)

    profesor_id: Mapped[int] = mapped_column(
        ForeignKey("profesor.id"),
        nullable=True
    )
    colegio_id: Mapped[int] = mapped_column(
        ForeignKey("super_admin.id"),
        nullable=True
    )

    profesor = relationship("Profesor", back_populates="aulas")
    colegio = relationship("SuperAdmin", back_populates="aulas", foreign_keys=[colegio_id])
    estudiantes = relationship("Estudiantes", back_populates="aula")

    def serialize(self):
        return {
            "aula_id": self.aula_id,
            "curso": self.curso,
            "clase": self.clase,
            "profesor_id": self.profesor_id,
            "estudiantes": [estudiante.serialize() for estudiante in self.estudiantes]
        }

class Estudiantes(db.Model):
    __tablename__ = "estudiantes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=True)

    profesor_id: Mapped[int] = mapped_column(
        ForeignKey("profesor.id"),
        nullable=True
    )
    aula_id: Mapped[int] = mapped_column(
        ForeignKey("aula.aula_id"),
        nullable=True
    )
    profesor = relationship("Profesor", back_populates="estudiantes")
    aula = relationship("Aula", back_populates="estudiantes")
    eventos = relationship(
        "Eventos",
        secondary=evento_estudiantes,
        back_populates="alumnos"
    )
    tutores = relationship(
        "TutorLegal",
        secondary=tutor_estudiantes,
        back_populates="estudiantes"
    )
    calificaciones = relationship(
        "Calificaciones", back_populates="estudiante")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "profesor_id": self.profesor_id
        }


class Asignaturas(db.Model):
    __tablename__ = "asignaturas"

    asignatura_id: Mapped[int] = mapped_column(primary_key=True)
    nombre_asignatura: Mapped[str] = mapped_column(String(120), nullable=True)

    calificaciones = relationship(
        "Calificaciones", back_populates="asignatura")

    def serialize(self):
        return {
            "nombre_asignatura": self.nombre_asignatura,
            "asignatura_id": self.asignatura_id,
        }


class Calificaciones(db.Model):
    __tablename__ = "calificaciones"

    calificacion_id: Mapped[int] = mapped_column(primary_key=True)
    calificacion: Mapped[int] = mapped_column(nullable=True)

    asignatura_id: Mapped[int] = mapped_column(
        ForeignKey("asignaturas.asignatura_id"),
        nullable=True
    )
    estudiante_id: Mapped[int] = mapped_column(
        ForeignKey("estudiantes.id"),
        nullable=True
    )
    asignatura = relationship("Asignaturas", back_populates="calificaciones")
    estudiante = relationship("Estudiantes", back_populates="calificaciones")

    def serialize(self):
        return {
            "calificacion_id": self.calificacion_id,
            "calificacion": self.calificacion,
        }


class tipo_evento(enum.Enum):
    EXCURSION = "excursion"
    EXAMEN = "examen"
    REUNION = "reunion"
    EVENTO_SOLIDARIO = "evento solidario"


class Eventos(db.Model):
    __tablename__ = "eventos"

    evento_id: Mapped[int] = mapped_column(primary_key=True)
    nombre_evento: Mapped[str] = mapped_column(String(80), nullable=True)
    localizacion: Mapped[str] = mapped_column(String(80), nullable=True)
    tipo_de_evento: Mapped[tipo_evento] = mapped_column(
        Enum(tipo_evento), nullable=False)
    profesor_id: Mapped[int] = mapped_column(
        ForeignKey("profesor.id"),
        nullable=True
    )

    profesor = relationship("Profesor", back_populates="eventos")
    alumnos = relationship(
        "Estudiantes",
        secondary=evento_estudiantes,
        back_populates="eventos"
    )

    def serialize(self):
        return {
            "evento_id": self.evento_id,
            "nombre_evento": self.nombre_evento,
            "localizacion": self.localizacion,
            "tipo_de_evento": self.tipo_de_evento.value,
        }
