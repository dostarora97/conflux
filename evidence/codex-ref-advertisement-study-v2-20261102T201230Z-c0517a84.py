#!/usr/bin/env python3
"""Local ref inventory measurement, not 100 live agents or network benchmark."""
from pathlib import Path
import json,os,re,subprocess,tempfile,time
E={k:v for k,v in os.environ.items() if not k.startswith('GIT_')}
E.update(GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL='/dev/null',GIT_AUTHOR_NAME='Ref Study',GIT_AUTHOR_EMAIL='test@example.invalid',GIT_COMMITTER_NAME='Ref Study',GIT_COMMITTER_EMAIL='test@example.invalid')
def git(repo,*a,input=None,extra=None):
 env=E.copy();env.update(extra or {})
 r=subprocess.run(['git','-C',str(repo),'-c','gc.auto=0',*a],input=input,text=True,capture_output=True,env=env)
 if r.returncode:raise RuntimeError(r.stderr)
 return r.stdout

def run():
 results=[];writers=100;rooms=100
 with tempfile.TemporaryDirectory(prefix='git-ref-study-',dir='/private/tmp') as td:
  root=Path(td);client=root/'client.git';client.mkdir();git(client,'init','--bare','-q')
  for layout in ('global','channel'):
   remote=root/(layout+'.git');remote.mkdir();git(remote,'init','--bare','-q')
   tree=git(remote,'mktree',input='').strip();oid=git(remote,'commit-tree',tree,input='Shared fixture commit\n').strip()
   refnames=[f'refs/heads/catalog/c{r:03d}' for r in range(rooms)]
   if layout=='global':refnames += [f'refs/heads/writers/w{w:03d}' for w in range(writers)]
   else:refnames += [f'refs/heads/channels/c{r:03d}/writers/w{w:03d}' for r in range(rooms) for w in range(writers)]
   git(remote,'update-ref','--stdin',input=''.join(f'create {ref} {oid}\n' for ref in refnames))
   expected=len(refnames);actual=len(git(remote,'for-each-ref','--format=%(refname)').splitlines());assert actual==expected
   pattern='refs/heads/writers/*' if layout=='global' else 'refs/heads/channels/c050/writers/*'
   for storage in ('loose','packed'):
    if storage=='packed':git(remote,'pack-refs','--all','--prune')
    for label,version,patterns in [('v2_scoped',2,[pattern]),('v2_unscoped',2,[]),('v0_scoped_client_pattern',0,[pattern]),('v2_scoped_fetch',2,[pattern])]:
     trace=root/f'{layout}-{storage}-{label}.trace'
     begin=time.perf_counter()
     if label=='v2_scoped_fetch':
      dest=f'refs/remotes/study/{layout}/{storage}/'
      git(client,'-c',f'protocol.version={version}','fetch','--no-tags','--no-write-fetch-head',remote.as_uri(),pattern+':'+dest+'*',extra={'GIT_TRACE_PACKET':str(trace)})
      out=git(client,'for-each-ref','--format=%(refname)',dest)
     else:
      out=git(client,'-c',f'protocol.version={version}','ls-remote','--refs',remote.as_uri(),*patterns,extra={'GIT_TRACE_PACKET':str(trace)})
     elapsed=time.perf_counter()-begin
     log=trace.read_text()
     advertised=[]
     for line in log.splitlines():
      m=re.search(r'packet:\s+upload-pack> ([0-9a-f]{40,64}) (refs/[^\s]+)',line)
      if m:advertised.append((m.group(1),m.group(2).split(chr(92)+'0',1)[0]))
     # Count only server-side ref data lines once (not client duplicate trace lines).
     returned=len(out.splitlines())
     assert returned==(writers if patterns else expected),(layout,label,returned)
     assert advertised,(layout,label,'trace parser found no server advertisement')
     if version==2:assert 'version 2' in log
     payload=sum(len(o)+1+len(ref)+1 for o,ref in advertised)
     prefixes=[line.split('ref-prefix ',1)[1] for line in log.splitlines() if '> ref-prefix ' in line]
     results.append({'layout':layout,'ref_storage':storage,'query':label,'operation':'fetch' if label=='v2_scoped_fetch' else 'ls-remote','total_remote_refs':expected,'returned_refs_after_client_filter':returned,'server_advertised_ref_lines':len(advertised),'server_ref_line_payload_bytes_excluding_pkt_headers_and_capabilities':payload,'client_sent_prefixes':prefixes,'local_elapsed_seconds_single_warm_or_cold_unspecified_sample':round(elapsed,6)})
  return {'scope':'Local file transport, 100 publisher labels,100 channel labels, one fixture commit shared by all refs. No message histories/real catalogs, no100independentagents/no concurrentpollers/noWAN/noauthorization/nopublishthroughput. Payload bytes count traced server ref-data lines only, not complete wire traffic. Timing is one uncontrolled local-cache sample, not cold-latency benchmark. Protocolv2 may ignore ref-prefix on other servers; do not generalize provider support.','git_version':git(client,'--version').strip(),'results':results}
if __name__=='__main__':print(json.dumps(run(),indent=2))
