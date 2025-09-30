# api/result.py (updated)
# Returns normalized rows: maps Reg, Name, Uni-Roll No, Col Roll No, subject columns, Total Back, Result, SGPA
import os, json
from urllib.parse import parse_qs

# synonyms lists for mapping
REG_SYNS = ['reg','reg. no','reg no','regno','registration','registration no','registration number','regno.','reg. no.','regno']
NAME_SYNS = ['name','student name','candidate name','full name']
UNI_SYNS = ['uni-roll','uni-roll no','uni roll','uni roll no','uni-roll no','uni roll number','uni-roll-number','uni-roll-no','uni roll']
COLROLL_SYNS = ['col roll','college roll','col roll no','col-roll-no','colroll','section','class','college roll no']

TRAILING_SYNS = {
  'total_back': ['total back','back','totalback','backlog','backlogs','total backlogs'],
  'result': ['result','status','pass/fail','pass fail'],
  'sgpa': ['sgpa','gpa','cgpa']
}

def find_key(keys, synonyms):
    lk = [k.lower().strip() for k in keys]
    for s in synonyms:
        s_norm = s.lower().strip()
        for i,k in enumerate(lk):
            if k == s_norm:
                return keys[i]
        for i,k in enumerate(lk):
            if s_norm in k or k in s_norm:
                return keys[i]
    return None

def is_subject_key(k):
    # heuristics: contains both letters and digits or matches typical codes like FEC or 4CS etc.
    if not k: return False
    kn = k.lower()
    if any(x in kn for x in ['fec','feco','fep']): return True
    if any(ch.isdigit() for ch in k) and any(ch.isalpha() for ch in k):
        return True
    # also if format like '4cs1-03' or contains subject-like patterns
    return False

def handler(request):
    try:
        params = {}
        if hasattr(request, 'args'):
            params = {k: v for k, v in request.args.items()}
        else:
            qs = request.environ.get('QUERY_STRING','')
            params = {k: v[0] for k, v in parse_qs(qs).items()}

        reg = params.get('reg','').strip()
        branch = params.get('branch','').strip()
        if not reg:
            return (json.dumps({'error':'reg is required'}), 400, {'Content-Type':'application/json'})
        if not branch:
            return (json.dumps({'error':'branch is required'}), 400, {'Content-Type':'application/json'})

        filename = os.path.join(os.getcwd(), 'data', f"{branch}.json")
        if not os.path.exists(filename):
            return (json.dumps({'error':'Incorrect entries or branch selection. Please try again.'}), 400, {'Content-Type':'application/json'})

        with open(filename, 'r', encoding='utf-8') as fh:
            rows = json.load(fh)

        # find keys from first row
        if not rows:
            return (json.dumps({'result': []}), 200, {'Content-Type':'application/json'})
        sample_keys = list(rows[0].keys())

        reg_key = find_key(sample_keys, REG_SYNS) or sample_keys[0]
        name_key = find_key(sample_keys, NAME_SYNS) or None
        uni_key = find_key(sample_keys, UNI_SYNS) or None
        colroll_key = find_key(sample_keys, COLROLL_SYNS) or None

        # subject detection
        subject_keys = [k for k in sample_keys if is_subject_key(k) and k not in [reg_key, name_key, uni_key, colroll_key]]
        # trailing keys
        total_back_key = find_key(sample_keys, TRAILING_SYNS['total_back'])
        result_key = find_key(sample_keys, TRAILING_SYNS['result'])
        sgpa_key = find_key(sample_keys, TRAILING_SYNS['sgpa'])

        normalized = []
        reg_norm = reg.strip().lower()
        for r in rows:
            # matching: look for reg in specific key first, else across values
            matched = False
            if reg_key and str(r.get(reg_key,'')).strip().lower() == reg_norm:
                matched = True
            else:
                for v in r.values():
                    if isinstance(v, str) and v.strip().lower() == reg_norm:
                        matched = True
                        break
            if not matched:
                # substring match as fallback
                for v in r.values():
                    if isinstance(v, str) and reg_norm in v.strip().lower():
                        matched = True
                        break
            if not matched:
                continue

            out = {}
            out['Reg'] = r.get(reg_key, '') if reg_key else ''
            out['Name'] = r.get(name_key, '') if name_key else ''
            out['Uni-Roll No'] = r.get(uni_key, '') if uni_key else ''
            out['Col Roll No'] = r.get(colroll_key, '') if colroll_key else ''

            # subjects in order
            for sk in subject_keys:
                out[sk] = r.get(sk, '')

            # totals / trailing
            if total_back_key:
                out['Total Back'] = r.get(total_back_key, '')
            else:
                # compute count of failures
                backc = 0
                for sk in subject_keys:
                    v = str(r.get(sk,'')).strip().upper()
                    if v == 'F' or 'FAIL' in v:
                        backc += 1
                out['Total Back'] = str(backc)

            out['Result'] = r.get(result_key, '') if result_key else r.get('Result','')
            out['SGPA'] = r.get(sgpa_key, '') if sgpa_key else r.get('SGPA','')

            normalized.append(out)

        return (json.dumps({'result': normalized}, ensure_ascii=False), 200, {'Content-Type':'application/json'})
    except Exception as e:
        return (json.dumps({'error': str(e)}), 500, {'Content-Type':'application/json'})
