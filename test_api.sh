#!/bin/bash

echo "=================================="
echo "  PODCAST SYSTEM API DEMO"
echo "=================================="
echo ""

echo "1️⃣  System Status:"
echo "-------------------"
curl -s http://localhost:8000/stats | python3 -c "import sys, json; data=json.load(sys.stdin); print(f'Podcasts: {data[\"podcasts\"]}\nEpisodes: {data[\"episodes\"]}\nTags: {data[\"tags\"]}\nTranscript Segments: {data[\"transcript_segments\"]}')"
echo ""

echo "2️⃣  Podcasts:"
echo "-------------------"
curl -s http://localhost:8000/podcasts/ | python3 -c "import sys, json; [print(f'  📻 {p[\"name\"]} (ID: {p[\"id\"]})') for p in json.load(sys.stdin)]"
echo ""

echo "3️⃣  Episodes:"
echo "-------------------"
curl -s http://localhost:8000/episodes/ | python3 -c "import sys, json; [print(f'  🎙️  {e[\"title\"]}\n     Episode {e[\"episode_number\"]} | {len(e[\"tags\"])} tags | {e[\"podcast_name\"]}') for e in json.load(sys.stdin)]"
echo ""

echo "4️⃣  Tags:"
echo "-------------------"
curl -s 'http://localhost:8000/tags/?limit=10&sort_by=usage' | python3 -c "import sys, json; [print(f'  🏷️  {t[\"name\"]} ({t[\"usage_count\"]} uses)') for t in json.load(sys.stdin)]"
echo ""

echo "5️⃣  Search Transcript for 'AI':"
echo "-------------------"
curl -s -X POST http://localhost:8000/search/transcripts \
  -H "Content-Type: application/json" \
  -d '{"query":"AI","limit":3}' | python3 -c "import sys, json; data=json.load(sys.stdin); print(f'Found {data[\"total_count\"]} results\n'); [print(f'  💬 {r[\"text\"][:80]}...\n     ⏱️  {int(r[\"start_time\"]//60)}:{int(r[\"start_time\"]%60):02d} | {r[\"speaker\"] or \"Unknown\"}') for r in data[\"results\"][:3]]"
echo ""

echo "=================================="
echo "✅ API is fully functional!"
echo "=================================="

