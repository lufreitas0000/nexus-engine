import datetime
from typing import List

from sqlalchemy import Column, String, ForeignKey, Table, Text, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

citation_table = Table(
    "citations",
    Base.metadata,
    Column("referrer_id", String, ForeignKey("papers.arxiv_id"), primary_key=True),
    Column("referee_id", String, ForeignKey("papers.arxiv_id"), primary_key=True),
)

class PaperORM(Base):
    __tablename__ = "papers"

    arxiv_id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(Text)
    abstract: Mapped[str] = mapped_column(Text)
    published_date: Mapped[datetime.datetime] = mapped_column(DateTime)

    citations: Mapped[List["PaperORM"]] = relationship(
        "PaperORM",
        secondary=citation_table,
        primaryjoin=arxiv_id == citation_table.c.referrer_id,
        secondaryjoin=arxiv_id == citation_table.c.referee_id,
        back_populates="cited_by",
    )

    cited_by: Mapped[List["PaperORM"]] = relationship(
        "PaperORM",
        secondary=citation_table,
        primaryjoin=arxiv_id == citation_table.c.referee_id,
        secondaryjoin=arxiv_id == citation_table.c.referrer_id,
        back_populates="citations",
    )
