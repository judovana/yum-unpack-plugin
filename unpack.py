# requires rpm2cpio cpio installed
from yum.plugins import PluginYumExit, TYPE_CORE, TYPE_INTERACTIVE
from subprocess import call, Popen, PIPE

import subprocess
import re
import os

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
pattern1 = None
pattern1_forceIn = None
pattern1_forceOut = None
pattern2 = None
pattern3 = None
path = '/opt/'
debuglevel=None
exitAfterUnpack = False
allpkgs = None

# all conduits described at http://yum.baseurl.org/api/yum/yum/plugins.html
# the hooks in http://yum.baseurl.org/wiki/WritingYumPlugins are not in any order, here they are ordered as yum is launching them


def init_hook(conduit):
    conduit.info(2, '***********************WARNING**************************');
    conduit.info(2, '                 Unpack plugin active')
    conduit.info(2, 'Selected packagesunpacked to /opt or where destination in unpack.conf points.')
    conduit.info(2, 'Special exclusion/forcing from that confing is cosidered.')
    conduit.info(2, 'See the README.md page of and unpack.conf and eventuelly also unpack.py for more info.')
    conduit.info(2, '********************************************************');
    global path
    global exitAfterUnpack
    global resrc1
    global resrc1_forceIn
    global resrc1_forceOut
    global resrc2
    global resrc3
    global pattern1
    global pattern1_forceIn
    global pattern1_forceOut
    global pattern2
    global pattern3
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
    pattern1 = re.compile(resrc1)
    pattern1_forceIn = re.compile(resrc1_forceIn)
    pattern1_forceOut = re.compile(resrc1_forceOut)
    pattern2 = re.compile(resrc2)
    pattern3 = re.compile(resrc3)
    conduit.info(2, ID_PRFIX+'unpack to ' + path);
    conduit.info(2, ID_PRFIX+'filter_pre1_repo ' + resrc1);
    conduit.info(2, ID_PRFIX+'filter_pre2_forceIn ' + resrc1_forceIn);
    conduit.info(2, ID_PRFIX+'filter_pre2_forceOut ' + resrc1_forceOut);
    conduit.info(2, ID_PRFIX+'filter_post ' + resrc2);
    conduit.info(2, ID_PRFIX+'filter_unpack ' + resrc3);
    conduit.info(2, ID_PRFIX+'quit_after_unpack ' + str(exitAfterUnpack));
    global debuglevel
    debuglevel = conduit.getConf().debuglevel;
    conduit.info(3, ID_PRFIX+'debuglevel ' + str(debuglevel));



#yum.plugins.PostRepoSetupPluginConduit
def postreposetup_hook(conduit):
    conduit.info(3, conduit);
    conduit.info(3, '* *1* *');
    #python dont like mepty methods, s having those numbering there

#yum.plugins.MainPluginConduit
def exclude_hook(conduit):
    conduit.info(3, conduit);
    conduit.info(3, '* *2 *');
    #same effect as in preresolve_hook removal, but much less information about packages    

#yum.plugins.DepsolvePluginConduit
def preresolve_hook(conduit):
    #packages filtered out here will not play any role in upcoming trasnaction. If important dep is removed, transaction fails.
    conduit.info(3, conduit);
    conduit.info(3, '* *3* *');
    global allpkgs
    allpkgs = conduit.getPackages()  #allpackages from all repos
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
        name = s.ui_envra
        if pattern3.match(name):
            conduit.info(3, ID_PRFIX+name + ' matching ' + resrc3)
            conduit.info(2, ID_PRFIX+"Proecessing:" + s.localPkg());
            xcwd=path+"/"+s.ui_envra
            if not os.path.exists(xcwd):
                os.makedirs(xcwd)
            else:
                conduit.info(2, ID_PRFIX+'WARNING ' + s.ui_envra + " already unpacked in " + path);
            if debuglevel < 3:
                FNULL = open(os.devnull, 'w')
            else:
                FNULL=PIPE
            p1 = Popen(["rpm2cpio", s.localPkg()], stdout=PIPE, stderr=None, preexec_fn=None, close_fds=False, shell=False, cwd=xcwd)
            p2 = Popen(["cpio", "-idmv"], stdin=p1.stdout, stdout=FNULL, stderr=FNULL, preexec_fn=None, close_fds=False, shell=False, cwd=xcwd)
            p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
            output = p2.communicate()[0]
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
