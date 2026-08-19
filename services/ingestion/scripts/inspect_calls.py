#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from opportunity_ingestion.bdns import BdnsClient  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect a small page of real BDNS calls.")
    parser.add_argument("--limit", type=int, default=5, choices=range(1, 11), help="Number of calls to display (1-10).")
    args = parser.parse_args()

    with BdnsClient() as client:
        page = client.latest_calls(page_size=args.limit)

    print(f"Convocatorias recibidas: {len(page.content)} (total reportado: {page.total_elements})")
    for index, call in enumerate(page.content, start=1):
        print(f"\n{index}. BDNS: {call.numero_convocatoria}")
        print(f"   Título: {call.descripcion or '[ausente]'}")
        print(f"   Organismo: {call.nivel3 or call.nivel2 or call.nivel1 or '[ausente]'}")
        print(f"   Fecha de recepción: {call.fecha_recepcion or '[ausente]'}")
        print(f"   MRR: {call.mrr if call.mrr is not None else '[ausente]'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

