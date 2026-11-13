import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';

const root = fileURLToPath(new URL('../', import.meta.url));
const temp = await fs.realpath(await fs.mkdtemp(path.join(os.tmpdir(), 'merge-package-')));
const npm = process.env.npm_execpath;
assert.ok(npm, 'Run this check with npm run test:package');
function run(args, cwd, expected = 0) {
  const result = spawnSync(process.execPath, [npm, ...args], {
    cwd, encoding: 'utf8', env: {...process.env, npm_config_update_notifier: 'false'},
  });
  assert.equal(result.status, expected, result.stdout + result.stderr);
  return expected === 0 ? result.stdout : result.stdout + result.stderr;
}
try {
  const [packed] = JSON.parse(run(['pack', '--json', '--pack-destination', temp], root));
  assert.ok(packed.files.some(f => f.path === 'skills/oss-contribution-insights/LICENSE'));
  assert.ok(packed.files.every(f => !f.path.includes('__pycache__') && !/\.py[co]$/.test(f.path)));
  const tarball = path.join(temp, packed.filename);
  const exec = ['exec', '--yes', '--package', tarball, '--', 'merge-guide'];
  assert.match(run([...exec, '--help'], temp), /Mangesh’s Merge Guide installer/);
  for (const [target, directory] of [['codex', '.agents'], ['claude', '.claude'], ['cursor', '.cursor']]) {
    const dest = path.join(temp, directory, 'skills', 'oss-contribution-insights');
    run([...exec, 'install', '--target', target, '--scope', 'project', '--dry-run'], temp);
    await assert.rejects(fs.stat(dest), {code: 'ENOENT'});
    run([...exec, 'install', '--target', target, '--scope', 'project'], temp);
    const marker = JSON.parse(await fs.readFile(path.join(dest, '.merge-guide-install.json'), 'utf8'));
    assert.equal(marker.version, JSON.parse(await fs.readFile(path.join(root, 'package.json'), 'utf8')).version);
    for (const [file, hash] of Object.entries(marker.files)) {
      const actual = await fs.readFile(path.join(dest, ...file.split('/')));
      assert.equal(crypto.createHash('sha256').update(actual).digest('hex'), hash);
      assert.deepEqual(actual, await fs.readFile(path.join(root, 'skills', 'oss-contribution-insights', ...file.split('/'))));
    }
    run([...exec, 'install', '--target', target, '--scope', 'project'], temp, 1);
    const before = await fs.readFile(path.join(dest, 'SKILL.md'), 'utf8');
    const upgrade = [...exec, 'install', '--target', target, '--scope', 'project', '--upgrade'];
    run([...upgrade, '--dry-run'], temp);
    assert.equal(await fs.readFile(path.join(dest, 'SKILL.md'), 'utf8'), before);
    run(upgrade, temp);
    const siblings = await fs.readdir(path.dirname(dest));
    const backups = siblings.filter(name => name.startsWith('oss-contribution-insights.backup-'));
    assert.equal(backups.length, 1);
    assert.equal(await fs.readFile(path.join(path.dirname(dest), backups[0], 'SKILL.md'), 'utf8'), before);
    const edited = before + '\nLocal contribution notes.\n';
    await fs.writeFile(path.join(dest, 'SKILL.md'), edited);
    assert.match(run(upgrade, temp, 1), /modified or added/);
    assert.equal(await fs.readFile(path.join(dest, 'SKILL.md'), 'utf8'), edited);
    console.log(`${target}: packed CLI, dry run, file parity, upgrade backup and local-edit preservation verified`);
  }
} finally {
  await fs.rm(temp, {recursive: true, force: true});
}
