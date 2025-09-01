from sqlalchemy import String,Integer,ForeignKey,DateTime,Boolean
from sqlalchemy.orm import Mapped, mapped_column,relationship, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs
from datetime import datetime,timezone

class Base(AsyncAttrs, DeclarativeBase): 
    pass

class User(Base):
    __tablename__ = "User"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255))  
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    

class Chapa(Base):
    __tablename__ = "Chapa"

    chapa_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chapa_nome: Mapped[str] = mapped_column(String(100), nullable=False)

class Voto(Base):
    __tablename__ = "Voto"

    matricula: Mapped[str] = mapped_column(String(100), primary_key=True)
    #documento: Mapped[str] = mapped_column(String(100))
    #estudante: Mapped[str] = mapped_column(String(100))
    horario: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))

    chapa_id: Mapped[int] = mapped_column(ForeignKey("Chapa.chapa_id"), nullable=False)

    # Relacionamento com Chapa
    chapa: Mapped["Chapa"] = relationship("Chapa", back_populates="votos")