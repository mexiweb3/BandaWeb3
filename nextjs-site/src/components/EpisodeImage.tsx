'use client';

interface EpisodeImageProps {
    src: string;
    alt: string;
    fill?: boolean;
    width?: number;
    height?: number;
    className?: string;
}

export default function EpisodeImage({ src, alt, fill, width, height, className }: EpisodeImageProps) {
    // If fill is true, use absolute positioning to fill the container
    if (fill) {
        return (
            <img
                src={src}
                alt={alt}
                className={`absolute inset-0 w-full h-full ${className || ''}`}
                style={{ objectFit: 'cover' }}
            />
        );
    }

    // Otherwise use normal img with width/height
    return (
        <img
            src={src}
            alt={alt}
            width={width}
            height={height}
            className={className}
        />
    );
}
