import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "Oportexa",
    short_name: "Oportexa",
    description: "Descubre, entiende y verifica ayudas y subvenciones públicas.",
    start_url: "/",
    display: "standalone",
    background_color: "#F6F6F3",
    theme_color: "#F6F6F3",
    icons: [
      { src: "/icons/icon-192.png", sizes: "192x192", type: "image/png", purpose: "any" },
      { src: "/icons/icon-512.png", sizes: "512x512", type: "image/png", purpose: "any" },
    ],
  };
}
