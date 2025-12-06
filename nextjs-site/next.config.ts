/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [],
    unoptimized: true, // Allow local images without optimization
  },
  // Enable static export for Vercel
  output: 'standalone',
};

export default nextConfig;
