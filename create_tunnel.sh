#!/bin/bash
echo "🌐 Creating public URL for your Podcast Manager..."
echo ""
echo "Opening tunnel to localhost:3000..."
echo "This will give you a public URL you can access from any browser"
echo ""
echo "⚠️  Press Ctrl+C to stop the tunnel"
echo ""
ssh -R 80:localhost:3000 localhost.run
