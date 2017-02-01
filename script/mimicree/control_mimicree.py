# -*- coding: utf-8 -*-
from cproc import cproc
import sys
cp = cproc(False)
def make_simfile(pop,slc,gen,rep,DDIR):
    TAG=DDIR.split('/')[-1]
    reprange = range(0,rep)
    #variables
    WDIR="/home/ykojima/Projects/wfeed/tmp/mimicree"
    SDIR="/home/ykojima/Projects/wfeed/script/mimicree"
    cov = "100"
    hapfile = DDIR + "/hap_init.mimhap"
    #command for snps
    basecnd = "-n 40 -e 0.5 -m 0.8 --loci-count 4000 "
    slccnd = "-s " + slc + " "
    inpfn = "--input " + hapfile + " "
    snpfn = DDIR + "/snps/s" + slc + "_r6.txt "
    cmdsnps = "python " + SDIR + "/toysoft/pick-random-addtive-snps.py " + basecnd + slccnd + inpfn +  "> " + snpfn
    cp.add(cmdsnps)
    #command for ref
    ofnsa = DDIR + "/sim" + "_s" + slc + ".sync "
    cofnsa = DDIR + "/tmp/sim" + "_s" + slc + ".sync "
    ofnda = DDIR + "/sim" + "_s" + slc + ".dat "
    cofnda = DDIR + "/tmp/sim" + "_s" + slc + ".dat "
    cmdref = "cp " + WDIR + "/sim_ref.sync " + ofnsa
    cp.add(cmdref)
    cmdrm = "rm " + ofnda
    cmdtch = "touch " + ofnda
    cp.add(cmdrm)
    cp.add(cmdtch)
    cp.mkqsf(TAG+"shared"+slc)
    #qsub for setting
    cp.qsub(TAG+"shared"+slc,"setting")
    ##command for simulation
    cmdb = "java -Xmx1g "
    cndb = "--output-format sync --threads 1 "
    scfn = "-jar " + SDIR + "/toysoft/MimicrEESummary.jar "
    recomb = "--recombination-rate " + WDIR + "/dmel.rr.txt "
    snps = "--additive " + snpfn
    hap = "--haplotypes-g0 " + DDIR + "/hap_init.mimhap "
    for rnum in reprange:
        strnum = str(rnum) 
        #variables in loop
        opm = "--output-mode " + gen + " "
        rofns = DDIR + "/tmp/sim_r_g" + strnum + "_s" + slc + ".sync "
        ofns = DDIR + "/tmp/sim_g" + strnum + "_s" + slc + ".sync "
        ofno = DDIR + "/tmp/sim_g" + strnum + "_s" + slc + ".o "
        ofn =  "--output-file " + rofns
        ofnd = DDIR + "/tmp/sim_g" + strnum + "_s" + slc + ".dat "
        #commands
        cmdsim = cmdb + scfn + cndb + recomb + opm + snps + ofn + hap
        #poisson sampling
        cmdpois = "python " + SDIR + "/poisson-3fold-sample.py "
        cmdpois += "--input " + rofns + "--coverage " + cov + " >> " + ofns
        #extract one colomn
        cmdawko = "awk \'{print $NF}\' " + ofns + "> " + ofno
        #A and C and Generation
        cmdawkd = "awk -F \":\" -v GEN="+ gen + " \'{print $1 \"\\t\" $3 \"\\t\" GEN}\' " + ofno + "> " + ofnd
        cp.add(cmdsim)
        cp.add(cmdpois)
        cp.add(cmdawko)
        cp.add(cmdawkd)        
        cp.mkqsf(TAG+"simulation"+slc)
    cp.job_size(4)
    cp.qsub(TAG+"simulation"+slc,"shared"+slc)
    #command for concating data
    for rnum in reprange:
        strnum = str(rnum) 
        ofnd = DDIR + "/tmp/sim_g" + strnum  + "_s" + slc +".dat "
        ofno = DDIR + "/tmp/sim_g" + strnum + "_s" + slc + ".o "
        cmdpst = "paste " + ofnsa + ofno + "> " + cofnsa
        cmdcp = "cp " + cofnsa + ofnsa
        cmdpstd = "paste " + ofnda + ofnd + "> " + cofnda
        cmdcpd = "cp " + cofnda + ofnda        
        cp.add(cmdpst)
        cp.add(cmdcp)
        cp.add(cmdpstd)
        cp.add(cmdcpd)
    #initial tab at line eliminated
    cmdsed = "sed -e 's/^\t//g' " + cofnda + "> " + ofnda
    cp.add(cmdsed)
    cp.mkqsf(TAG+"concating"+slc)
    cp.qsub(TAG+"concating"+slc,"simulation"+slc)
def make_labels(slc,DDIR):
    TAG=DDIR.split('/')[-1]
    WDIR="/home/ykojima/Projects/wfeed/tmp/mimicree"
    SDIR="/home/ykojima/Projects/wfeed/script/mimicree"
    ofnsa = DDIR + "/sim" + "_s" + slc + ".sync "
    snpfn = DDIR + "/snps/s" + slc + "_r6.txt "
    lbfn = DDIR + "/lb_s" + slc + "_r6.txt "
    cmdlb = "python " + SDIR + "/toysoft/rocr-generate-labellist.py " + ofnsa + snpfn + "> " + lbfn
    cp.add(cmdlb)
    cp.mkqsf(TAG+"labeling")
    cp.qsub(TAG+"labeling",TAG+"concating"+slc,TAG+"concating"+"0")
    
if __name__=="__main__":
    #variables
    WDIR="/home/ykojima/Projects/wfeed/tmp/mimicree"
    SDIR="/home/ykojima/Projects/wfeed/script/mimicree"
    gen = "60"
    pop = "1000"
    slc = "0.05"
    rep = 6
    DDIR = WDIR + "/sim_p" + pop + "_s" + slc + "_gen" + gen
    TAG=DDIR.replace('/','_')
    #command for setting
    cmdmkdir = "mkdir " + DDIR + " " + DDIR + "/tmp " + DDIR + "/snps" 
    cp.add(cmdmkdir)
    #make mimhap
    chapfile = DDIR + "/tmp/hap_init.mimhap"
    hapfile = DDIR + "/hap_init.mimhap"
    cmdmimhap = "python " + SDIR + "/mimhap_gen.py " + "4000 " + pop + " " + chapfile
    cmdphap = "paste " + WDIR + "/hap_ref.mimhap " + chapfile + " > " + hapfile
    cp.add(cmdmimhap)
    cp.add(cmdphap)
    cp.mkqsf("setting")
    cp.qsub("setting")
    #do simulation
    make_simfile(pop,slc,gen,rep,DDIR)
    make_simfile(pop,"0",gen,rep,DDIR)
    make_labels(slc,DDIR)
    #java -Xmx1g -jar /home/ykojimaProjects/wfeed/script/mimicree/toysoft/MimicrEESummary.jar --output-format sync --threads 2 --recombination-rate /home/ykojimaProjects/wfeed/tmp/mimicree/dmel.rr.txt --output-mode 45 --additive /home/ykojimaProjects/wfeed/tmp/mimicree/sim_p1000_s0.01_r6/snps/s0.01_r6.txt --output-file /home/ykojimaProjects/wfeed/tmp/mimicree/sim_p1000_s0.01_r6/tmp/sim_g45.sync
    
