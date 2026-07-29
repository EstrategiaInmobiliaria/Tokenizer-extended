# Agartha Monetization Hub

Sitio comercial y sistema de captura de oportunidades para Agartha Bienes
Raíces.

## Fuentes de ingreso

- Captación de compradores e inversionistas para desarrollos.
- Diagnósticos y servicios de estrategia inmobiliaria.
- Venta de sistemas y prompts de inteligencia artificial.
- Conversión de enlaces guardados en investigación y contenido mediante
  `/radar`.

## Configuración segura

1. Copia `.env.example` como `.env`.
2. Sustituye los canales oficiales y enlaces públicos.
3. Crea los enlaces de checkout dentro de Stripe, Mercado Pago, Gumroad o
   Lemon Squeezy.
4. Configura la cuenta receptora directamente con el proveedor de pago.

La aplicación no solicita ni almacena números de tarjeta, cuentas bancarias,
CVV, NIP, contraseñas o códigos de verificación.

## Desarrollo

```bash
yarn
yarn dev
```

## Validación

```bash
yarn lint
yarn build
```

## Flujo comercial

1. Instagram y TikTok dirigen al sitio.
2. El visitante elige desarrollos, estrategia o productos digitales.
3. Los prospectos inmobiliarios se califican por WhatsApp o email.
4. Los productos digitales se cobran mediante checkout alojado por el
   proveedor.
5. El `/radar` guarda enlaces localmente y genera un prompt para analizarlos
   con la IA elegida.

Antes de publicar desarrollos deben agregarse inventario real, precios
vigentes, permisos de uso de imágenes, avisos de privacidad y términos
aplicables a la jurisdicción de operación.
