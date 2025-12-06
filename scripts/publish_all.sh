#!/bin/bash
# BandaWeb3 Publishing Orchestrator
# Formats and publishes content to all platforms

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Load environment variables
if [ -f "$PROJECT_DIR/config/.env" ]; then
    export $(cat "$PROJECT_DIR/config/.env" | grep -v '^#' | xargs)
fi

# Function to print colored output
print_step() {
    echo -e "${CYAN}==>${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Function to show usage
usage() {
    cat << EOF
Usage: $0 <episode_number> [options]

Formats and publishes BandaWeb3 content to all platforms.

Arguments:
    episode_number    Episode number (e.g., 075)

Options:
    --skip-format     Skip content formatting step
    --skip-linkedin   Skip LinkedIn publishing
    --skip-instagram  Skip Instagram publishing
    --dry-run         Format only, don't publish
    --schedule TIME   Schedule posts for later (format: "YYYY-MM-DD HH:MM")
    -h, --help        Show this help message

Examples:
    # Publish everything
    $0 075

    # Dry run (format only)
    $0 075 --dry-run

    # Skip Instagram
    $0 075 --skip-instagram

    # Schedule for tomorrow at 9am
    $0 075 --schedule "2024-12-06 09:00"
EOF
    exit 1
}

# Parse arguments
EPISODE_NUM=""
SKIP_FORMAT=false
SKIP_LINKEDIN=false
SKIP_INSTAGRAM=false
DRY_RUN=false
SCHEDULE_TIME=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            ;;
        --skip-format)
            SKIP_FORMAT=true
            shift
            ;;
        --skip-linkedin)
            SKIP_LINKEDIN=true
            shift
            ;;
        --skip-instagram)
            SKIP_INSTAGRAM=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --schedule)
            SCHEDULE_TIME="$2"
            shift 2
            ;;
        *)
            if [ -z "$EPISODE_NUM" ]; then
                EPISODE_NUM="$1"
            else
                print_error "Unknown option: $1"
                usage
            fi
            shift
            ;;
    esac
done

# Validate episode number
if [ -z "$EPISODE_NUM" ]; then
    print_error "Episode number required"
    usage
fi

# Find episode directory
EPISODE_DIR=$(find "$PROJECT_DIR/.." -maxdepth 1 -type d -name "E${EPISODE_NUM}_*" | head -n 1)

if [ -z "$EPISODE_DIR" ]; then
    print_error "Episode directory not found for E${EPISODE_NUM}"
    exit 1
fi

print_success "Found episode directory: $EPISODE_DIR"

# Header
echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}  BandaWeb3 Publishing Workflow - Episode ${EPISODE_NUM}           ${CYAN}║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Format content
if [ "$SKIP_FORMAT" = false ]; then
    print_step "Step 1: Formatting content for all platforms"
    
    if python3 "$SCRIPT_DIR/format_for_platforms.py" "$EPISODE_DIR" --all --clipboard; then
        print_success "Content formatted successfully"
    else
        print_error "Failed to format content"
        exit 1
    fi
    echo ""
else
    print_warning "Skipping content formatting (--skip-format)"
    echo ""
fi

# Step 2: Display formatted content summary
print_step "Step 2: Content Summary"

FORMATTED_DIR="$EPISODE_DIR/formatted"
if [ -d "$FORMATTED_DIR" ]; then
    echo ""
    echo -e "${BLUE}📱 Twitter Thread:${NC}"
    if [ -f "$FORMATTED_DIR/twitter_thread_formatted.txt" ]; then
        TWEET_COUNT=$(grep -c "^---$" "$FORMATTED_DIR/twitter_thread_formatted.txt" || echo "0")
        TWEET_COUNT=$((TWEET_COUNT + 1))
        echo "   ✓ $TWEET_COUNT tweets formatted"
        echo "   ✓ Copied to clipboard (ready to paste in Typefully/Buffer)"
    else
        echo "   ✗ Not found"
    fi
    
    echo ""
    echo -e "${BLUE}💼 LinkedIn:${NC}"
    if [ -f "$FORMATTED_DIR/linkedin_article_formatted.txt" ]; then
        CHAR_COUNT=$(wc -c < "$FORMATTED_DIR/linkedin_article_formatted.txt")
        echo "   ✓ Article formatted ($CHAR_COUNT characters)"
    fi
    if [ -f "$FORMATTED_DIR/linkedin_post_formatted.txt" ]; then
        CHAR_COUNT=$(wc -c < "$FORMATTED_DIR/linkedin_post_formatted.txt")
        echo "   ✓ Post formatted ($CHAR_COUNT characters)"
    fi
    
    echo ""
    echo -e "${BLUE}📸 Instagram:${NC}"
    if [ -f "$FORMATTED_DIR/instagram_caption_formatted.txt" ]; then
        CHAR_COUNT=$(wc -c < "$FORMATTED_DIR/instagram_caption_formatted.txt")
        echo "   ✓ Caption formatted ($CHAR_COUNT characters)"
    else
        echo "   ✗ Not found"
    fi
    echo ""
fi

# If dry run, stop here
if [ "$DRY_RUN" = true ]; then
    print_warning "Dry run mode - stopping before publishing"
    echo ""
    echo -e "${GREEN}✅ Content formatted and ready to publish!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Review formatted content in: $FORMATTED_DIR"
    echo "  2. Twitter thread is in clipboard - paste in Typefully/Buffer"
    echo "  3. Run without --dry-run to publish to LinkedIn/Instagram"
    echo ""
    exit 0
fi

# Step 3: Publish to LinkedIn
if [ "$SKIP_LINKEDIN" = false ] && [ "$ENABLE_LINKEDIN_AUTO_PUBLISH" = "true" ]; then
    print_step "Step 3: Publishing to LinkedIn"
    
    LINKEDIN_ARTICLE="$EPISODE_DIR/content/article.md"
    
    if [ -f "$LINKEDIN_ARTICLE" ]; then
        if [ -n "$SCHEDULE_TIME" ]; then
            print_warning "Scheduling LinkedIn post for $SCHEDULE_TIME"
            python3 "$SCRIPT_DIR/publish_linkedin.py" "$LINKEDIN_ARTICLE" --schedule "$SCHEDULE_TIME"
        else
            if python3 "$SCRIPT_DIR/publish_linkedin.py" "$LINKEDIN_ARTICLE"; then
                print_success "Published to LinkedIn"
            else
                print_error "Failed to publish to LinkedIn"
            fi
        fi
    else
        print_warning "LinkedIn article not found, skipping"
    fi
    echo ""
else
    print_warning "Skipping LinkedIn (disabled or --skip-linkedin)"
    echo ""
fi

# Step 4: Publish to Instagram
if [ "$SKIP_INSTAGRAM" = false ] && [ "$ENABLE_INSTAGRAM_AUTO_PUBLISH" = "true" ]; then
    print_step "Step 4: Publishing to Instagram"
    
    print_warning "Instagram publishing requires manual image URLs"
    print_warning "Please run: python3 $SCRIPT_DIR/publish_instagram.py $EPISODE_DIR --type carousel"
    echo ""
else
    print_warning "Skipping Instagram (disabled or --skip-instagram)"
    echo ""
fi

# Step 5: Summary
echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}  Publishing Summary                                        ${CYAN}║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${GREEN}✅ Content formatted and ready!${NC}"
echo ""
echo "📱 Twitter/X:"
echo "   → Thread copied to clipboard"
echo "   → Paste in Typefully or Buffer to schedule"
echo ""

if [ "$SKIP_LINKEDIN" = false ]; then
    echo "💼 LinkedIn:"
    if [ -n "$SCHEDULE_TIME" ]; then
        echo "   → Scheduled for $SCHEDULE_TIME"
    else
        echo "   → Published (check your LinkedIn profile)"
    fi
    echo ""
fi

if [ "$SKIP_INSTAGRAM" = false ]; then
    echo "📸 Instagram:"
    echo "   → Run publish_instagram.py manually with image URLs"
    echo ""
fi

echo "📊 Next steps:"
echo "   1. Publish Twitter thread from Typefully/Buffer"
echo "   2. Monitor engagement on all platforms"
echo "   3. Run collect_analytics.py after 7 days"
echo ""

print_success "Publishing workflow complete!"
echo ""
