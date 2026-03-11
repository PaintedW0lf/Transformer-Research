#!/bin/bash
# Download script for spiritual/philosophical texts
# Run from ~/LLMTraining directory

mkdir -p data/western data/eastern

echo "=== Downloading Western Texts ==="

# King James Bible (public domain)
if [ ! -f "data/western/kjv_bible.txt" ]; then
    echo "Downloading KJV Bible..."
    curl -sL "https://www.gutenberg.org/cache/epub/10/pg10.txt" -o data/western/kjv_bible.txt || echo "Failed to download Bible"
fi

# Plato's Republic (public domain)
if [ ! -f "data/western/plato_republic.txt" ]; then
    echo "Downloading Plato's Republic..."
    curl -sL "https://www.gutenberg.org/cache/epub/1727/pg1727.txt" -o data/western/plato_republic.txt || echo "Failed to download Plato"
fi

# Aristotle's Politics (public domain)
if [ ! -f "data/western/aristotle_politics.txt" ]; then
    echo "Downloading Aristotle's Politics..."
    curl -sL "https://www.gutenberg.org/cache/epub/66627/pg66627.txt" -o data/western/aristotle_politics.txt || echo "Failed to download Aristotle"
fi

echo ""
echo "=== Downloading Eastern Texts ==="

# Bhagavad Gita (public domain)
if [ ! -f "data/eastern/bhagavad_gita.txt" ]; then
    echo "Downloading Bhagavad Gita..."
    curl -sL "https://www.gutenberg.org/cache/epub/41750/pg41750.txt" -o data/eastern/bhagavad_gita.txt || echo "Failed to download Gita"
fi

# Tao Te Ching (public domain)
if [ ! -f "data/eastern/tao_te_ching.txt" ]; then
    echo "Downloading Tao Te Ching..."
    curl -sL "https://www.gutenberg.org/cache/epub/112/pg112.txt" -o data/eastern/tao_te_ching.txt || echo "Failed to download Tao Te Ching"
fi

# Upanishads (public domain)
if [ ! -f "data/eastern/upanishads.txt" ]; then
    echo "Downloading Upanishads..."
    curl -sL "https://www.gutenberg.org/cache/epub/45504/pg45504.txt" -o data/eastern/upanishads.txt || echo "Failed to download Upanishads"
fi

echo ""
echo "=== Download Complete ==="
echo "Western texts: $(ls data/western/*.txt 2>/dev/null | wc -l) files"
echo "Eastern texts: $(ls data/eastern/*.txt 2>/dev/null | wc -l) files"
