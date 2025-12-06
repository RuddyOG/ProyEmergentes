use('gamc_datos');

// Sonido
db.sonido.insertOne({
  devAddr: "A84041F4",
  deduplicationId: "f68f1c9a-12cd-4e34-9aaf",
  time: ISODate("2025-11-03T15:30:00Z"),
  deviceInfo: {
    tenantName: "GAMC",
    deviceName: "SensorSonido1",
    devEui: "A84041F4B1C2D3E4",
    deviceProfileName: "WS302",
    tag: {
      description: "Sensor de sonido ambiental",
      address: "Av. Heroinas y San Martín",
      location: { lat: -17.3935, lng: -66.1570 }
    }
  },
  txInfo: { frequency: 915, dr: 5, adr: true },
  object: { laeq: 58.2, lai: 55.9, laiMax: 80.4, battery: 92, status: "OK" }
});

// Aire
db.aire.insertOne({
  devAddr: "A84041F5",
  time: ISODate("2025-11-03T15:30:00Z"),
  deviceInfo: {
    tenantName: "GAMC",
    deviceName: "SensorAire1",
    deviceProfileName: "EM500-CO2"
  },
  object: { co2: 427, temperature: 23.4, humidity: 51.8, battery: 88, status: "OK" }
});

// Soterrado
db.soterrado.insertOne({
  devAddr: "A84041F6",
  time: ISODate("2025-11-03T15:30:00Z"),
  deviceInfo: {
    tenantName: "GAMC",
    deviceName: "SensorSoterrado1",
    deviceProfileName: "EM310-UDL"
  },
  object: { distance: 1.8, position: "normal", battery: 95, status: "OK" }
});
