import "server-only";
import { Pool } from "pg";

let pool: Pool | undefined;

export function getPool(): Pool {
  if (!process.env.DATABASE_URL) throw new Error("DATABASE_URL no está configurada en el servidor.");
  pool ??= new Pool({ connectionString: process.env.DATABASE_URL, max: 5, application_name: "opportunity-intel-web" });
  return pool;
}
