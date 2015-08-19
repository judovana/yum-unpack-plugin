# yum-unpack-plugin
Plugin for unpacking newest, but also older packages form repositories to custom dir for various case of comparing

plugin is depending on rpm2cpio and cpio commands available on PATH

The plugin works in two ways.
Defaults, as set in default unpack.conf and hardcoded in unpack.py:
    destination = /opt
    filter_pre1_repo = .*
    filter_pre2_forceIn = NothingCanMatchMe
    filter_pre2_forceOut = NothingCanMatchMe
    filter_post = .*
    filter_unpack = NothingCanMatchMe
    quit_after_unpack = False
In this mode, it do by default nothing. Recommended is to set destination to some value  usable by you.
You are supposed to put regular expression matching package you care bout (in my case .*java-1.*.0-openjdk.* as value of filter_unpack
Then, during any update(install/reinstall ...) of matching package the package (in addition to installation) will be also unpacked to destination. So I can investigate it.

Second supported mode is getting old versions of packages (if your repo is capable of, which it mostly is)
    destination = /home/jvanek/uncpio
    filter_pre1_repo = .*
    ; eg.: filter_pre2_forceIn = .*java-1.*.0-openjdk.*
    filter_pre2_forceIn = REGEX_PACKAGES_YOU_WONT
    filter_pre2_forceOut = .*
    filter_post = .*
    filter_unpack = .*
    quit_after_unpack = True
In this scenario, it removes complelty context of original transaction (filter_pre2_forceOut = .*)
and smuggle inside all PACKAGES_YOU_WONT (eg all javas) ever released for this product (filter_pre2_forceIn = .*java-1.*.0-openjdk.*)
If you are facing multilib issues (and you probably are unless you specify correct ENVRA into regex), use --setopt=protected_multilib=false
Then unpack them all to destination, so I can diff them.
See also quit_after_unpack = True. It is highly recommended to abort yum after unpacking, otherwise your system may be terribly damaged.

Note, this plugin have to had valid transaction at the input right now, otherwise it will notproceed.

filter_pre1_repo and filter_post are for special cases when other regexes fails to select only the packages you need or you need only some really strange case of install/unpack.

To make this plugin work, threat it as normal yum plugin, and place files like this:
/etc/yum/pluginconf.d/unpack.conf
/usr/lib/yum-plugins/unpack.py
Or any other pathe where your yum is searching for configs and for plugins. You mostly need to be root. Sorry.
