# BandaWeb3 - Next.js Site

Sitio web dinámico de BandaWeb3 construido con Next.js 14, TypeScript y Tailwind CSS.

## Características

- ✅ **ISR (Incremental Static Regeneration)**: Páginas se regeneran automáticamente cada 60 segundos
- ✅ **TypeScript**: Type safety completo
- ✅ **Optimización de imágenes**: Next.js Image optimization
- ✅ **SEO-friendly**: Server-side rendering
- ✅ **Responsive**: Mobile-first design con Tailwind CSS

## Requisitos

- Node.js >= 20.9.0
- npm o yarn

## Instalación

```bash
npm install
```

## Desarrollo Local

```bash
npm run dev
```

Abre [http://localhost:3000](http://localhost:3000) en tu navegador.

## Build de Producción

```bash
npm run build
npm start
```

## Deployment en Vercel

1. Conecta tu repositorio de GitHub a Vercel
2. Configura el proyecto:
   - **Root Directory**: `nextjs-site/`
   - **Framework**: Next.js (auto-detectado)
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next` (auto)

3. Deploy automático con cada push a `master`

## Estructura del Proyecto

```
nextjs-site/
├── src/
│   ├── app/                 # App Router (Next.js 13+)
│   │   ├── layout.tsx      # Root layout
│   │   ├── page.tsx        # Home page
│   │   └── episodes/
│   │       └── [id]/
│   │           └── page.tsx # Dynamic episode pages
│   └── lib/
│       ├── episodes.ts     # Data fetching logic
│       └── episodes_database.json
├── public/
│   ├── flyers/            # Episode flyers
│   └── audio/             # Audio files
└── next.config.ts         # Next.js configuration
```

## Actualizar Episodios

1. Edita `../data/episodes_database.json`
2. Copia el archivo actualizado: `cp ../data/episodes_database.json src/lib/`
3. Las páginas se regenerarán automáticamente en 60 segundos (ISR)
4. O fuerza regeneración con deploy a Vercel

## Notas

- **Node.js 18**: El desarrollo local requiere Node 20+, pero Vercel usa Node 20 automáticamente
- **ISR**: Configurado con `revalidate: 60` (60 segundos)
- **Imágenes**: Todas las imágenes deben estar en `public/flyers/`
