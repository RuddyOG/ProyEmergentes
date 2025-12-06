// Conexión a MongoDB y creación de colecciones base para GAMC

use('gamc_datos');

// Crear colecciones
db.createCollection('sonido');
db.createCollection('aire');
db.createCollection('soterrado');

// Crear índices
db.sonido.createIndex({ time: 1 });
db.aire.createIndex({ time: 1 });
db.soterrado.createIndex({ time: 1 });

print("Base de datos 'gamc_datos' y colecciones creadas correctamente.");
