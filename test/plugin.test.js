import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

const read = (path) => JSON.parse(fs.readFileSync(new URL(path, import.meta.url), 'utf8'));
const pkg = read('../package.json');
const plugin = read('../.claude-plugin/plugin.json');
const marketplace = read('../.claude-plugin/marketplace.json');

test('plugin version tracks the npm package version', () => {
  assert.equal(plugin.version, pkg.version);
});

test('marketplace entry installs the plugin from the repository root', () => {
  assert.equal(marketplace.plugins.length, 1);
  assert.equal(marketplace.plugins[0].name, plugin.name);
  assert.equal(marketplace.plugins[0].source, './');
});

test('plugin root keeps the layout claude.ai can install', () => {
  // claude.ai and Cowork refuse a plugin with a top-level bin/ directory.
  assert.equal(fs.existsSync(new URL('../bin', import.meta.url)), false);
  assert.ok(fs.existsSync(new URL('../skills/oss-contribution-insights/SKILL.md', import.meta.url)));
  assert.equal(plugin.license, pkg.license);
});
