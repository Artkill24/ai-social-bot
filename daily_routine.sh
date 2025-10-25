#!/bin/bash
# Routine completa per massima crescita

echo "🚀 Starting daily growth routine..."

# Morning boost (8-9 AM)
echo "☀️ Morning session..."
python engage.py --max-posts 30
python auto_reply.py --max-replies 20
sleep 10

# Afternoon boost (2-3 PM)
echo "🌤️ Afternoon session..."
python src/main_viral.py
sleep 5
python engage.py --max-posts 20
python auto_reply.py --max-replies 15

# Evening boost (8-9 PM)
echo "🌙 Evening session..."
python engage.py --max-posts 25
python auto_reply.py --max-replies 20

# Report
echo ""
echo "✅ Daily routine complete!"
python monetize.py

echo ""
echo "📊 Next run: Tomorrow same time"
