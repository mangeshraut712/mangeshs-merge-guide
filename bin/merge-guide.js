#!/usr/bin/env node
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';

const NAME = 'oss-contribution-insights';
const MARKER = '.merge-guide-install.json';
const packageRoot = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const digest = data => crypto.createHash('sha256').update(data).digest('hex');
const exists = async p => { try {return await fs.lstat(p);} catch(e) {if(e.code==='ENOENT') return null; throw e;} };

export function destination({target, scope='user', home=os.homedir(), cwd=process.cwd(), dest, claudeConfig=process.env.CLAUDE_CONFIG_DIR, platformPath=path}) {
  if(dest) {
    if(target || scope !== 'user') throw new Error('--dest cannot be combined with --target or --scope');
    return platformPath.resolve(cwd, dest);
  }
  if(!['codex','claude','cursor'].includes(target)) throw new Error('Choose --target codex|claude|cursor or an explicit --dest directory.');
  if(!['user','project'].includes(scope)) throw new Error('--scope must be user or project');
  if(target==='claude' && scope==='user' && claudeConfig) return platformPath.resolve(cwd,claudeConfig,'skills',NAME);
  const root = scope==='user' ? home : cwd;
  const folder = {codex:'.agents',claude:'.claude',cursor:'.cursor'}[target];
  return platformPath.join(root,folder,'skills',NAME);
}

async function rejectSymlinkAncestors(p) {
  let current=path.resolve(p);
  while(true) {
    const stat=await exists(current);
    if(stat?.isSymbolicLink()) throw new Error(`Refusing symlink path: ${current}`);
    if(stat && !stat.isDirectory()) throw new Error(`Not a directory: ${current}`);
    const parent=path.dirname(current); if(parent===current) break; current=parent;
  }
}

async function inventory(root, skipMarker=false, skipGenerated=false) {
  const files={};
  async function walk(dir,rel='') {
    for(const entry of await fs.readdir(dir,{withFileTypes:true})) {
      if(skipMarker && rel==='' && entry.name===MARKER) continue;
      if(skipGenerated && (entry.name==='__pycache__' || /\.py[co]$/.test(entry.name))) continue;
      const r=rel ? `${rel}/${entry.name}` : entry.name;
      if(entry.isSymbolicLink()) throw new Error(`Refusing symlink in skill: ${r}`);
      if(entry.isDirectory()) await walk(path.join(dir,entry.name),r);
      else if(entry.isFile()) files[r]=await fs.readFile(path.join(dir,entry.name));
      else throw new Error(`Unsupported file: ${r}`);
    }
  }
  await walk(root);return files;
}
const hashes = files => Object.fromEntries(Object.keys(files).sort().map(k=>[k,digest(files[k])]));

export async function install({dest,source=path.join(packageRoot,'skills',NAME),dryRun=false,upgrade=false,version='0.1.0'}) {
  dest=path.resolve(dest);
  await rejectSymlinkAncestors(dest);
  const files=await inventory(source,false,true);
  if(!files['SKILL.md'] || !files.LICENSE || files[MARKER]) throw new Error('Invalid packaged skill');
  const prior=await exists(dest);
  if(prior) {
    if(!upgrade) throw new Error('Destination already exists. Use --upgrade only for an unchanged managed installation.');
    const markerStat=await exists(path.join(dest,MARKER));
    if(!markerStat?.isFile() || markerStat.isSymbolicLink()) throw new Error('Existing installation is not managed; no files changed.');
    const marker=JSON.parse(await fs.readFile(path.join(dest,MARKER),'utf8'));
    if(marker.name!==NAME || marker.schema!==1 || JSON.stringify(hashes(await inventory(dest,true)))!==JSON.stringify(marker.files)) throw new Error('Existing files were modified or added; preserve them manually before upgrading.');
  } else if(upgrade) throw new Error('No existing managed installation to upgrade.');
  if(dryRun) return {destination:dest,action:prior?'upgrade':'install',dryRun:true,files:Object.keys(files).length};
  const parent=path.dirname(dest);
  await fs.mkdir(parent,{recursive:true});
  await rejectSymlinkAncestors(parent);
  const lock=dest+'.install-lock';
  const lockHandle=await fs.open(lock,'wx',0o600);
  let stage,backup;
  try {
    // Cooperating installers share this lock. Recheck state after acquiring it.
    const now=await exists(dest);
    if(Boolean(now)!==Boolean(prior)) throw new Error('Destination changed during installation; retry after inspection.');
    await rejectSymlinkAncestors(dest);
    if(prior) {
      const marker=JSON.parse(await fs.readFile(path.join(dest,MARKER),'utf8'));
      if(marker.name!==NAME || marker.schema!==1 || JSON.stringify(hashes(await inventory(dest,true)))!==JSON.stringify(marker.files)) throw new Error('Existing installation changed; upgrade cancelled.');
    }
    stage=await fs.mkdtemp(path.join(parent,'.merge-guide-stage-'));
    for(const [rel,data] of Object.entries(files)) {
      const out=path.join(stage,...rel.split('/'));await fs.mkdir(path.dirname(out),{recursive:true});await fs.writeFile(out,data,{flag:'wx'});
    }
    await fs.writeFile(path.join(stage,MARKER),JSON.stringify({schema:1,name:NAME,version,files:hashes(files)},null,2)+'\n',{flag:'wx',mode:0o600});
    if(prior) {backup=dest+'.backup-'+crypto.randomUUID();await fs.rename(dest,backup);}
    try {await fs.rename(stage,dest);stage=null;} catch(e) {if(backup) {await fs.rename(backup,dest);backup=null;}throw e;}
    return {destination:dest,action:prior?'upgraded':'installed',backup:backup??null,files:Object.keys(files).length};
  } finally {
    if(stage) await fs.rm(stage,{recursive:true,force:true});
    await lockHandle.close();await fs.unlink(lock);
  }
}

const HELP=`Mangesh’s Merge Guide installer
Usage: merge-guide install --target codex|claude|cursor [--scope user|project] [--dry-run] [--upgrade]
       merge-guide install --dest PATH [--dry-run] [--upgrade]
Installs the complete skill, not the agent runtime. --dest is the exact skill folder.
No credentials, telemetry, background jobs or automatic updates. Existing files are preserved.
`;
export async function main(args=process.argv.slice(2)) {
  if(!args.length || args.includes('--help') || args.includes('-h')) {console.log(HELP);return;}
  if(args[0]!=='install') throw new Error('Expected install; use --help.');
  const options={};
  for(let i=1;i<args.length;i++) {
    const a=args[i];
    if(['--dry-run','--upgrade'].includes(a)) options[a==='--dry-run'?'dryRun':'upgrade']=true;
    else if(['--target','--scope','--dest'].includes(a)) {const v=args[++i];if(!v || v.startsWith('--')) throw new Error(`Missing value for ${a}`);if(options[a.slice(2)])throw new Error(`Duplicate ${a}`);options[a.slice(2)]=v;}
    else throw new Error(`Unknown argument: ${a}`);
  }
  const pkg=JSON.parse(await fs.readFile(path.join(packageRoot,'package.json'),'utf8'));
  const result=await install({...options,dest:destination(options),version:pkg.version});
  console.log(JSON.stringify(result,null,2));
  if(!options.dryRun)console.log('Files installed. Verify discovery in your configured agent, then invoke oss-contribution-insights. Task execution and upstream acceptance are separate checks.');
}
if(process.argv[1] && await fs.realpath(process.argv[1]).catch(()=>null)===fileURLToPath(import.meta.url)) main().catch(e=>{console.error(`merge-guide: ${e.message}`);process.exitCode=1;});
