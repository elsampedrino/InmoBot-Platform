import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.inmobot.panel',
  appName: 'InmoBot Panel',
  webDir: 'dist',
  server: {
    // https scheme: localStorage comparte origen con la API y evita problemas de seguridad
    androidScheme: 'https',
  },
};

export default config;
