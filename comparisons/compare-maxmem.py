#!/usr/bin/env python3
import sys
import json
from collections import defaultdict

def read_blocks(file):
    block = ''
    for line in file:
        if line.startswith("step") and len(block)>0:
            yield block
        else:
            block += line
    yield block

def create_memory_report(filename):
    memory_reports=list()
    step=0
    with open(filename, encoding="utf8", errors="ignore") as f:
        for block in read_blocks(f):
            step=step+1
            memory_report={}
            memory_report["step"]=step
            for line in block.split("\n"):
                if line.startswith("Memory Report:"):
                    fields=line.split(":")
                    memory_report[fields[1].strip()]=int(fields[2].strip())
            memory_reports.append(memory_report)
    return memory_reports


mem_prof_pr=create_memory_report(sys.argv[1])
mem_prof_base=create_memory_report(sys.argv[2])

sys.stdout.write("max memory pr")
sys.stdout.write("\n")
sys.stdout.write(json.dumps(mem_prof_pr))
sys.stdout.write("\n")
sys.stdout.write("max memory ib")
sys.stdout.write("\n")
sys.stdout.write(json.dumps(mem_prof_base))
sys.stdout.write("\n")
mem_keys=["step", "total memory requested",  "max memory used", "presently used", "# allocations calls", "# deallocations calls"]
mem_prof_pdiffs=[]
for i in range(1, len(mem_prof_pr)):
    step=0
    mem_prof_pdiff={}
    for key in mem_keys:
        if key == "step":
            step=mem_prof_pr[i][key]
            mem_prof_pdiff[key]=step
        else:
            diff=mem_prof_pr[i][key]-mem_prof_base[i][key]
            percent_diff=diff/mem_prof_pr[i][key]*100
            mem_prof_pdiff[key]=percent_diff
    mem_prof_pdiffs.append(mem_prof_pdiff)

sys.stdout.write("max memory percentage diffs")
sys.stdout.write("\n")
sys.stdout.write(json.dumps(mem_prof_pdiffs))
sys.stdout.write("\n")

mem_prof_adiffs=[]
for i in range(1, len(mem_prof_pr)): 
    step=0
    mem_prof_adiff={}
    for key in mem_keys:
        if key == "step":
            step=mem_prof_pr[i][key]
            mem_prof_adiff[key]=step
        else:
            diff=mem_prof_pr[i][key]-mem_prof_base[i][key]
            mem_prof_adiff[key]=diff
    mem_prof_adiffs.append(mem_prof_adiff)
sys.stdout.write("max memory absolute diffs")
sys.stdout.write("\n")
sys.stdout.write(json.dumps(mem_prof_adiffs))
sys.stdout.write("\n")

THREASHOLD=1.0
sys.stdout.write("threashold %2f%%" % THREASHOLD)
sys.stdout.write("\n")

errs=0
for i in range(0, len(mem_prof_pdiffs)):
    mmu=mem_prof_pdiffs[i]["max memory used"]
    if abs(mmu) > THREASHOLD:
        errs=errs+1
        sys.stderr.write("step %s max memory used percentage diff %2f%% exceeds threashhold %2f%%" % (mem_prof_pdiffs[i]["step"], abs(mmu), THREASHOLD))
        sys.stderr.write('\n')

if errs > 0:
    exit(10)
