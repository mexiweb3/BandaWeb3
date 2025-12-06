import { getAllEpisodes } from '@/lib/episodes';
import Link from 'next/link';
import Image from 'next/image';

export const revalidate = 60; // ISR: Revalidate every 60 seconds

export default function Home() {
  const episodes = getAllEpisodes();
  const hostedEpisodes = episodes.filter(
    ep => ep.status === 'archived' || ep.status === 'published'
  );

  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-900 to-black text-white">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-6xl font-bold mb-4 bg-gradient-to-r from-purple-400 to-pink-600 bg-clip-text text-transparent">
            BandaWeb3
          </h1>
          <p className="text-xl text-gray-300">
            Conversaciones sobre Web3, Blockchain y el futuro descentralizado
          </p>
        </div>

        {/* Episodes Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {hostedEpisodes.map((episode) => (
            <Link
              key={episode.number}
              href={`/episodes/${episode.number}`}
              className="group block"
            >
              <div className="bg-gray-800 rounded-lg overflow-hidden hover:ring-2 hover:ring-purple-500 transition-all duration-300 hover:scale-105">
                {/* Flyer Image */}
                {episode.flyer_urls && episode.flyer_urls.length > 0 && (
                  <div className="relative h-64 w-full">
                    <Image
                      src={episode.flyer_urls[0].replace('../static/images/', '/flyers/')}
                      alt={`Episode ${episode.number}`}
                      fill
                      className="object-cover"
                    />
                    <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-all duration-300 flex items-center justify-center">
                      <svg className="w-16 h-16 text-white opacity-0 group-hover:opacity-100 transition-opacity" fill="currentColor" viewBox="0 0 24 24">
                        <polygon points="5 3 19 12 5 21 5 3"></polygon>
                      </svg>
                    </div>
                  </div>
                )}

                {/* Episode Info */}
                <div className="p-6">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-purple-400 font-bold">#{episode.number}</span>
                    <span className="text-gray-400 text-sm">{episode.date}</span>
                  </div>
                  <h2 className="text-xl font-semibold mb-2 line-clamp-2">
                    {episode.title}
                  </h2>
                  {episode.description && (
                    <p className="text-gray-400 text-sm line-clamp-3 mb-4">
                      {episode.description}
                    </p>
                  )}
                  {episode.topics && episode.topics.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {episode.topics.slice(0, 3).map((topic, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-1 bg-purple-900 bg-opacity-50 rounded text-xs"
                        >
                          {topic}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </main>
  );
}
