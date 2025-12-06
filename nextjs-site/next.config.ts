/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [],
    unoptimized: false,
  },
  // Enable static export for Vercel
  output: 'standalone',
};

export default nextConfig;
