$ErrorActionPreference='Continue'
$repo='C:\Genesis_System3_clean';$out='C:\Genesis_System3_clean\reports\latest\ui_recovery'
$scopes=@('core/brokers/dhan','core/data','core/engine','dashboard/backend','dashboard/frontend/src')
$paths=@(git -C $repo ls-files -- '*.py' '*.ts' '*.tsx' '*.md' '*.json' '*.yml' '*.yaml' '*.ps1')
$paths=@($paths | Where-Object {$_ -notmatch '(^|/)(\.secrets|node_modules|\.venv|dist|build|__pycache__)/' -and $_ -notmatch '(^|/)(\.env|secret|credential|token_payload|private_key)(\.|$)'})
$files=foreach($rel in $paths){$p=Join-Path $repo ($rel -replace '/','\');if(Test-Path -LiteralPath $p -PathType Leaf){$f=Get-Item -LiteralPath $p;[pscustomobject]@{rel=$rel;name=$f.Name;ext=$f.Extension;length=$f.Length;path=$p;dir=($rel -replace '/[^/]+$','')}}}
$checks=New-Object System.Collections.Generic.List[object]
$idx=0
foreach($scope in $scopes){
 $set=@($files|Where-Object {$_.rel -like "$scope/*"})
 $patterns=@(
 @{name='same_filename_multiple_paths';kind='name'},
 @{name='same_size_multiple_paths';kind='length'},
 @{name='zero_byte_files';kind='zero'},
 @{name='tiny_source_under_100_bytes';kind='tiny'},
 @{name='oversized_source_over_100KB';kind='huge'},
 @{name='backup_or_copy_suffix';kind='backup'},
 @{name='legacy_or_deprecated_filename';kind='legacy'},
 @{name='test_or_mock_in_runtime_tree';kind='mock'},
 @{name='mixed_case_name_collisions';kind='case'},
 @{name='duplicate_content_sha256';kind='hash'}
 )
 foreach($pat in $patterns){$idx++;$samples=@();$count=0
 switch($pat.kind){
 'name' {$hits=@($set|Group-Object name|Where-Object Count -gt 1);$count=$hits.Count;$samples=@($hits|Select-Object -First 6|ForEach-Object {($_.Group.rel -join ' <> ')})}
 'length' {$hits=@($set|Where-Object length -gt 0|Group-Object length|Where-Object Count -gt 1);$count=$hits.Count;$samples=@($hits|Select-Object -First 6|ForEach-Object {($_.Group.rel -join ' <> ')})}
 'zero' {$hits=@($set|Where-Object length -eq 0);$count=$hits.Count;$samples=@($hits|Select-Object -First 6 -ExpandProperty rel)}
 'tiny' {$hits=@($set|Where-Object {$_.length -gt 0 -and $_.length -lt 100});$count=$hits.Count;$samples=@($hits|Select-Object -First 6 -ExpandProperty rel)}
 'huge' {$hits=@($set|Where-Object length -gt 102400);$count=$hits.Count;$samples=@($hits|Select-Object -First 6 -ExpandProperty rel)}
 'backup' {$hits=@($set|Where-Object {$_.name -match '(copy|backup|old|bak|\([0-9]+\)|_v[0-9]+)'});$count=$hits.Count;$samples=@($hits|Select-Object -First 6 -ExpandProperty rel)}
 'legacy' {$hits=@($set|Where-Object {$_.name -match '(legacy|deprecated|obsolete|retired)'});$count=$hits.Count;$samples=@($hits|Select-Object -First 6 -ExpandProperty rel)}
 'mock' {$hits=@($set|Where-Object {$_.name -match '(test_|mock|dummy|synthetic|fixture)'});$count=$hits.Count;$samples=@($hits|Select-Object -First 6 -ExpandProperty rel)}
 'case' {$hits=@($set|Group-Object {$_.name.ToLowerInvariant()}|Where-Object {(@($_.Group|Select-Object -ExpandProperty name -Unique)).Count -gt 1});$count=$hits.Count;$samples=@($hits|Select-Object -First 6|ForEach-Object {($_.Group.rel -join ' <> ')})}
 'hash' {$hashed=foreach($f in $set){if($f.length -le 2097152){try{[pscustomobject]@{rel=$f.rel;hash=(Get-FileHash -LiteralPath $f.path -Algorithm SHA256).Hash}}catch{}}};$hits=@($hashed|Group-Object hash|Where-Object {$_.Count -gt 1 -and $_.Name});$count=$hits.Count;$samples=@($hits|Select-Object -First 6|ForEach-Object {($_.Group.rel -join ' <> ')})}
 }
 $checks.Add([pscustomobject]@{id=('MM-{0:D3}' -f $idx);scope=$scope;check=$pat.name;files_scanned=$set.Count;findings=$count;examples=($samples -join ' ; ');classification='CANDIDATE_NOT_DEFECT'})
 }
}
$checks|ConvertTo-Json -Depth 5|Set-Content -LiteralPath (Join-Path $out 'GENESIS_50_MISMATCH_CHECKS.json') -Encoding UTF8
$md=@('# Genesis System3 — 50 file mismatch forensic checks','', 'Source: on-disk tracked code/docs. Checks are read-only, except reports written here. SHA-256 only for files <=2MB. Same size or same filename does not prove defect. Excludes secret-like filenames.','', 'Scanned tracked, on-disk files: '+$files.Count,'','| Check | Scope | Heuristic | Matches | Sample paths |','|---|---|---|---:|---|')+@($checks|ForEach-Object {'| '+$_.id+' | '+$_.scope+' | '+$_.check+' | '+$_.findings+' | '+($_.examples -replace '\|','/')+' |'})
$md|Set-Content -LiteralPath (Join-Path $out 'GENESIS_50_MISMATCH_CHECKS.md') -Encoding UTF8
'CHECKS='+$checks.Count;'TRACKED_FILES_PRESENT='+$files.Count;'CHECKS_WITH_MATCHES='+@($checks|Where-Object findings -gt 0).Count
$checks|Where-Object findings -gt 0|Select-Object id,scope,check,findings,examples|Format-Table -Wrap -AutoSize|Out-String -Width 220
