// Render a story whose audio + timeline were produced by scripts/tts.py
// Usage: node scripts/render.mjs stories/demo.json
import { bundle } from '@remotion/bundler';
import { renderMedia, selectComposition } from '@remotion/renderer';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const story = JSON.parse(fs.readFileSync(process.argv[2] ?? 'stories/demo.json', 'utf8'));
const timeline = JSON.parse(fs.readFileSync(path.join(root, 'public/build', story.id, 'timeline.json'), 'utf8'));
const outFile = path.join(root, 'out', `${story.id}.mp4`);
fs.mkdirSync(path.dirname(outFile), { recursive: true });

// CHROME_PATH lets you point at a local Chromium; otherwise Remotion downloads its own.
const browserExecutable = process.env.CHROME_PATH || null;

const serveUrl = await bundle({ entryPoint: path.join(root, 'src/index.ts'), publicDir: path.join(root, 'public') });
const inputProps = { timeline };
const composition = await selectComposition({ serveUrl, id: 'JokeVideo', inputProps, browserExecutable });

let last = -1;
await renderMedia({
  composition, serveUrl, inputProps, browserExecutable,
  codec: 'h264', crf: 16, x264Preset: process.env.X264_PRESET || 'slow',
  imageFormat: 'jpeg', jpegQuality: 100, colorSpace: 'bt709',
  audioCodec: 'aac', audioBitrate: '256k',
  outputLocation: outFile,
  concurrency: Math.max(1, os.cpus().length),
  chromiumOptions: { gl: 'swangle' },
  onProgress: ({ progress }) => {
    const p = Math.floor(progress * 10);
    if (p !== last) { last = p; process.stdout.write(`render ${p * 10}%\n`); }
  },
});
console.log(`-> ${outFile}`);
