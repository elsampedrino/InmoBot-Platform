const { Client } = require('pg');

// Configuración de conexión PostgreSQL
// Ajustar estos valores según tu configuración
const client = new Client({
  host: 'oregon-postgres.render.com',
  port: 5432,
  database: 'inmobot_db_w0g1',
  user: 'inmobot_db_w0g1_user',
  password: process.env.PGPASSWORD || '',
  ssl: {
    rejectUnauthorized: false
  }
});

async function migrate() {
  try {
    console.log('Conectando a PostgreSQL...');
    await client.connect();
    console.log('✓ Conectado a PostgreSQL\n');

    // 1. Agregar columna repo a chat_logs
    console.log('Ejecutando: ALTER TABLE chat_logs ADD COLUMN repo...');
    await client.query(`
      ALTER TABLE chat_logs
      ADD COLUMN IF NOT EXISTS repo VARCHAR(50) DEFAULT 'demo'
    `);
    console.log('✓ Columna repo agregada a chat_logs\n');

    // 2. Agregar columna repo a conversion_logs
    console.log('Ejecutando: ALTER TABLE conversion_logs ADD COLUMN repo...');
    await client.query(`
      ALTER TABLE conversion_logs
      ADD COLUMN IF NOT EXISTS repo VARCHAR(50) DEFAULT 'demo'
    `);
    console.log('✓ Columna repo agregada a conversion_logs\n');

    // 3. Crear índice en chat_logs
    console.log('Ejecutando: CREATE INDEX idx_chat_logs_repo...');
    await client.query(`
      CREATE INDEX IF NOT EXISTS idx_chat_logs_repo ON chat_logs(repo)
    `);
    console.log('✓ Índice idx_chat_logs_repo creado\n');

    // 4. Crear índice en conversion_logs
    console.log('Ejecutando: CREATE INDEX idx_conversion_logs_repo...');
    await client.query(`
      CREATE INDEX IF NOT EXISTS idx_conversion_logs_repo ON conversion_logs(repo)
    `);
    console.log('✓ Índice idx_conversion_logs_repo creado\n');

    // 5. Agregar comentarios
    console.log('Agregando comentarios...');
    await client.query(`
      COMMENT ON COLUMN chat_logs.repo IS 'Identificador del catálogo/cliente: demo, bbr, etc'
    `);
    await client.query(`
      COMMENT ON COLUMN conversion_logs.repo IS 'Identificador del catálogo/cliente: demo, bbr, etc'
    `);
    console.log('✓ Comentarios agregados\n');

    // 6. Verificar
    console.log('Verificando columnas creadas...');
    const result = await client.query(`
      SELECT table_name, column_name, data_type, column_default
      FROM information_schema.columns
      WHERE table_name IN ('chat_logs', 'conversion_logs')
        AND column_name = 'repo'
      ORDER BY table_name
    `);

    console.log('\n📊 Verificación exitosa:');
    result.rows.forEach(row => {
      console.log(`  ✓ ${row.table_name}.${row.column_name}: ${row.data_type} (default: ${row.column_default})`);
    });

    console.log('\n🎉 Migración completada exitosamente!');

  } catch (error) {
    console.error('\n❌ Error durante la migración:');
    console.error(error.message);
    console.error('\nStack trace:');
    console.error(error.stack);
    process.exit(1);
  } finally {
    await client.end();
    console.log('\n✓ Conexión cerrada');
  }
}

// Ejecutar migración
migrate();
