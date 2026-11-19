// newsday-20261119 — make.fun news-image-20261119 entry (Node 22, stdlib only).
//
// The front page is rendered ahead of time by tools/draw.py (Pillow) and
// shipped in this repo as entry.png. This program only copies it into the
// grader's output directory, so it runs with no network and no dependencies.
//
// Outside the grader container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(outDir, { recursive: true });

const src = new URL('./entry.png', import.meta.url);
const dst = join(outDir, 'entry.png');
copyFileSync(src, dst);
console.log(`wrote ${dst}`);
