"""
Script de utilidad para crear usuarios del panel admin.

Uso:
    python scripts/crear_admin.py

Variables de entorno necesarias: DATABASE_URL (del .env)
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

import bcrypt as _bcrypt
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

engine = create_async_engine(os.environ["DATABASE_URL"])
Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def main():
    print("=== Crear usuario admin ===\n")

    async with Session() as db:
        # Listar empresas disponibles
        result = await db.execute(text("SELECT id_empresa, nombre, slug FROM empresas WHERE activa = true ORDER BY id_empresa"))
        empresas = result.fetchall()
        if not empresas:
            print("ERROR: No hay empresas activas en la base de datos.")
            return

        print("Empresas disponibles:")
        for e in empresas:
            print(f"  [{e[0]}] {e[1]}  (slug: {e[2]})")

        id_empresa = int(input("\nID de empresa: ").strip())
        nombre = input("Nombre del usuario: ").strip()
        email = input("Email: ").strip()
        password = input("Contraseña: ").strip()
        es_superadmin = input("¿Es superadmin? (s/n): ").strip().lower() == "s"

        password_hash = _bcrypt.hashpw(password.encode(), _bcrypt.gensalt()).decode()

        await db.execute(text("""
            INSERT INTO usuarios_admin (id_empresa, email, password_hash, nombre, activo, es_superadmin)
            VALUES (:id_empresa, :email, :password_hash, :nombre, true, :es_superadmin)
            ON CONFLICT (email) DO UPDATE
            SET password_hash = :password_hash, nombre = :nombre, activo = true
        """), {
            "id_empresa": id_empresa,
            "email": email,
            "password_hash": password_hash,
            "nombre": nombre,
            "es_superadmin": es_superadmin,
        })
        await db.commit()
        print(f"\n✓ Usuario '{email}' creado/actualizado correctamente.")


if __name__ == "__main__":
    asyncio.run(main())