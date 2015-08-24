# requires rpm2cpio cpio installed
from yum.plugins import PluginYumExit, TYPE_CORE, TYPE_INTERACTIVE
from subprocess import call, Popen, PIPE

import subprocess
import re
import os
import sys
import fileinput

requires_api_version = '2.3'
plugin_type = (TYPE_CORE, TYPE_INTERACTIVE)
ID_STRING="[UNPACK]"
ID_PRFIX=ID_STRING+" "
NEVER_MATCH="NothingCanMatchMe"
ALL_MATCH=".*"
resrc1=ALL_MATCH
resrc1_forceIn=NEVER_MATCH
resrc1_forceOut=NEVER_MATCH
resrc2=ALL_MATCH
resrc3=NEVER_MATCH
groupSubpackagesSrc=NEVER_MATCH
pattern1 = None
pattern1_forceIn = None
pattern1_forceOut = None
pattern2 = None
pattern3 = None
path = '/opt/'
debuglevel=None
exitAfterUnpack = False
allpkgs = None
trimEpoch = False
groupSubpackages = None
allowFakeTransaction = False
fakeTransRemoval = re.compile(".*FakePackageToBeRemoved.*")


# all conduits described at http://yum.baseurl.org/api/yum/yum/plugins.html
# the hooks in http://yum.baseurl.org/wiki/WritingYumPlugins are not in any order, here they are ordered as yum is launching them


def init_hook(conduit):
    conduit.info(2, '***************************WARNING*****************************');
    conduit.info(2, '                 Unpack plugin active')
    conduit.info(2, 'Selected packagesunpacked to /opt or where destination in unpack.conf points.')
    conduit.info(2, 'Special exclusion/forcing from that confing is cosidered.')
    conduit.info(2, 'See the README.md page of and unpack.conf and eventuelly also unpack.py for more info.')
    conduit.info(2, '***************************************************************');
    global path
    global exitAfterUnpack
    global resrc1
    global resrc1_forceIn
    global resrc1_forceOut
    global resrc2
    global resrc3
    global trimEpoch
    global groupSubpackagesSrc
    global pattern1
    global pattern1_forceIn
    global pattern1_forceOut
    global pattern2
    global pattern3
    global groupSubpackages
    global allowFakeTransaction
    s = conduit.confString('main', 'destination', path)
    path = s
    s = conduit.confString('main', 'filter_pre1_repo', resrc1)
    resrc1 = s
    s = conduit.confString('main', 'filter_pre2_forceIn', resrc1_forceIn)
    resrc1_forceIn = s
    s = conduit.confString('main', 'filter_pre2_forceOut', resrc1_forceOut)
    resrc1_forceOut = s
    s = conduit.confString('main', 'filter_post', resrc2)
    resrc2 = s
    s = conduit.confString('main', 'filter_unpack', resrc3)
    resrc3 = s
    s = conduit.confBool('main', 'quit_after_unpack', False)
    exitAfterUnpack = s
    s = conduit.confBool('main', 'fake_transaction', False)
    allowFakeTransaction = s
    s = conduit.confBool('main', 'trim_epoch', False)
    trimEpoch = s
    s = conduit.confString('main', 'group_subpackages', groupSubpackagesSrc)
    groupSubpackagesSrc = s
    pattern1 = re.compile(resrc1)
    pattern1_forceIn = re.compile(resrc1_forceIn)
    pattern1_forceOut = re.compile(resrc1_forceOut)
    pattern2 = re.compile(resrc2)
    pattern3 = re.compile(resrc3)
    pattern3 = re.compile(resrc3)
    groupSubpackages  = re.compile(groupSubpackagesSrc)
    conduit.info(2, ID_PRFIX+'unpack to ' + path);
    conduit.info(2, ID_PRFIX+'filter_pre1_repo ' + resrc1);
    conduit.info(2, ID_PRFIX+'filter_pre2_forceIn ' + resrc1_forceIn);
    conduit.info(2, ID_PRFIX+'filter_pre2_forceOut ' + resrc1_forceOut);
    conduit.info(2, ID_PRFIX+'filter_post ' + resrc2);
    conduit.info(2, ID_PRFIX+'filter_unpack ' + resrc3);
    conduit.info(2, ID_PRFIX+'quit_after_unpack ' + str(exitAfterUnpack));
    conduit.info(2, ID_PRFIX+'trim_epoch ' + str(trimEpoch));
    conduit.info(2, ID_PRFIX+'group_subpackages ' + groupSubpackagesSrc);
    conduit.info(2, ID_PRFIX+'fake_transaction ' + str(allowFakeTransaction));
    global debuglevel
    debuglevel = conduit.getConf().debuglevel;
    conduit.info(3, ID_PRFIX+'debuglevel ' + str(debuglevel));


def config_hook(conduit):
        parser = conduit.getOptParser()
        parser.add_option('', '--unpack-only', dest='unpack_only',
                action='store_true', default=False,
                help="will overwrite unpack plugins seetings and will only unpack specified packages ")

def store_true(conduit):
	conduit.info(2, '* *?* *');

#yum.plugins.PostRepoSetupPluginConduit
def postreposetup_hook(conduit):
    conduit.info(3, conduit);
    conduit.info(3, '* *1* *');
    #overwriting unpack-only here
    opts, commands = conduit.getCmdLine()
    if opts.unpack_only:
        conduit.info(2, ID_PRFIX+' using unpack-only command ');
        global allowFakeTransaction
        global pattern1_forceOut
        global resrc1_forceOut
        global resrc1_forceIn
        global pattern1_forceIn
        resrc1_forceOut = ".*"
        resrc1_forceIn = ".*"
        pattern1_forceOut = re.compile(resrc1_forceOut)
        pattern1_forceIn = re.compile(resrc1_forceIn)
        allowFakeTransaction = True

class _Fake2:
	def __getitem__(a,b):
		return ""

class _Fake3:
	id = "a"

class _Fake:
	name = "FakePackageToBeRemoved"
	provides_names = []
	obsoletes_names = []
	requires = []
	repoid = "a"
	arch = "noarch"
	epoch = "0"
	version = "0.0"
	release = "0"
	id = "a"
	repo = _Fake3()
	ui_from_repo = "a"
	size = 0
	pkgtup = (name, arch, epoch, version, release)
	def have_fastReturnFileEntries(a):
		return False
	def returnPrco(a,b):
		return []
	def returnFileTypes(a):
		return []
	def returnIdSum(a):
		return _Fake2()
	def printVer(a):
		":)"
	def verifyLocalPkg(a):
		return True
	def verEQ(a,b):
		return True

#yum.plugins.MainPluginConduit
def exclude_hook(conduit):
    conduit.info(3, conduit);
    conduit.info(3, '* *2 *');
    #place to create fake trasnaction for "downlaod only"
    if allowFakeTransaction:
	    ts = conduit.getTsInfo()
	    q = ts.addUpdate(_Fake())
	    conduit.info(2, ID_PRFIX+'trans have ' + str(len(ts.matchNaevr())));

#yum.plugins.DepsolvePluginConduit
def preresolve_hook(conduit):
    #packages filtered out here will not play any role in upcoming trasnaction. If important dep is removed, transaction fails.
    conduit.info(3, conduit);
    conduit.info(3, '* *3* *');
    global allpkgs
    allpkgs = conduit.getPackages()  #all packages from all repos
    lmatching = []
    lNmatching = []
    conduit.info(2, ID_PRFIX+'applying filter_pre1_repo:');
    for s in allpkgs:
        name=s.ui_envra 
        if pattern1.match(name):
            conduit.info(4, ID_PRFIX+name + ' matching ' + resrc1)
            lmatching.append(s)
        else:
            conduit.info(4, 'bad luck for '+ name +  ' because ' + resrc1);
            lNmatching.append(s)
    conduit.info(2, ID_PRFIX+'removing ' + str(len(lNmatching))+ ' from total of '+ str(len(allpkgs)));
    for s in lNmatching:
        conduit.delPackage(s)
    conduit.info(2, ID_PRFIX+'remained ' + str(len(conduit.getPackages()))+ ' of expected '+ str(len(lmatching)));
    
# get type of variable
def more(s):
    return s.__repr__()


#yum.plugins.DepsolvePluginConduit
def postresolve_hook(conduit):
    # removing packages here (like in preresolve) have no effect, but transaction info is already filled
    # http://yum.baseurl.org/api/yum-3.2.27/yum.transactioninfo.TransactionData-class.html#setDatabases
    # packages cnabe added/removed here directly 
    #getPackageByNevra - find one exact package - cna be used to creae list of packages to downlaod manually whe user specified NVRA as input?
    #getPackages - return all package in repo or in all repos - can be used to create list fo packages to downlaod manually by using regex?
    conduit.info(3, conduit);
    conduit.info(3, '* *4* *');
    ts = conduit.getTsInfo()
    # lorig = conduit.getPackages() #just packages from trasnaction
    lorig = allpkgs #we wont smuggle into from all apckages
    lmatching1 = []
    lmatching2 = []
     
    conduit.info(2, ID_PRFIX+'applying filter_pre2_forceOut:'); #removal from transaction
    for s in ts.matchNaevr():
        name = s.__str__()
        if allowFakeTransaction:
		    if fakeTransRemoval.match(name):
			    ts.remove((s.name, s.arch, s.epoch, s.version, s.release))
        if pattern1_forceOut.match(name):
            conduit.info(4, ID_PRFIX+name + ' matching ' + resrc1_forceOut)
            lmatching2.append(s)
    
    conduit.info(2, ID_PRFIX+'applying filter_pre2_forceIn:'); #adding from all packages
    # jsut look for matching nvras
    for s in lorig:
        name=s.ui_envra 
        if pattern1_forceIn.match(name):
            conduit.info(4, ID_PRFIX+name + ' matching ' + resrc1_forceIn)
            lmatching1.append(s)
    
    conduit.info(2, ID_PRFIX+'removing ' + str(len(lmatching2))+ ' from trasnaction of '+ str(len(ts.matchNaevr())));
    for s in lmatching2:
        #s of TransactionMember
        ts.remove((s.name, s.arch, s.epoch, s.version, s.release))
    conduit.info(2, ID_PRFIX+'remained transaction of ' + str(len(ts.matchNaevr())));
    conduit.info(2, ID_PRFIX+'adding ' + str(len(lmatching1))+ ' to trasnaction of '+ str(len(ts.matchNaevr())));
    for s in lmatching1:
        # s of YumAvailablePackageSqlite
        q = ts.addUpdate(s)
        #q.isDep = 1 
    conduit.info(2, ID_PRFIX+'remained transaction of ' + str(len(ts.matchNaevr())));
    ts.changed=False
    #ts._unresolvedMembers.clear()
    #ts.changed=False

#yum.plugins.DownloadPluginConduit
#http://yum.baseurl.org/api/yum-3.2.26/yum.plugins.DownloadPluginConduit-class.html ?
def predownload_hook(conduit):
    conduit.info(3, conduit);
    conduit.info(3, '* *5* *');
    # list of http://yum.baseurl.org/api/yum-3.2.27/yum.sqlitesack.YumAvailablePackageSqlite-class.html
    lorig = conduit.getDownloadPackages();
    lnw = []
    # print out all packages from trasnaction
    #for s in lorig:
    #    conduit.info(2, s);
    conduit.info(2, ID_PRFIX+'applying filter_post:');
    for s in lorig:
        #name=s.sourcerpm
        #name=s.s. __str__()
        name=s.ui_envra 
        if pattern2.match(name):
            conduit.info(2, ID_PRFIX+name + ' matching ' + resrc2)
            lnw.append(s)
        else:
            conduit.info(2, ID_PRFIX+'bad luck for '+ name +  ' because ' + resrc2);
    del lorig[:]
    #recreatig list
    for s in lnw:
        lorig.append(s)

def getEpoch(s):
    index = s.find(":")
    if index < 0:
        return ("", s);
    return  (s[:index], s[index+1:])
    
    
def getArch(s):
    index = s.rfind(".")
    if index < 0:
        return (s,"");
    return  (s[:index], s[index+1:])

def getParentInTransactionArch(tl, parent):
    result = []
    for s in tl:
        if s.envra == parent:
            result.append(s)
    return result

def isParentInTransactionArch(tl, parent):
    #retyping :(
    if not getParentInTransactionArch(tl, parent):
        return False
    else:
        return True

def getParentInTransaction(tl, parent):
    result = []
    for s in tl:
        if getArch(s.envra)[0] == getArch(parent)[0]:
            result.append(s)
    return result

def isParentInTransaction(tl, parent):
    #retyping :(
    if not getParentInTransaction(tl, parent):
        return False
    else:
        return True

#yum.plugins.DownloadPluginConduit
#http://yum.baseurl.org/api/yum-3.2.26/yum.plugins.DownloadPluginConduit-class.html ?
def postdownload_hook(conduit):
    conduit.info(3, conduit);
    conduit.info(3, '* *6* *');
    # list of http://yum.baseurl.org/api/yum-3.2.27/yum.sqlitesack.YumAvailablePackageSqlite-class.html
    lorig = conduit.getDownloadPackages();
    
    if not os.path.exists(path):
        os.makedirs(path)

    for s in lorig:
        #if package is subpackage, this is his parent. We will use it for matching
        basePackageName = s.base_package_name
        basePackageEpoch = getEpoch(s.envra)[0]
        #aprox, noarch needs special handling
        basePackageAproxArch = getArch(s.envra)[1]
        basePackageENVRA=basePackageEpoch+":"+basePackageName+"-"+getEpoch(s.printVer())[1]+"."+basePackageAproxArch
        #name = s.ui_envra
        #include epoch always if enabled
        name = s.envra
        #noarch subpackages may unpack to more then one arches of parent-package
        names = []
        # epoch is included in regex anyway
        if pattern3.match(name):
            conduit.info(2, '***************************************************************');
            group = False
            conduit.info(3, ID_PRFIX+name + ' matching ' + resrc3)
            if name == basePackageENVRA:
                conduit.info(2, ID_PRFIX+name+" is main package itself");
                conduit.info(2, ID_PRFIX+"NOT grouping");
            else:
                conduit.info(2, ID_PRFIX+name+" is subpackage of " + getArch(basePackageENVRA)[0]);
                if groupSubpackages.match(basePackageENVRA):
                    conduit.info(2, ID_PRFIX+"Grouping! "+basePackageENVRA + ' matched ' + groupSubpackagesSrc);
                    group = True
                else:
                    conduit.info(2, ID_PRFIX+"NOT grouping "+basePackageENVRA + ' not matched ' + groupSubpackagesSrc);
            conduit.info(2, ID_PRFIX+"Proecessing:" + s.localPkg());
            if group and basePackageAproxArch != "noarch":
                name=basePackageENVRA
            if group and basePackageAproxArch == "noarch":
                if  isParentInTransactionArch(lorig, basePackageENVRA):
                    conduit.info(2, ID_PRFIX+"Although this package is subpackage and is noarch, its parent seems to be noarch too, continue in grouping");
                    name=basePackageENVRA
                else:
                    conduit.info(2, ID_PRFIX+"This package is subpackage and should be grupped. However is noarch and its parrent is not noarch. Trying to find arched parrent in transaction");
                    if  isParentInTransaction(lorig, basePackageENVRA):
                        found = getParentInTransaction(lorig, basePackageENVRA)
                        conduit.info(3, ID_PRFIX+"Found: "+str(found));
                        names = []
                        for n in found:
                            names.append(n.envra);
            if not names:
                names=[name]
            for lname in names:
                if trimEpoch:
                    lname = getEpoch(lname)[1]
                xcwd=path+"/"+lname
                if not os.path.exists(xcwd):
                    os.makedirs(xcwd)
                else:
                    if (group):
                        conduit.info(2, ID_PRFIX+'info(g) ' + lname + " already unpacked in " + path);
                    else:
                        conduit.info(2, ID_PRFIX+'WARNING ' + lname + " already unpacked in " + path);
                if debuglevel < 3:
                    FNULL = open(os.devnull, 'w')
                else:
                    FNULL=PIPE
                p1 = Popen(["rpm2cpio", s.localPkg()], stdout=PIPE, stderr=None, preexec_fn=None, close_fds=False, shell=False, cwd=xcwd)
                p2 = Popen(["cpio", "-idmv"], stdin=p1.stdout, stdout=FNULL, stderr=FNULL, preexec_fn=None, close_fds=False, shell=False, cwd=xcwd)
                p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
                output = p2.communicate()[0]
                conduit.info(2, ID_PRFIX+'Finished ' + s.envra + " to " + xcwd);
        else:
            conduit.info(2, ID_PRFIX+name + ' NOT matching ' + resrc3)
    if exitAfterUnpack:
        raise PluginYumExit(ID_PRFIX+'unpack plugin terminated YUM execution here. Done. Check ' + path + " for results.")

#yum.plugins.MainPluginConduit
def pretrans_hook(conduit):
    conduit.info(3, conduit);
    conduit.info(3, '* *7* *');
    # did nto find a way how to access downlaoded package here
    #raise PluginYumExit('addjava plugin terminated execution here')



if __name__ == '__main__':
    print  "Utility to test various regexes. Put yur regexes as arguments and then test matches"
    for idx, val in enumerate(sys.argv):
        if idx == 0:
            continue
        print  "  compiling " + val
        re.compile(val)
        print  "  done"
    print  "You cannow type  strings which will be tried if they match your regexes from commandline."
    print  "press ctrl+D or ctrl+C to end"
    while True:
        s = sys.stdin.readline()
        if not s:
            break
        s = s.rstrip()
        for idx, val in enumerate(sys.argv):
            if idx == 0:
                continue
            print  "  '"+s + "' matches '" + val + "' ?"
            if re.compile(val).match(s):
                print  "    True"
            else:
                print  "    False"
