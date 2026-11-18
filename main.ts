import { copyFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const sourceDirectory: string = dirname(fileURLToPath(import.meta.url));
const outputDirectory: string = process.env.MAKEFUN_OUTPUT_DIR || '/output';

mkdirSync(outputDirectory, { recursive: true });
copyFileSync(join(sourceDirectory, 'entry.png'), join(outputDirectory, 'entry.png'));
