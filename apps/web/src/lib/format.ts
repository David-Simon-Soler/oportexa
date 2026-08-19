export function formatMoney(value: string | number | null): string {
  if (value === null || value === undefined || value === "") return "Importe no especificado";
  const amount = Number(value);
  if (!Number.isFinite(amount)) return "Importe no especificado";
  return new Intl.NumberFormat("es-ES", { style: "currency", currency: "EUR" }).format(amount);
}

export function formatDate(value: string | null): string {
  if (!value) return "Fecha no especificada";
  const date = new Date(`${value}T00:00:00`);
  return Number.isNaN(date.getTime()) ? "Fecha no especificada" : new Intl.DateTimeFormat("es-ES", { dateStyle: "medium" }).format(date);
}

export function statusLabel(isOpen: boolean | null, endDate: string | null): string {
  if (isOpen) return endDate ? "Abierta" : "Convocatoria indicada como abierta; la fuente no especifica fecha de cierre.";
  return "Cerrada o sin estado confirmado";
}
