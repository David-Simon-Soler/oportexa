from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RawModel(BaseModel):
    """Faithful exploratory representation; unknown API fields are preserved."""

    model_config = ConfigDict(extra="allow")


class RawCallSummary(RawModel):
    id: int | None = None
    mrr: bool | None = None
    numero_convocatoria: str = Field(alias="numeroConvocatoria")
    descripcion: str | None = None
    descripcion_leng: str | None = Field(default=None, alias="descripcionLeng")
    fecha_recepcion: date | None = Field(default=None, alias="fechaRecepcion")
    nivel1: str | None = None
    nivel2: str | None = None
    nivel3: str | None = None
    codigo_invente: str | None = Field(default=None, alias="codigoInvente")


class RawPage(RawModel):
    content: list[RawCallSummary] = []
    total_pages: int | None = Field(default=None, alias="totalPages")
    total_elements: int | None = Field(default=None, alias="totalElements")
    number: int | None = None
    size: int | None = None
    number_of_elements: int | None = Field(default=None, alias="numberOfElements")
    last: bool | None = None
    first: bool | None = None
    empty: bool | None = None
    advertencia: str | None = None


class RawNestedDescription(RawModel):
    descripcion: str | None = None
    codigo: str | None = None


class RawOrgan(RawModel):
    nivel1: str | None = None
    nivel2: str | None = None
    nivel3: str | None = None


class RawDocument(RawModel):
    id: int | None = None
    nombre_fic: str | None = Field(default=None, alias="nombreFic")
    descripcion: str | None = None
    longitud: int | None = Field(default=None, alias="long")
    fecha_modificacion: date | None = Field(default=None, alias="datMod")
    fecha_publicacion: date | None = Field(default=None, alias="datPublicacion")


class RawCallDetail(RawModel):
    id: int | float | None = None
    organo: RawOrgan | None = None
    sede_electronica: str | None = Field(default=None, alias="sedeElectronica")
    codigo_bdns: str | None = Field(default=None, alias="codigoBDNS")
    fecha_recepcion: date | None = Field(default=None, alias="fechaRecepcion")
    instrumentos: list[RawNestedDescription] | None = None
    tipo_convocatoria: str | None = Field(default=None, alias="tipoConvocatoria")
    presupuesto_total: float | None = Field(default=None, alias="presupuestoTotal")
    mrr: bool | None = None
    descripcion: str | None = None
    descripcion_leng: str | None = Field(default=None, alias="descripcionLeng")
    tipos_beneficiarios: list[RawNestedDescription] | None = Field(default=None, alias="tiposBeneficiarios")
    sectores: list[RawNestedDescription] | None = None
    regiones: list[RawNestedDescription] | None = None
    descripcion_finalidad: str | None = Field(default=None, alias="descripcionFinalidad")
    descripcion_bases_reguladoras: str | None = Field(default=None, alias="descripcionBasesReguladoras")
    url_bases_reguladoras: str | None = Field(default=None, alias="urlBasesReguladoras")
    se_publica_diario_oficial: bool | None = Field(default=None, alias="sePublicaDiarioOficial")
    abierto: bool | None = None
    fecha_inicio_solicitud: date | None = Field(default=None, alias="fechaInicioSolicitud")
    fecha_fin_solicitud: date | None = Field(default=None, alias="fechaFinSolicitud")
    text_inicio: str | None = Field(default=None, alias="textInicio")
    text_fin: str | None = Field(default=None, alias="textFin")
    ayuda_estado: str | None = Field(default=None, alias="ayudaEstado")
    url_ayuda_estado: str | None = Field(default=None, alias="urlAyudaEstado")
    fondos: list[RawNestedDescription] | None = None
    reglamento: dict[str, Any] | None = None
    objetivos: list[RawNestedDescription] | None = None
    sectores_productos: list[RawNestedDescription] | None = Field(default=None, alias="sectoresProductos")
    documentos: list[RawDocument] | None = None
    anuncios: list[dict[str, Any]] | None = None
    advertencia: str | None = None
