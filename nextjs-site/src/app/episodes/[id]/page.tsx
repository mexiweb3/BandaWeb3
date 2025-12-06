import { getAllEpisodes, getEpisodeById } from '@/lib/episodes';
import { notFound } from 'next/navigation';
import Link from 'next/link';

export const revalidate = 60; // ISR: Revalidate every 60 seconds

// Generate static params for all episodes
export async function generateStaticParams() {
    const episodes = getAllEpisodes();
    return episodes.map((episode) => ({
        id: episode.number,
    }));
}

export default function EpisodePage({ params }: { params: { id: string } }) {
    const episode = getEpisodeById(params.id);

    if (!episode) {
        notFound();
    }

    return (
        <main className="min-h-screen bg-gradient-to-b from-gray-900 to-black text-white">
            <div className="container mx-auto px-4 py-8 max-w-4xl">
                {/* Back Button */}
                <Link
                    href="/"
                    className="inline-flex items-center text-purple-400 hover:text-purple-300 mb-8"
                >
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                    </svg>
                    Volver a todos los episodios
                </Link>

                {/* Episode Header */}
                <div className="mb-8">
                    <div className="text-purple-400 text-lg font-bold mb-2">
                        Episodio #{episode.number}
                    </div>
                    <h1 className="text-4xl font-bold mb-4">{episode.title}</h1>
                    <div className="flex flex-wrap gap-4 text-gray-400">
                        <span>📅 {episode.date}</span>
                        {episode.duration && <span>⏱️ {episode.duration}</span>}
                        {episode.listeners && <span>👥 {episode.listeners} oyentes</span>}
                    </div>
                </div>

                {/* Flyer */}
                {episode.flyer_urls && episode.flyer_urls.length > 0 && (
                    <div className="mb-8 rounded-lg overflow-hidden">
                        <img
                            src={episode.flyer_urls[0]}
                            alt={`Episode ${episode.number} Flyer`}
                            className="w-full h-auto"
                        />
                    </div>
                )}

                {/* Listen Button or Audio Player */}
                <div className="mb-8 bg-gray-800 rounded-lg p-6">
                    <h2 className="text-2xl font-bold mb-4">Escuchar episodio</h2>
                    {episode.audio_url ? (
                        <audio controls className="w-full">
                            <source src={`/audio/${episode.audio_url}`} type="audio/mpeg" />
                            Tu navegador no soporta el elemento de audio.
                        </audio>
                    ) : episode.space_url ? (
                        <a
                            href={episode.space_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="block"
                        >
                            <img
                                src="/flyers/listen_button.png"
                                alt="Escuchar en X Space"
                                className="hover:scale-105 transition-transform"
                                style={{ maxWidth: '300px' }}
                            />
                        </a>
                    ) : (
                        <p className="text-gray-400">Audio próximamente disponible</p>
                    )}
                </div>

                {/* Description */}
                {episode.description && (
                    <div className="mb-8">
                        <h2 className="text-2xl font-bold mb-4">Sobre este episodio</h2>
                        <p className="text-gray-300 leading-relaxed">{episode.description}</p>
                    </div>
                )}

                {/* Guests */}
                {episode.guests && episode.guests.length > 0 && (
                    <div className="mb-8">
                        <h2 className="text-2xl font-bold mb-4">Invitados</h2>
                        <ul className="space-y-2">
                            {episode.guests.map((guest, idx) => (
                                <li key={idx} className="flex items-center">
                                    {episode.guest_links && episode.guest_links[guest] ? (
                                        <a
                                            href={episode.guest_links[guest]}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="text-purple-400 hover:text-purple-300"
                                        >
                                            @{guest}
                                        </a>
                                    ) : (
                                        <span className="text-gray-300">{guest}</span>
                                    )}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}

                {/* Topics */}
                {episode.topics && episode.topics.length > 0 && (
                    <div className="mb-8">
                        <h2 className="text-2xl font-bold mb-4">Temas</h2>
                        <div className="flex flex-wrap gap-2">
                            {episode.topics.map((topic, idx) => (
                                <span
                                    key={idx}
                                    className="px-4 py-2 bg-purple-900 bg-opacity-50 rounded-full"
                                >
                                    {topic}
                                </span>
                            ))}
                        </div>
                    </div>
                )}

                {/* External Links */}
                {episode.space_url && (
                    <div className="mb-8">
                        <h2 className="text-2xl font-bold mb-4">Enlaces</h2>
                        <a
                            href={episode.space_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center px-6 py-3 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors"
                        >
                            <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                                <path d="M23 3a10.9 10.9 0 01-3.14 1.53 4.48 4.48 0 00-7.86 3v1A10.66 10.66 0 013 4s-4 9 5 13a11.64 11.64 0 01-7 2c9 5 20 0 20-11.5a4.5 4.5 0 00-.08-.83A7.72 7.72 0 0023 3z"></path>
                            </svg>
                            Space Original
                        </a>
                    </div>
                )}
            </div>
        </main>
    );
}
