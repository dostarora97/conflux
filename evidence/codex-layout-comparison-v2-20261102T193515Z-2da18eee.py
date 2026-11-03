#!/usr/bin/env python3
"""Matched small workload; history/byte accounting, not throughput or swarm benchmark."""
from pathlib import Path
import json, os, random, subprocess, tempfile
ENV={k:v for k,v in os.environ.items() if not k.startswith('GIT_')}
ENV.update(GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL='/dev/null',GIT_NO_REPLACE_OBJECTS='1',GIT_AUTHOR_NAME='Layout Study',GIT_AUTHOR_EMAIL='test@example.invalid',GIT_COMMITTER_NAME='Layout Study',GIT_COMMITTER_EMAIL='test@example.invalid',GIT_AUTHOR_DATE='2000-01-01T00:00:00Z',GIT_COMMITTER_DATE='2000-01-01T00:00:00Z')
def git(repo,*args,input=None):
 r=subprocess.run(['git','-C',str(repo),'-c','gc.auto=0','-c','core.hooksPath=/dev/null','-c','pack.threads=1','-c','index.threads=1',*args],input=input,capture_output=True,env=ENV)
 if r.returncode:raise RuntimeError(r.stderr.decode())
 return r.stdout.decode().strip()
def make(repo):repo.mkdir();git(repo,'init','--bare','-q')
def blob(repo,b):return git(repo,'hash-object','-w','--stdin',input=b)
def tree(repo,entries):return git(repo,'mktree',input=''.join('100644 blob '+oid+'\t'+name+'\n' for name,oid in sorted(entries.items())).encode())
def commit(repo,t,label,parent=None):
 return git(repo,'commit-tree',t,*(['-p',parent] if parent else []),input=(label+'\n').encode())
def stats(repo):
 lines=git(repo,'rev-list','--objects','--all').splitlines()
 oids=sorted({line.split()[0] for line in lines})
 rows=git(repo,'cat-file','--batch-check=%(objecttype) %(objectsize)',input=('\n'.join(oids)+'\n').encode()).splitlines()
 kinds={}
 for row in rows:
  kind,size=row.split();v=kinds.setdefault(kind,{'count':0,'bytes':0});v['count']+=1;v['bytes']+=int(size)
 return {'object_types':kinds,'total_uncompressed_object_bytes':sum(v['bytes'] for v in kinds.values()),'pack_bytes':sum(p.stat().st_size for p in (repo/'objects'/'pack').glob('*.pack'))}
def run():
 n=6;rooms=4;per_writer=20;payload_size=4096;work=[]
 for w in range(n):
  for q in range(per_writer):
   targets=[q%rooms]
   if q%5==0:targets.append((q+1)%rooms)
   work.append({'writer':w,'sequence':q,'targets':targets,'payload':random.Random(10000*w+q).randbytes(payload_size)})
 results={}
 with tempfile.TemporaryDirectory(prefix='git-layout-study-',dir='/private/tmp') as td:
  base=Path(td)
  for layout in ('global','channel'):
   source=base/(layout+'.git');reader=base/(layout+'-reader.git');make(source);make(reader)
   tips={}; refs={};metadata={};genesis=set()
   for event in work:
    w=event['writer'];q=event['sequence'];body=blob(source,event['payload'])
    channels=[None] if layout=='global' else event['targets']
    for ch in channels:
     key=(w,ch)
     if key not in tips:
      init={'version':1,'kind':'init','writer':w,'channel':ch}
      it=tree(source,{'packet.json':blob(source,json.dumps(init,sort_keys=True).encode())})
      tips[key]=commit(source,it,'genesis '+str(key));genesis.add(tips[key])
      refs[key]='refs/heads/study/'+('global/w'+str(w) if ch is None else 'room'+str(ch)+'/w'+str(w))
     record={'version':1,'kind':'message','record_id':f'w{w}-s{q}','writer':w,'channel':ch,'targets':event['targets'],'content':'body.bin'}
     t=tree(source,{'packet.json':blob(source,json.dumps(record,sort_keys=True).encode()),'body.bin':body})
     c=commit(source,t,'publication '+str(key)+' '+str(q),tips[key]);tips[key]=c;metadata[c]=record
   for key,tip in tips.items():git(source,'update-ref',refs[key],tip)
   selected=[ref for (w,ch),ref in refs.items() if ch is None or ch==0]
   git(reader,'fetch','-q','--no-tags',source.as_uri(),*[f'{ref}:refs/remotes/study/{i}' for i,ref in enumerate(selected)])
   received=set(git(reader,'rev-list','--all').splitlines())
   messages=[metadata[c] for c in received if c in metadata]
   useful={r['record_id'] for r in messages if 0 in r['targets']}
   assert useful=={f"w{e['writer']}-s{e['sequence']}" for e in work if 0 in e['targets']}
   results[layout]={'published_stream_refs':len(refs),'publication_commits_excluding_genesis':len(metadata),'genesis_commits':len(genesis),'reader_selected_refs':len(selected),'reader_received_publication_commits':len(messages),'reader_useful_logical_messages':len(useful),'reader_unrelated_publication_commits':sum(0 not in r['targets'] for r in messages),'source':stats(source),'cold_reader':stats(reader)}
 return {'scope':'Small deterministic local bare/file Git workload. Matched JSON/tree packet representation, one record/commit; no manifests, policy, local journal, authentication, network latency, concurrency, retention or production benchmark. Object bytes are uncompressed payload sizes; pack bytes count .pack only, not .idx/refs/disk allocation. Absolute overhead depends on chosen representation.','workload':{'writers':n,'rooms':rooms,'logical_records_per_writer':per_writer,'logical_records_total':len(work),'random_payload_bytes_per_record':payload_size,'multicast_rule':'Every fifth record also targets the next room; all other records target one room. Each writer publishes to every room. Reader subscribes only room0.','multicast_records':sum(len(e['targets'])>1 for e in work),'seed':'Random(10000*writer+sequence), Python randbytes'},'git_version':subprocess.check_output(['git','--version'],text=True).strip(),'results':results}
if __name__=='__main__':print(json.dumps(run(),indent=2))
