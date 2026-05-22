/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  transpilePackages: ["@umrabor/ui", "@umrabor/shared"],
  experimental: {
    typedRoutes: false,
  },
};
module.exports = nextConfig;
