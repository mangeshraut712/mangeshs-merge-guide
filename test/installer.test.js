import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import {install,destination,main} from '../bin/merge-guide.js';
async function fixture(fn){const root=await fs.realpath(await fs.mkdtemp(path.join(os.tmpdir(),'merge-test-')));try{const source=path.join(root,'source');await fs.mkdir(source);await fs.writeFile(path.join(source,'SKILL.md'),'test');await fs.writeFile(path.join(source,'LICENSE'),'MIT');await fn({root,source,dest:path.join(root,'home','skill')});}finally{await fs.rm(root,{recursive:true,force:true});}}
test('Windows and POSIX paths',()=>{assert.equal(destination({target:'codex',home:'C:\\Users\\A',platformPath:path.win32}),'C:\\Users\\A\\.agents\\skills\\oss-contribution-insights');assert.equal(destination({target:'cursor',scope:'project',cwd:'/project',platformPath:path.posix}),'/project/.cursor/skills/oss-contribution-insights');assert.throws(()=>destination({target:'unknown'}));});
test('dry run writes nothing',()=>fixture(async o=>{const r=await install({...o,dryRun:true});assert.equal(r.dryRun,true);await assert.rejects(fs.stat(path.dirname(o.dest)));}));
test('install keeps license and refuses existing destination',()=>fixture(async o=>{await install(o);assert.equal(await fs.readFile(path.join(o.dest,'LICENSE'),'utf8'),'MIT');await assert.rejects(install(o),/already exists/);}));
test('upgrade retains old complete backup',()=>fixture(async o=>{await install(o);await fs.writeFile(path.join(o.source,'SKILL.md'),'new');const r=await install({...o,upgrade:true});assert.equal(await fs.readFile(path.join(o.dest,'SKILL.md'),'utf8'),'new');assert.equal(await fs.readFile(path.join(r.backup,'SKILL.md'),'utf8'),'test');}));
test('modified and additional files block upgrade',()=>fixture(async o=>{await install(o);await fs.writeFile(path.join(o.dest,'notes.txt'),'mine');await assert.rejects(install({...o,upgrade:true}),/modified or added/);await fs.unlink(path.join(o.dest,'notes.txt'));await fs.writeFile(path.join(o.dest,'SKILL.md'),'mine');await assert.rejects(install({...o,upgrade:true}),/modified or added/);}));
test('unmanaged and missing upgrades refused',()=>fixture(async o=>{await assert.rejects(install({...o,upgrade:true}),/No existing/);await fs.mkdir(o.dest,{recursive:true});await assert.rejects(install({...o,upgrade:true}),/not managed/);}));
test('symlink destination including dangling target refused',()=>fixture(async o=>{await fs.mkdir(path.dirname(o.dest),{recursive:true});await fs.symlink(path.join(o.root,'missing'),o.dest);await assert.rejects(install(o),/symlink/);}));
test('symlink ancestor refused',()=>fixture(async o=>{await fs.mkdir(path.join(o.root,'actual'));await fs.symlink(path.join(o.root,'actual'),path.dirname(o.dest));await assert.rejects(install(o),/symlink/);}));
test('source symlink refused',()=>fixture(async o=>{await fs.symlink(path.join(o.source,'LICENSE'),path.join(o.source,'link'));await assert.rejects(install(o),/symlink/);}));
test('regular-file destination refused',()=>fixture(async o=>{await fs.mkdir(path.dirname(o.dest),{recursive:true});await fs.writeFile(o.dest,'keep');await assert.rejects(install(o),/Not a directory/);assert.equal(await fs.readFile(o.dest,'utf8'),'keep');}));
test('installer lock refused without changing target',()=>fixture(async o=>{await fs.mkdir(path.dirname(o.dest),{recursive:true});await fs.writeFile(o.dest+'.install-lock','keep');await assert.rejects(install(o),/EEXIST/);assert.equal(await fs.readFile(o.dest+'.install-lock','utf8'),'keep');}));
test('argument errors',async()=>{await assert.rejects(main(['install','--target']),/Missing/);await assert.rejects(main(['install','--wat']),/Unknown/);assert.throws(()=>destination({target:'codex',dest:'x'}),/cannot/);});

test('Claude configuration root respected',()=>{assert.equal(destination({target:'claude',claudeConfig:'/custom',platformPath:path.posix}),'/custom/skills/oss-contribution-insights');});
test('symlinked executable entry runs CLI',()=>fixture(async o=>{
  const {spawnSync}=await import('node:child_process');
  const {fileURLToPath}=await import('node:url');
  const link=path.join(o.root,'merge-guide');
  await fs.symlink(fileURLToPath(new URL('../bin/merge-guide.js',import.meta.url)),link);
  const run=spawnSync(process.execPath,[link,'--help'],{encoding:'utf8'});
  assert.equal(run.status,0);assert.match(run.stdout,/Mangesh’s Merge Guide installer/);
}));

test('generated source bytecode excluded',()=>fixture(async o=>{await fs.mkdir(path.join(o.source,'__pycache__'));await fs.writeFile(path.join(o.source,'__pycache__','foo.pyc'),'cache');await install(o);await assert.rejects(fs.stat(path.join(o.dest,'__pycache__')));}));


test('running Python helpers does not block a managed upgrade',()=>fixture(async o=>{
  await install(o);
  await fs.mkdir(path.join(o.dest,'scripts','__pycache__'),{recursive:true});
  await fs.writeFile(path.join(o.dest,'scripts','__pycache__','ledger.cpython-313.pyc'),'generated');
  await fs.writeFile(path.join(o.source,'SKILL.md'),'updated');
  const result=await install({...o,upgrade:true});
  assert.equal(await fs.readFile(path.join(o.dest,'SKILL.md'),'utf8'),'updated');
  assert.equal(await fs.readFile(path.join(result.backup,'scripts','__pycache__','ledger.cpython-313.pyc'),'utf8'),'generated');
}));
