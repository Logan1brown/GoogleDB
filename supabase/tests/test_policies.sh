#!/bin/bash

# Load environment variables
source .env

echo "Testing Supabase Policies..."

# Test 1: Public Read Access (should work without auth)
echo "\n1. Testing public read access..."
curl -s "$SUPABASE_URL/rest/v1/shows?select=*&limit=1" \
  -H "apikey: $SUPABASE_ANON_KEY" \
  -H "Content-Type: application/json"

# Test 2: Anonymous Insert (should fail)
echo "\n\n2. Testing anonymous insert (should fail)..."
curl -s -X POST "$SUPABASE_URL/rest/v1/shows" \
  -H "apikey: $SUPABASE_ANON_KEY" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Show", "search_name": "test show"}'

# Test 3: Authenticated Insert (should work)
echo "\n\n3. Testing authenticated insert..."
curl -s -X POST "$SUPABASE_URL/rest/v1/shows" \
  -H "apikey: $SUPABASE_ANON_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Show", "search_name": "test show"}'

# Test 4: Service Role Delete (should work)
echo "\n\n4. Testing service role delete..."
curl -s -X DELETE "$SUPABASE_URL/rest/v1/shows?search_name=eq.test%20show" \
  -H "apikey: $SUPABASE_SERVICE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_KEY"

echo "\n\nTests completed!"
