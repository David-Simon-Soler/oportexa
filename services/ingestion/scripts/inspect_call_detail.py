#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from opportunity_ingestion.bdns import BdnsClient  # noqa: E402


def show(value: object) -> object:
    if value is None:
        return "[ausente]"
    if isinstance(value, list) and not value:
        return "[vacío]"
    return value


def descriptions(items: list | None) -> object:
    if items is None:
        return "[ausente]"
    if not items:
        return "[vacío]"
    return [item.descripcion for item in items]


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect one real BDNS call detail.")
    parser.add_argument("bdns_code", help="Código BDNS, por ejemplo 925673.")
    args = parser.parse_args()

    with BdnsClient() as client:
        call = client.get_call_detail(args.bdns_code)

    print(f"BDNS: {show(call.codigo_bdns)}")
    print(f"Organismo: {show(call.organo)}")
    print(f"Título: {show(call.descripcion)}")
    print(f"Descripción cooficial: {show(call.descripcion_leng)}")
    print(f"Presupuesto: {show(call.presupuesto_total)}")
    print(f"Beneficiarios: {descriptions(call.tipos_beneficiarios)}")
    print(f"Sectores: {descriptions(call.sectores)}")
    print(f"Regiones: {descriptions(call.regiones)}")
    print(f"Fecha inicio: {show(call.fecha_inicio_solicitud)}")
    print(f"Fecha fin: {show(call.fecha_fin_solicitud)}")
    print(f"Bases reguladoras: {show(call.descripcion_bases_reguladoras)}")
    print(f"URL bases reguladoras: {show(call.url_bases_reguladoras)}")
    print(f"Fondos: {descriptions(call.fondos)}")
    if call.documentos is None:
        documents = "[ausente]"
    elif not call.documentos:
        documents = "[vacío]"
    else:
        documents = [doc.nombre_fic or doc.descripcion for doc in call.documentos]
    print(f"Documentos: {documents}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
