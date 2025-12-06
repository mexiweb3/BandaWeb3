import episodesData from './episodes_database.json';

// TypeScript interfaces
export interface Episode {
    number: string;
    title: string;
    date: string;
    time?: string;
    duration?: string;
    guests?: string[];
    guest_links?: Record<string, string>;
    space_url?: string;
    audio_url?: string;
    unlock_url?: string;
    opensea_url?: string;
    contract_url?: string;
    description?: string;
    topics?: string[];
    status?: string;
    transcript_available?: boolean;
    content_generated?: boolean;
    flyer_urls?: string[];
    listeners?: string;
}

export interface EpisodesDatabase {
    metadata: {
        total_episodes: number;
        last_updated: string;
    };
    episodes: Episode[];
}

// Cast the imported JSON to our type
const database = episodesData as EpisodesDatabase;

/**
 * Get all episodes
 */
export function getAllEpisodes(): Episode[] {
    return database.episodes;
}

/**
 * Get episode by number
 */
export function getEpisodeById(id: string): Episode | undefined {
    return database.episodes.find(ep => ep.number === id);
}

/**
 * Get hosted episodes (status: archived or published)
 */
export function getHostedEpisodes(): Episode[] {
    return database.episodes.filter(
        ep => ep.status === 'archived' || ep.status === 'published'
    );
}

/**
 * Get co-hosted episodes
 */
export function getCohostedEpisodes(): Episode[] {
    return database.episodes.filter(
        ep => ep.status === 'co-hosted'
    );
}

/**
 * Get scheduled episodes
 */
export function getScheduledEpisodes(): Episode[] {
    return database.episodes.filter(
        ep => ep.status === 'scheduled'
    );
}

/**
 * Get episode count
 */
export function getEpisodeCount(): number {
    return database.metadata.total_episodes;
}
