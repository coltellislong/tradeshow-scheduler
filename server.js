require('dotenv').config();
const express = require('express');
const cors = require('cors');
const path = require('path');
const { MongoClient, ObjectId } = require('mongodb');

const app = express();
const PORT = process.env.PORT || 3000;

// ─── Middleware ───────────────────────────────────────────
app.use(cors());
app.use(express.json());

// ─── Serve frontend from /public ─────────────────────────
app.use(express.static(path.join(__dirname, 'public')));

// ─── MongoDB Connection ──────────────────────────────────
const MONGO_URI = process.env.MONGO_URI;
const DB_NAME = process.env.DB_NAME || 'tradeshow_db';

if (!MONGO_URI) {
  console.error('ERROR: MONGO_URI environment variable is not set.');
  console.error('Set it to your MongoDB Atlas connection string, e.g.:');
  console.error('  mongodb+srv://<user>:<pass>@cluster0.xxxxx.mongodb.net/tradeshow_db');
  process.exit(1);
}

let db;

async function connectDB() {
  const client = new MongoClient(MONGO_URI);
  await client.connect();
  db = client.db(DB_NAME);
  console.log(`Connected to MongoDB: ${DB_NAME}`);
}

// Helper to get collections
function shows() { return db.collection('shows'); }
function feed() { return db.collection('feed'); }

// ─── SHOWS ROUTES ────────────────────────────────────────

// GET /api/shows — fetch all shows
app.get('/api/shows', async (req, res) => {
  try {
    const all = await shows().find().toArray();
    res.json(all);
  } catch (err) {
    console.error('GET /api/shows error:', err);
    res.status(500).json({ error: 'Failed to fetch shows' });
  }
});

// POST /api/shows — create a new show
app.post('/api/shows', async (req, res) => {
  try {
    const show = req.body;
    if (!show.name || !show.startDate) {
      return res.status(400).json({ error: 'name and startDate are required' });
    }
    const result = await shows().insertOne(show);
    res.status(201).json({ ...show, _id: result.insertedId });
  } catch (err) {
    console.error('POST /api/shows error:', err);
    res.status(500).json({ error: 'Failed to create show' });
  }
});

// PUT /api/shows/:id — update a show by its custom id field
app.put('/api/shows/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const updates = req.body;
    delete updates._id; // prevent overwriting _id
    const result = await shows().findOneAndUpdate(
      { id },
      { $set: updates },
      { returnDocument: 'after' }
    );
    if (!result) {
      return res.status(404).json({ error: 'Show not found' });
    }
    res.json(result);
  } catch (err) {
    console.error('PUT /api/shows/:id error:', err);
    res.status(500).json({ error: 'Failed to update show' });
  }
});

// DELETE /api/shows/:id — delete a show by its custom id field
app.delete('/api/shows/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const result = await shows().deleteOne({ id });
    if (result.deletedCount === 0) {
      return res.status(404).json({ error: 'Show not found' });
    }
    res.json({ success: true });
  } catch (err) {
    console.error('DELETE /api/shows/:id error:', err);
    res.status(500).json({ error: 'Failed to delete show' });
  }
});

// POST /api/shows/bulk — import multiple shows at once
app.post('/api/shows/bulk', async (req, res) => {
  try {
    const items = req.body;
    if (!Array.isArray(items) || items.length === 0) {
      return res.status(400).json({ error: 'Expected a non-empty array of shows' });
    }
    const result = await shows().insertMany(items);
    res.status(201).json({ insertedCount: result.insertedCount });
  } catch (err) {
    console.error('POST /api/shows/bulk error:', err);
    res.status(500).json({ error: 'Failed to bulk import shows' });
  }
});

// ─── FEED ROUTES ─────────────────────────────────────────

// GET /api/feed — fetch recent feed events (last 50)
app.get('/api/feed', async (req, res) => {
  try {
    const events = await feed().find().sort({ ts: -1 }).limit(50).toArray();
    res.json(events.reverse());
  } catch (err) {
    console.error('GET /api/feed error:', err);
    res.status(500).json({ error: 'Failed to fetch feed' });
  }
});

// POST /api/feed — add a feed event
app.post('/api/feed', async (req, res) => {
  try {
    const event = req.body;
    const result = await feed().insertOne(event);
    res.status(201).json({ ...event, _id: result.insertedId });
  } catch (err) {
    console.error('POST /api/feed error:', err);
    res.status(500).json({ error: 'Failed to add feed event' });
  }
});

// ─── HEALTH CHECK ────────────────────────────────────────
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', db: db ? 'connected' : 'disconnected' });
});

// ─── Catch-all: serve index.html for any non-API route ──
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// ─── START ───────────────────────────────────────────────
connectDB().then(() => {
  app.listen(PORT, () => {
    console.log(`API running on http://localhost:${PORT}`);
  });
}).catch(err => {
  console.error('Failed to connect to MongoDB:', err);
  process.exit(1);
});
