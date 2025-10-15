import { defineConfig } from "drizzle-kit";

if (!process.env.DATABASE_URL) {
  throw new Error("DATABASE_URL, ensure the database is provisioned");
}

// Determine dialect based on DATABASE_URL
const isPostgres = process.env.DATABASE_URL.includes('postgresql://');
const isSQLite = process.env.DATABASE_URL.includes('sqlite:');

export default defineConfig({
  out: "./migrations",
  schema: "./shared/schema.ts", // Updated to correct path
  dialect: isPostgres ? "postgresql" : isSQLite ? "sqlite" : "postgresql",
  dbCredentials: {
    url: process.env.DATABASE_URL,
  },
});
